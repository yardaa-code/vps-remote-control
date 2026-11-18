# vps-remote-control

**English:** A Claude Code skill that walks a complete beginner through setting up their own small server
(VPS) running Claude Code 24/7 with **Remote Control**, so you can use Claude from the mobile app even
with your computer switched off. It covers SSH keys (Mac and Windows), basic hardening (key-only login,
firewall, fail2ban, no root), a service that restarts Claude after a crash, a nightly restart, and a daily
check that warns you before the Claude login expires (via ntfy, Gmail or Resend), and optionally
connects the server to GitHub. Claude does the technical work, you only order the server and log in.

**Note:** Claude talks to you in your language, the guide files themselves are in Czech. The recommended
provider is Czech (Forpsi Classic VPS Mini+, Ubuntu 24.04), but any VPS with Ubuntu 24.04 and root
access works.

Install: tell Claude Code *"Install the skill from https://github.com/yardaa-code/vps-remote-control"*,
or run `/plugin marketplace add yardaa-code/vps-remote-control` and
`/plugin install vps-remote-control@vps-remote-control`. MIT licence.

---

Skill pro Claude Code, který tě krok za krokem provede nastavením **vlastního malého serveru**, na kterém
nonstop běží Claude Code s **Remote Control**. Claude pak můžeš ovládat z aplikace v mobilu, i když máš
počítač vypnutý. Nemusíš umět programovat ani spravovat servery, technickou práci udělá Claude za tebe.

## Co budeš potřebovat
- počítač s **Claude Code** (Mac nebo Windows),
- placené předplatné Claude, ve kterém je Remote Control k dispozici (ověř si na claude.com),
- aplikaci **Claude** v mobilu,
- server (VPS), doporučený **Forpsi Classic VPS Mini+ s Ubuntu 24.04** za cca 85 Kč měsíčně
  (cena z listopadu 2026),
- zhruba hodinu času.

## Instalace
**Nejjednodušší:** otevři Claude Code a napiš mu:

> Nainstaluj si skill z https://github.com/yardaa-code/vps-remote-control (složku `skills/vps-remote-control`
> zkopíruj do `~/.claude/skills/`).

**Nebo jako plugin** (jde pak snadno aktualizovat). V Claude Code napiš tyhle dva příkazy:

```
/plugin marketplace add yardaa-code/vps-remote-control
/plugin install vps-remote-control@vps-remote-control
```

Aktualizace pluginu: `/plugin marketplace update vps-remote-control`.

Po instalaci restartuj Claude Code a napiš třeba **„chci Claude na serveru, ať ho můžu ovládat z mobilu“**.

## Co se nastaví
- **Zabezpečení:** přihlášení na server jen klíčem (heslo vypnuté), firewall, blokování útočníků
  (fail2ban), Claude běží pod vlastním účtem bez práv správce.
- **Claude Code s Remote Control** ve službě, která ho po pádu do 20 s znovu spustí, se stropem paměti.
- **Noční restart** ve 4:00 (paměť Claude s časem roste).
- **Hlídač přihlášení:** přihlášení Claude vyprší zhruba po 4 týdnech a Remote Control pak potichu
  přestane fungovat. Hlídač tě včas upozorní přes **ntfy** (notifikace do mobilu), **Gmail**, nebo
  **Resend**, podle tvé volby.
- **GitHub (volitelně):** Claude na serveru pak z mobilu stáhne tvůj projekt, upraví ho a otevře pull
  request. Do commitů se zapíše anonymní adresa od GitHubu, ne tvůj e-mail.

## Dobré vědět
- Server je **jen pro Claude**. Claude na něm smí spouštět příkazy, nedávej na něj nic důležitého.
- Jednou za ~4 týdny je potřeba Claude na serveru znovu přihlásit. Stačí napsat Claude Code v počítači
  „přihlas znovu Claude na serveru“.
- Hesla ani klíče skill nikam neposílá. Heslo roota a hesla pro upozornění zadáváš jen ty ve svém
  terminálu.

## Pro vývojáře
- `skills/vps-remote-control/SKILL.md`: průvodce pro Claude, `reference/`: podrobné návody,
  `scripts/`: co se nahraje na server.
- Testy hlídače: `python3 -m unittest discover testy`.
- Verze: při změně skriptů zvyš číslo v `skills/vps-remote-control/scripts/VERZE` i v
  `.claude-plugin/plugin.json` (stejné). Skill podle ní nabídne uživatelům aktualizaci serveru.

Licence MIT.
