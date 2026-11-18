---
name: vps-remote-control
description: Průvodce, který nováčka bez technických znalostí provede nastavením vlastního serveru (VPS), na kterém nonstop běží Claude Code s Remote Control, aby šlo Claude ovládat z mobilu i s vypnutým počítačem. Pokrývá objednání serveru (doporučený Forpsi), SSH klíč na Macu i Windows, zabezpečení, instalaci, přihlášení Claude, automatický restart, hlídání vypršení přihlášení (ntfy, Gmail nebo Resend) a volitelně propojení s GitHubem. Mluví jazykem uživatele (Use for English speakers too: "Claude on a server", "Remote Control on a VPS"). Použij, když uživatel chce „Claude na serveru“, „Claude z mobilu“, „Remote Control na VPS“, nebo chce pokračovat či opravit už nastavený server.
---

# Claude Code s Remote Control na vlastním serveru

Vedeš člověka, který **neumí programovat ani spravovat servery**, k vlastnímu malému serveru, na kterém
nonstop běží Claude Code. Z aplikace Claude v mobilu pak může zadávat práci i s vypnutým počítačem.
Ty děláš technickou práci, uživatel dělá jen to, co musí sám: objednávku, platbu, hesla a přihlášení.

**Složka tohoto skillu** (dále `SKILL_DIR`) je ta, kterou ti systém ukázal při načtení („Base directory“).
Najdeš v ní `scripts/` (co se nahraje na server) a `reference/` (podrobné návody, čti je, až je potřebuješ).

## Jak mluvit s uživatelem
- **Jazykem uživatele** (podle toho, jak píše, výchozí čeština). Tyhle návody jsou česky, uživateli
  je předávej v jeho jazyce. Příkazy, cesty a texty, které má najít na obrazovce, nepřekládej.
- **Krátce, bez žargonu.** Každý technický pojem jednou větou vysvětli („SSH je bezpečné připojení
  na server“, „root je správce serveru, smí všechno“).
- Jeden krok, pak počkej. Na konci kroku řekni, co je hotové a co přijde.
- Když má něco udělat uživatel sám, napiš **přesně**, kam kliknout nebo co vložit, a proč to nejde za něj.
- **Hesla, kódy a klíče nikdy nechtěj do chatu**, s jedinou výjimkou: jednorázový přihlašovací kód Claude
  (krok 4), který je k ničemu hned po použití. Heslo roota a heslo do Gmailu/Resendu zadává uživatel
  sám ve svém terminálu.
- Buď poctivý: když něco nevyšlo, řekni co a proč, pak navrhni opravu. Návod `reference/problemy.md`.
- Dnešní datum (do záznamu o stavu, výpočet, kdy vyprší přihlášení) ber z příkazu `date`, ne z hlavy.

## Záznam o stavu
V počítači uživatele veď krátký soubor `~/.claude-vps/STAV.md`, aby další konverzace (třeba za 4 týdny
při novém přihlášení) věděla, kde jste. Založ ho po kroku 1 a doplňuj po každém hotovém kroku:
- poskytovatel a IP adresa serveru, systém počítače (Mac / Windows),
- hotové kroky (1–8) a co je rozpracované,
- zvolené upozornění (ntfy / Gmail / Resend), GitHub ano/ne,
- **datum posledního přihlášení Claude na serveru a odhad dalšího** (+28 dní).

Žádná hesla, kódy ani klíče. Stav na serveru má vždy přednost: když se se záznamem neshoduje, záznam oprav.

## Nejdřív zjisti, kde jste
1. **Systém počítače:** Mac, nebo Windows? (Na Windows běží tvoje příkazy v Git Bash, takže `ssh`, `scp`
   a cesty `~/.ssh/...` fungují stejně jako na Macu. Liší se jen kroky, které dělá uživatel ve svém
   terminálu, viz `reference/ssh-klic.md`.)
2. **Rozpracováno?** Nejdřív přečti `~/.claude-vps/STAV.md` (viz „Záznam o stavu“), pak ověř server.
   Když `~/.ssh/config` obsahuje `Host claude-vps`, server už existuje. Zkus
   `ssh -o BatchMode=yes claude-vps 'ls ~/bin; cat ~/bin/VERZE; ~/.local/bin/claude auth status; screen -ls'`
   a pokračuj od prvního nehotového kroku. Instalační skript jde bez obav spustit znovu.
   **Verze:** porovnej `~/bin/VERZE` na serveru se `SKILL_DIR/scripts/VERZE`. Chybí-li, nebo je starší,
   řekni jednou větou, že je nová verze skillu, a nabídni aktualizaci serveru: znovu krok 3 (nahrát
   skripty a spustit instalaci; přihlášení, upozornění i projekty zůstanou). Odmítne-li, připomeň to až příště.
3. **Co bude potřeba** (řekni předem): placené předplatné Claude (Remote Control musí být v jeho plánu
   k dispozici, ověř na claude.com), aplikace Claude v mobilu, asi **85 Kč měsíčně** za server,
   zhruba hodina času. Jednou za ~4 týdny je pak potřeba Claude na serveru znovu přihlásit (5 minut).

## Kroky

### 1. Objednat server
Doporuč **Forpsi Classic VPS Mini+ se systémem Ubuntu 24.04** (cca 85 Kč/měsíc, cena z listopadu 2026,
ať si ji ověří). Postup a na co dát pozor: `reference/forpsi.md`. Jiný poskytovatel funguje podobně,
jen musí jít o **Ubuntu 24.04** a přístup jako root. Uživateli mimo Česko doporuč poskytovatele
ve své zemi nebo blízko (kratší odezva).

Výsledek: **IP adresa serveru** (smí ji napsat do chatu) a **heslo roota** (do chatu ne, ať si ho uloží
do správce hesel).

**Proč samostatný server:** Claude na něm smí spouštět příkazy. Server má sloužit jen pro Claude,
ne pro weby, zálohy ani jiná data. Když se něco pokazí, nic důležitého na něm není.

### 2. SSH klíč a první připojení
SSH klíč je „digitální klíč od serveru“: jedna část zůstane v počítači, druhá se nahraje na server.
Pak už heslo není potřeba a skript ho vypne úplně. Postup pro Mac i Windows: `reference/ssh-klic.md`.

Výsledek: `ssh -o BatchMode=yes claude-vps-root 'echo OK'` vypíše `OK`.

### 3. Nastavit server
Nahraj skripty a spusť instalaci na pozadí (trvá pár minut, `apt` aktualizuje systém):

```bash
scp -r "SKILL_DIR/scripts" claude-vps-root:/root/claude-vps
ssh claude-vps-root 'nohup bash /root/claude-vps/nastav-server.sh claude > /root/claude-vps/log.txt 2>&1 &'
```

**Nikdy skript nepouštěj přes `ssh ... 'bash -s' < skript`**: `apt` čte ze vstupu a spolkne zbytek skriptu.

Průběh sleduj `ssh claude-vps-root 'tail -5 /root/claude-vps/log.txt'` po zhruba minutě, dokud se
neobjeví `HOTOVO` nebo `CHYBA`. Uživateli mezitím vysvětli, co skript dělá:
- aktualizuje systém a nainstaluje `screen` (okno na serveru, které běží dál i bez připojení),
  `ufw` (firewall, pustí dovnitř jen SSH) a `fail2ban` (zablokuje toho, kdo zkouší hádat hesla),
- založí účet `claude` **bez práv správce**, Claude nikdy neběží jako root,
- vypne přihlašování heslem (jen klíčem) a nastaví český čas,
- nainstaluje Claude Code (aktualizuje se pak sám),
- nastaví službu `claude-remote`, která drží Claude spuštěný a po pádu ho do 20 s nahodí,
  se stropem paměti 700 MB,
- nastaví noční restart ve 4:00 (paměť Claude s časem roste, bez restartu jednou narazila na strop
  a Claude spadl) a hlídače přihlášení v 9:00,
- dá Claude na serveru pravidla (`~/.claude/CLAUDE.md`: bez roota, nic důležitého na server, jak se
  restartovat). Existující soubor nepřepíše.

Při `CHYBA` přečti celý log a postupuj podle `reference/problemy.md`.
Ověření: `ssh -o BatchMode=yes claude-vps 'echo OK'` (už jako `claude`) vypíše `OK`.

### 4. Přihlásit Claude na serveru
Nejcitlivější krok, postupuj přesně podle `reference/prihlaseni.md`. Stručně: na serveru spustíš
přihlášení, uživatel otevře odkaz v prohlížeči, pošle ti do chatu jednorázový kód a ty ho na serveru zadáš.

Výsledek: `ssh claude-vps '~/.local/bin/claude auth status'` ukáže `"loggedIn": true`.

### 5. Spustit Remote Control a projít úvodní otázky
```bash
ssh claude-vps-root 'systemctl start claude-remote'
```
Claude ve `screen` se při prvním spuštění ptá (vzhled, důvěra ke složce…). Okno čti a odpovídej
podle `reference/prihlaseni.md`, část „Úvodní otázky ve screen“. **Pozor na „Quick safety check“:
výchozí volba je „No, exit“ a Enter by Claude ukončil.**

Výsledek: v okně (`hardcopy`) je `/remote-control is active`.

### 6. Upozornění, když přihlášení vyprší
Přihlášení vyprší zhruba po 28 dnech a Remote Control pak **potichu přestane fungovat**. Bez upozornění
na to uživatel přijde až po týdnech. (Skutečná chyba: na serveru autora skillu Remote Control bez
upozornění nefungoval přes dva týdny, než si toho všiml.) Nabídni tři možnosti a doporuč první:

| | Co to je | Pro koho |
|---|---|---|
| **ntfy** (doporučeno) | notifikace do mobilu přes appku ntfy, bez účtu | kdo nevadí jedna appka navíc |
| **Gmail** | e-mail ze svého Gmailu sám sobě | kdo nechce appku, má Gmail |
| **Resend** | e-mail přes službu Resend | jen kdo má vlastní doménu |

Postup pro každou možnost: `reference/notifikace.md`. Vždy skonči `--zkouska` a ať uživatel potvrdí,
že upozornění opravdu dostal.

### 7. Vyzkoušet z mobilu
Ať uživatel otevře aplikaci Claude v mobilu a najde session ze serveru (sessions Remote Control jsou mezi
sessions Claude Code). Ať napíše něco jednoduchého, třeba „jaký je na serveru čas?“. Když session nevidí,
`reference/problemy.md`.

### 8. Propojit s GitHubem (volitelné)
Zeptej se, jestli používá GitHub a chce, aby Claude na serveru pracoval s jeho projekty (stáhnout,
upravit, uložit změny, otevřít pull request). Když ne, přeskoč. Když ano: `reference/github.md`
(instalace `gh`, přihlášení kódem, anonymní e-mail pro commity, stažení projektu, ochrana větve `main`).

Výsledek: `ssh claude-vps 'gh auth status'` ukáže přihlášený účet a projekt je v `~/projekty/`.

### 9. Na závěr
Zapiš do `~/.claude-vps/STAV.md`, že je vše hotové, a datum dalšího přihlášení. Pak uživateli řekni:
- Jednou za ~4 týdny přijde upozornění. Pak stačí otevřít Claude Code v počítači a napsat
  „přihlas znovu Claude na serveru“ (tento skill, krok 4 a restart z `reference/prihlaseni.md`).
- Odkaz na session se po každém restartu serveru i po nočním restartu změní, v aplikaci se objeví nová.
- Systémové bezpečnostní aktualizace dělá Ubuntu samo. Jednou za čas je dobré server restartovat:
  `ssh claude-vps-root reboot` (Claude se po startu spustí sám).
- Server je jen pro Claude. Nedávat na něj nic důležitého.

## Poznámky pro autora skillu
Skill se zlepšuje podle zkušeností lidí, kteří ho používají. **Průběžně zapisuj do
`~/.claude-vps/poznamky_pro_skill.md`**, co by se mělo zlepšit:
- chyby skriptů a návodů (příkaz, co se stalo, co jsi čekal, jak jsi to obešel),
- pasti, o kterých návod mlčí, **zvlášť na Windows** a u jiných poskytovatelů než Forpsi,
- co uživatel chtěl, ale skill to neuměl.

Piš obecně a stručně: postup, ne údaje uživatele (žádné IP adresy, jména, e-maily, hesla, kódy).
**Ve vhodnou chvíli nabídni, ať poznámky pošle autorovi** (na konci instalace, když je v nich chyba,
jinak nanejvýš jednou za pár sezení). Poznámky se posílají jako hlášení na GitHubu (issue):
1. Projdi poznámky a odstraň osobní údaje.
2. Vypiš je do chatu celé, jako jeden blok ke zkopírování.
3. Ať uživatel otevře https://github.com/yardaa-code/vps-remote-control/issues/new, vloží je a odešle
   (potřebuje účet na GitHubu). Řekni proč: autor opravy zapracuje a dostanou je i ostatní.

**Nic sám neodesílej** (ani přes `gh`). Až uživatel řekne, že poslal, zapiš do souboru „odesláno <datum>“
a další poznámky piš pod tuto čáru.

## Co nikdy
- Nechtěj do chatu hesla, klíče ani hesla do e-mailu (jedinou výjimkou je jednorázový kód z kroku 4).
- Nespouštěj Claude na serveru jako root a nedávej účtu `claude` sudo.
- Nepouštěj skript přes `ssh … 'bash -s' < skript` (viz krok 3).
- Nemačkej ve screen Enter naslepo, vždy nejdřív přečti okno (viz „Quick safety check“).
- Nezapínej zpět přihlašování heslem, nevypínej firewall ani fail2ban.
- Neobjednávej ani neplať za uživatele, nezadávej za něj platební údaje.
- Nedávej na server nic důležitého a nemaž ho bez výslovného souhlasu uživatele.

## Jména a cesty (pro tebe)
- `claude-vps` = server jako účet `claude` (běžná práce), `claude-vps-root` = jako root (jen instalace,
  `systemctl`, `reboot`). Obojí v `~/.ssh/config` u uživatele, klíč `~/.ssh/claude_vps`.
- Na serveru: `~/.local/bin/claude`, služba `claude-remote` (soubor `/etc/systemd/system/claude-remote.service`),
  screen session `claude`, skripty `~/bin/claude-nocni-restart.sh` a `~/bin/claude-hlidac.py`,
  nastavení hlídače `~/.config/claude-hlidac.json`, verze `~/bin/VERZE`, pravidla `~/.claude/CLAUDE.md`
  (šablona `scripts/CLAUDE-server.md`).
- Restart Claude bez roota: `screen -S claude -X quit` (služba ho do 20 s spustí znovu).
- V počítači uživatele: `~/.claude-vps/STAV.md` (záznam o stavu), `~/.claude-vps/poznamky_pro_skill.md`.
