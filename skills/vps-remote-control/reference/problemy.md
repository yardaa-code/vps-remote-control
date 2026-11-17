# Když něco nefunguje

Nejdřív zjisti stav (nic nemění):
```bash
ssh -o BatchMode=yes claude-vps 'uptime; screen -ls; ~/.local/bin/claude auth status; screen -S claude -X hardcopy /tmp/c.txt && tail -15 /tmp/c.txt'
```

## Z mobilu session nevidím / nereaguje
- **Odhlášený Claude** (`"loggedIn": false`, v okně `Not logged in`): proces dál běží, ale nefunguje.
  Restart nepomůže, je potřeba znovu přihlásit: `prihlaseni.md`.
- **Claude čeká na otázku** v okně (typicky „Quick safety check“): projdi podle `prihlaseni.md`,
  část „Úvodní otázky ve screen“.
- **Žádné screen okno `claude`:** zjisti stav služby jako root:
  `ssh claude-vps-root 'systemctl status claude-remote --no-pager | head -15'`.
  `failed` → `systemctl restart claude-remote`. `inactive` → `systemctl start claude-remote`.
- **Po restartu má session nový odkaz.** V aplikaci hledat novou session, stará zůstane mrtvá.

## Claude padá nebo je pomalý
Služba má strop paměti 700 MB. Když ho Claude překročí, ukončí se a služba ho do 20 s spustí znovu.
Proto noční restart ve 4:00. Příčina posledního pádu: `systemctl status claude-remote` (řádek `Result:`).

## SSH nejde (`Connection refused`, ping přitom jde)
Stává se po aktualizaci Ubuntu: SSH služba se nespustí znovu. Uživatel otevře **konzoli u poskytovatele**
(Forpsi: administrace serveru → konzole), přihlásí se `root` a heslem roota a napíše:
```
systemctl restart ssh
```

## `Permission denied (publickey)`
- Klíč chybí v počítači nebo se změnil `~/.ssh/config`: zkontroluj `~/.ssh/claude_vps` a sekce `Host claude-vps`.
- Uživatel se stal obětí fail2ban (5 špatných pokusů za hodinu = hodina blokace). Počkat hodinu.

## Instalační skript skončil `CHYBA`
Přečti celý `/root/claude-vps/log.txt`. Skript jde po opravě příčiny spustit znovu, hotové věci přeskočí.
- `Could not get lock`: běží jiná instalace (automatické aktualizace), za pár minut spustit znovu.
- `root nemá SSH klíč`: nejdřív `ssh-klic.md`.
- `přihlášení heslem pořád zapnuté`: v `/etc/ssh/sshd_config.d/` je jiný soubor, který heslo zapíná
  a je abecedně dřív než `01-claude-vps.conf`. Ukaž ho uživateli a po souhlasu ho uprav.
- Chyba při instalaci Claude Code: zkus znovu, jde-li o síť. Jinak `su - claude -c 'curl -fsSL https://claude.ai/install.sh | bash'` ručně a čti výpis.

## Zaseknutý Claude
Restart bez roota: `ssh claude-vps 'screen -S claude -X quit'`. Služba ho do 20 s spustí znovu, pak
zkontroluj okno.
