# Propojení s GitHubem (volitelné)

Díky tomu Claude na serveru umí z mobilu stáhnout projekt, upravit ho, uložit změny (commit) a otevřít
pull request. Kdo GitHub nepoužívá, tenhle krok přeskočí.

**Nejdřív řekni uživateli, co to znamená:** přihlášený Claude na serveru smí měnit **všechny** jeho
repozitáře na GitHubu. Proto na konci doporučíš ochranu hlavní větve (bod 5).

## 1. Nainstalovat `gh` (pomocník pro GitHub v terminálu)
Z oficiálních balíčků Ubuntu, jako root:
```bash
ssh claude-vps-root 'DEBIAN_FRONTEND=noninteractive apt-get -y -q -o DPkg::Lock::Timeout=600 install gh git < /dev/null && gh --version'
```

## 2. Přihlásit (jako `claude`)
Opačně než u Claude: **kód ukážeš ty uživateli** a on ho zadá na GitHubu. Do chatu nic tajného nejde.

```bash
ssh claude-vps 'rm -f /tmp/gh.log; screen -L -Logfile /tmp/gh.log -dmS gh gh auth login -h github.com -p https -w; sleep 4; screen -S gh -X hardcopy /tmp/gh.txt; cat /tmp/gh.txt'
```

1. V okně je `First copy your one-time code: XXXX-XXXX`. Pošli uživateli kód a odkaz
   **https://github.com/login/device**: „Otevři odkaz, přihlas se na GitHub, zadej kód a potvrď (Authorize).“
2. Okno čeká na Enter („Press Enter to open…“). Pošli ho: `ssh claude-vps "screen -S gh -X stuff $'\r'"`.
   Hlášky `Failed to copy one-time code to clipboard` a `Failed opening a web browser` jsou neškodné:
   server nemá schránku ani prohlížeč, `gh` dál čeká, až uživatel potvrdí na GitHubu.
3. Okno průběžně čti (`hardcopy` jako výše). Když se zeptá *Authenticate Git with your GitHub
   credentials?*, odpověz `Y` a Enter.
4. Až uživatel potvrdí, ověř a ukliď:
   ```bash
   ssh claude-vps 'gh auth status; gh auth setup-git; screen -S gh -X quit 2>/dev/null; rm -f /tmp/gh.log /tmp/gh.txt'
   ```
   Čekáš `Logged in to github.com account <jméno>`.

## 3. Jméno a e-mail pro commity
Každý commit nese jméno a e-mail autora a ve veřejném repozitáři je vidí kdokoli. Proto **anonymní
adresa od GitHubu** místo soukromého e-mailu (GitHub ji stejně přiřadí k účtu). Jméno se zeptej
uživatele (skutečné jméno, nebo jen přezdívka z GitHubu).
```bash
ssh claude-vps 'git config --global user.name "<JMÉNO>"; git config --global user.email "$(gh api user --jq "\"\(.id)+\(.login)@users.noreply.github.com\"")"; git config --global init.defaultBranch main; git config --global --list'
```

## 4. Stáhnout projekt
Zeptej se, na kterém repozitáři chce z mobilu pracovat (`gh repo list` ukáže jeho repozitáře):
```bash
ssh claude-vps 'mkdir -p ~/projekty && cd ~/projekty && gh repo clone <vlastník>/<repozitář>'
```
Řekni mu, že v mobilu pak stačí napsat třeba „v projektu <název> oprav …“, Claude na serveru přejde do
`~/projekty/<název>`.

## 5. Ochrana hlavní větve (doporučeno)
Aby Claude nemohl nic poslat rovnou do `main`, jen přes pull request, který uživatel schválí. Uživatel
na GitHubu otevře repozitář → **Settings** → **Rules** → **Rulesets** → **New branch ruleset**: název
„main“, Enforcement **Active**, Target branches **Include default branch**, zaškrtnout
**Require a pull request before merging** a **Block force pushes**, uložit.

U veřejných repozitářů to funguje zdarma. U soukromých repozitářů na bezplatném účtu GitHub tuhle
volbu nemusí nabízet. Pak uživateli řekni, že ochrana chybí a Claude musí sám dodržovat „jen přes
pull request“.

## Odpojení
Kdyby chtěl Claude na serveru přístup vzít: na GitHubu **Settings → Applications → Authorized OAuth
Apps → GitHub CLI → Revoke**. Na serveru pak `ssh claude-vps 'gh auth logout -h github.com'`.
