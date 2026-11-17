# Upozornění na vypršení přihlášení

Hlídač `~/bin/claude-hlidac.py` běží každý den v 9:00. Když je Claude odhlášený nebo přihlášení vyprší
do 5 dní, pošle upozornění. Nastavení bez hesel je v `~/.config/claude-hlidac.json` (zapisuješ ty),
heslo nebo klíč zvlášť v `~/.config/claude-hlidac-tajne` (zadává uživatel sám).

`nazev_serveru` se objeví v titulku upozornění, dej třeba `"Forpsi"`.

Nastavení zapiš takhle (příklad pro ntfy):
```bash
ssh claude-vps 'mkdir -p ~/.config && cat > ~/.config/claude-hlidac.json' <<'EOF'
{"zpusob": "ntfy", "ntfy_tema": "claude-7f3a9c2e1b4d", "nazev_serveru": "Forpsi"}
EOF
```

## ntfy (doporučeno)
Upozornění přijde jako notifikace do mobilu. Bez účtu a bez hesla.

1. Vymysli náhodné téma: `python3 -c "import secrets; print('claude-' + secrets.token_hex(6))"`.
   Téma funguje jako adresa: kdo ho zná, upozornění vidí. Proto náhodné. Upozornění neobsahují nic
   tajného, jen „je potřeba se přihlásit“.
2. Uživatel si do mobilu nainstaluje aplikaci **ntfy** (App Store / Google Play), klepne na **+**
   a vloží téma (server nechá výchozí `ntfy.sh`).
3. Zapiš nastavení: `{"zpusob": "ntfy", "ntfy_tema": "<téma>", "nazev_serveru": "Forpsi"}`.

## Gmail
E-mail ze svého Gmailu sám sobě. Potřebuje **heslo pro aplikace** (zvláštní heslo jen pro tenhle účel,
ne heslo do Gmailu).

1. Uživatel musí mít v účtu Google zapnuté **dvoufázové ověření** (bez něj hesla pro aplikace nejdou).
2. Na stránce **myaccount.google.com/apppasswords** vytvoří heslo, pojmenuje ho třeba „Claude server“.
   Google ukáže 16 znaků.
3. Zapiš nastavení: `{"zpusob": "gmail", "gmail_adresa": "<jeho adresa>", "nazev_serveru": "Forpsi"}`
   (jiný příjemce než odesílatel: přidej `"prijemce": "<adresa>"`).
4. Heslo uloží uživatel sám **ve svém terminálu** (Mac: Terminál, Windows: PowerShell), do chatu ne:
   ```
   ssh -t claude-vps "~/bin/claude-hlidac.py --uloz-heslo"
   ```
   Vloží heslo pro aplikace, Enter. Při psaní není nic vidět, to je v pořádku.

## Resend
Pro toho, kdo má **vlastní doménu** a účet na resend.com. E-mail chodí z adresy na jeho doméně.

1. V Resendu musí být doména ověřená (Domains).
2. Uživatel vytvoří API klíč s oprávněním **Sending access** jen pro tu doménu (API Keys), pojmenuje
   ho třeba „claude-server“. Ne klíč s plným přístupem.
3. Zapiš nastavení:
   `{"zpusob": "resend", "odesilatel": "Claude server <noreply@jeho-domena.cz>", "prijemce": "<adresa>", "nazev_serveru": "Forpsi"}`
4. Klíč uloží uživatel sám stejným příkazem jako u Gmailu (`--uloz-heslo`).

## Vyzkoušet (vždy)
```bash
ssh claude-vps '~/bin/claude-hlidac.py --nanecisto; ~/bin/claude-hlidac.py --zkouska'
```
`--nanecisto` vypíše, do kdy přihlášení platí. `--zkouska` pošle zkušební upozornění hned. Ať uživatel
potvrdí, že přišlo (u e-mailu zkontrolovat i spam). Chyby:
- `HTTP Error 403` u Resendu: klíč nemá právo na tu doménu, nebo doména není ověřená.
- `SMTPAuthenticationError` u Gmailu: špatné heslo pro aplikace, uložit znovu.
- `FileNotFoundError ... claude-hlidac-tajne`: heslo ještě není uložené.
