#!/bin/bash
# Nastaví čerstvý server s Ubuntu 24.04 pro Claude Code s Remote Control
# (ovládání Claude z mobilu). Spouští se jako root:
#
#   bash /root/claude-vps/nastav-server.sh [uzivatel]
#
# Jde spustit opakovaně, hotové věci jen znovu potvrdí.
# Na konci vypíše HOTOVO, při chybě řádek začínající CHYBA.
set -euo pipefail
trap 'echo "CHYBA: skript skončil na řádku $LINENO"' ERR

U="${1:-claude}"
D="$(cd "$(dirname "$0")" && pwd)"
krok() { echo; echo "== $*"; }

[ "$(id -u)" = 0 ] || { echo "CHYBA: spusť jako root"; exit 1; }
. /etc/os-release
[ "$ID" = ubuntu ] || { echo "CHYBA: čekám Ubuntu, tady je $PRETTY_NAME"; exit 1; }
[ "$VERSION_ID" = 24.04 ] || echo "POZOR: vyzkoušeno na Ubuntu 24.04, tady je $VERSION_ID"
# Bez klíče u roota by vypnutí hesel zamklo server.
[ -s /root/.ssh/authorized_keys ] || { echo "CHYBA: root nemá SSH klíč (/root/.ssh/authorized_keys), nejdřív nahraj klíč"; exit 1; }

krok "Aktualizace systému a balíčky (pár minut)"
export DEBIAN_FRONTEND=noninteractive
# Na čerstvém serveru často běží automatické aktualizace a drží zámek, počkáme na ně.
# < /dev/null: apt jinak čte ze vstupu a může spolknout zbytek skriptu.
APT=(apt-get -y -q -o DPkg::Lock::Timeout=600 -o Dpkg::Options::=--force-confdef -o Dpkg::Options::=--force-confold)
"${APT[@]}" update < /dev/null
"${APT[@]}" upgrade < /dev/null
"${APT[@]}" install screen fail2ban ufw curl python3 < /dev/null
timedatectl set-timezone Europe/Prague

krok "Účet $U (bez sudo, Claude neběží pod rootem)"
id "$U" >/dev/null 2>&1 || useradd -m -s /bin/bash "$U"
install -d -m 700 -o "$U" -g "$U" "/home/$U/.ssh"
install -m 600 -o "$U" -g "$U" /root/.ssh/authorized_keys "/home/$U/.ssh/authorized_keys"

krok "Firewall (povolené jen SSH)"
ufw allow OpenSSH >/dev/null
ufw --force enable

krok "fail2ban (blokuje toho, kdo zkouší hádat hesla)"
cat > /etc/fail2ban/jail.d/claude-vps.local <<'EOF'
[sshd]
enabled = true
maxretry = 5
findtime = 3600
bantime = 3600
EOF
systemctl enable fail2ban >/dev/null 2>&1
systemctl restart fail2ban

krok "SSH jen klíčem, heslem ne"
# Název 01-…: SSH bere první nalezenou hodnotu a soubory čte podle abecedy,
# takže by jinak mohl vyhrát třeba 50-cloud-init.conf s povoleným heslem.
cat > /etc/ssh/sshd_config.d/01-claude-vps.conf <<'EOF'
PasswordAuthentication no
KbdInteractiveAuthentication no
PermitRootLogin prohibit-password
EOF
sshd -t
systemctl reload ssh
sshd -T | grep -qx 'passwordauthentication no' || { echo "CHYBA: přihlášení heslem pořád zapnuté, zkontroluj /etc/ssh/sshd_config.d/"; exit 1; }

krok "Claude Code (oficiální instalátor, dál se aktualizuje sám)"
if [ -x "/home/$U/.local/bin/claude" ]; then
  echo "už je nainstalovaný"
else
  su - "$U" -c 'curl -fsSL https://claude.ai/install.sh | bash' < /dev/null
fi
[ -x "/home/$U/.local/bin/claude" ] || { echo "CHYBA: Claude Code se nenainstaloval"; exit 1; }

krok "Pomocné skripty a cron (4:00 restart, 9:00 hlídač přihlášení)"
install -d -o "$U" -g "$U" "/home/$U/bin"
install -m 755 -o "$U" -g "$U" "$D/claude-nocni-restart.sh" "$D/claude-hlidac.py" "/home/$U/bin/"
# Verze skillu, ze které je server nastavený (skill ji porovná a nabídne aktualizaci).
install -m 644 -o "$U" -g "$U" "$D/VERZE" "/home/$U/bin/VERZE"
crontab -u "$U" - <<EOF
# Noční restart Claude (čistí paměť), služba ho do 20 s spustí znovu
0 4 * * * /home/$U/bin/claude-nocni-restart.sh
# Denní kontrola přihlášení Claude, při problému pošle upozornění
0 9 * * * /home/$U/bin/claude-hlidac.py
EOF

krok "Pravidla pro Claude na serveru (~/.claude/CLAUDE.md)"
install -d -o "$U" -g "$U" "/home/$U/.claude"
# Jen když chybí, ať se nepřepíšou vlastní úpravy uživatele.
if [ -e "/home/$U/.claude/CLAUDE.md" ]; then
  echo "už existuje, nechávám beze změny"
else
  install -m 644 -o "$U" -g "$U" "$D/CLAUDE-server.md" "/home/$U/.claude/CLAUDE.md"
fi

krok "Služba claude-remote (spustí Claude ve screen, po pádu ho nahodí)"
cat > /etc/systemd/system/claude-remote.service <<EOF
[Unit]
Description=Claude Code Remote Control (screen session "claude")
After=network-online.target
Wants=network-online.target
StartLimitIntervalSec=0

[Service]
Type=simple
User=$U
WorkingDirectory=/home/$U
Environment=PATH=/home/$U/.local/bin:/usr/local/bin:/usr/bin:/bin
ExecStart=/usr/bin/screen -DmS claude /home/$U/.local/bin/claude --remote-control
ExecStop=-/usr/bin/screen -S claude -X quit
Restart=always
RestartSec=20
MemoryMax=700M

[Install]
WantedBy=multi-user.target
EOF
systemctl daemon-reload
# Jen zapnout po startu serveru. Poprvé se spustí až po přihlášení Claude.
systemctl enable claude-remote >/dev/null 2>&1

echo
echo "HOTOVO. Další krok: přihlásit Claude jako $U (claude auth login) a pak: systemctl start claude-remote"
