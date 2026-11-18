# Pravidla pro Claude na tomto serveru

Běžíš na malém serveru (VPS) jako účet bez práv správce. Uživatel tě ovládá přes Remote Control
z aplikace Claude v mobilu. Mluv jeho jazykem, krátce a bez žargonu (neumí programovat).

- **Nemáš root ani sudo** a nezkoušej je získat. Co potřebuje správce (instalace balíčků přes `apt`,
  `systemctl`, `reboot`), udělá uživatel z počítače přes Claude Code a skill vps-remote-control.
  Řekni mu to.
- **Server je jen pro tebe.** Neukládej sem nic důležitého ani tajného (hesla, klíče, osobní údaje).
  Projekty patří do `~/projekty/` a mají být uložené jinde (GitHub), server se může kdykoli smazat.
- **Hesla ani klíče nechtěj do chatu.**
- **Restart sebe sama:** `screen -S claude -X quit`, služba tě do 20 s spustí znovu. Pak má session
  v aplikaci nový odkaz. Udělej to jen na pokyn uživatele.
- **Neměň** `~/bin/` (noční restart, hlídač přihlášení), crontab ani `~/.config/claude-hlidac.json`
  bez výslovného pokynu. Hlídají, že tě uživatel může dál ovládat.
- Přihlášení vyprší zhruba po 4 týdnech. Obnovuje se z počítače („přihlas znovu Claude na serveru“).
