#!/usr/bin/env python3
"""Hlídač přihlášení Claude na tomto serveru.

Přihlášení Claude vyprší zhruba po 4 týdnech a Remote Control pak potichu
přestane fungovat. Hlídač jednou denně (z cronu) zjistí `claude auth status`
a když je Claude odhlášený nebo přihlášení vyprší do 5 dní, pošle upozornění
přes ntfy (appka v mobilu), Gmail, nebo Resend.

Nastavení (bez hesel): ~/.config/claude-hlidac.json, jazyk upozornění
"jazyk": "cs" (výchozí) nebo "en".
Heslo nebo klíč (jen Gmail a Resend): ~/.config/claude-hlidac-tajne

  claude-hlidac.py               běžná kontrola (spouští ji cron)
  claude-hlidac.py --nanecisto   jen vypíše stav a co by poslal, nic neodešle
  claude-hlidac.py --zkouska     hned pošle zkušební upozornění
  claude-hlidac.py --uloz-heslo  zeptá se na heslo/klíč a uloží ho jen pro tebe
"""
import datetime, getpass, json, os, smtplib, subprocess, sys, urllib.request
from email.message import EmailMessage

DOMOV = os.path.expanduser("~")
NASTAVENI = os.path.join(DOMOV, ".config", "claude-hlidac.json")
TAJNE = os.path.join(DOMOV, ".config", "claude-hlidac-tajne")
CLAUDE = os.environ.get("CLAUDE_BIN", os.path.join(DOMOV, ".local", "bin", "claude"))
UA = "claude-vps-hlidac/1.0"  # Resend bez hlavičky User-Agent vrací 403

TEXTY = {
    "cs": {
        "nejde": "Nejde zjistit stav přihlášení Claude (příkaz `claude auth status` selhal).",
        "odhlaseny": "Claude je ODHLÁŠENÝ, Remote Control nefunguje. Je potřeba se znovu přihlásit.",
        "bez_data": "Přihlášený, datum vypršení neznámé.",
        "plati": "Přihlášený, vyprší {datum} (za {dni} dní).",
        "vyprsi": "Přihlášení Claude vyprší za {dni} dní ({datum}). Je potřeba se znovu přihlásit.",
        "titulek": "Claude na serveru {nazev}: je potřeba se přihlásit",
        "zkouska_titulek": "Claude na serveru {nazev}: zkouška hlídače",
        "zkouska_text": "Tohle je zkušební upozornění. Když ho vidíš, hlídač přihlášení funguje.",
        "odeslano": "Zkušební upozornění odesláno.",
        "nenastaveno": "Hlídač ještě není nastavený (chybí {soubor}).",
        "vse_ok": "nic, vše v pořádku",
        "zadej": "Vlož heslo nebo klíč (při psaní není nic vidět) a stiskni Enter: ",
        "prazdne": "Nic nezadáno, nic jsem neuložil.",
        "ulozeno": "Uloženo do {soubor} (čitelné jen pro tebe).",
    },
    "en": {
        "nejde": "Cannot check the Claude login status (`claude auth status` failed).",
        "odhlaseny": "Claude is LOGGED OUT, Remote Control is not working. Please log in again.",
        "bez_data": "Logged in, expiry date unknown.",
        "plati": "Logged in, expires {datum} (in {dni} days).",
        "vyprsi": "The Claude login expires in {dni} days ({datum}). Please log in again.",
        "titulek": "Claude on server {nazev}: login needed",
        "zkouska_titulek": "Claude on server {nazev}: watchdog test",
        "zkouska_text": "This is a test notification. If you can see it, the login watchdog works.",
        "odeslano": "Test notification sent.",
        "nenastaveno": "The watchdog is not set up yet ({soubor} is missing).",
        "vse_ok": "nothing, all good",
        "zadej": "Paste the password or key (nothing shows while typing) and press Enter: ",
        "prazdne": "Nothing entered, nothing saved.",
        "ulozeno": "Saved to {soubor} (readable only by you).",
    },
}


def nacti_nastaveni():
    try:
        with open(NASTAVENI) as f:
            return json.load(f)
    except FileNotFoundError:
        return None


def texty(n):
    return TEXTY.get((n or {}).get("jazyk", "cs"), TEXTY["cs"])


def stav(t=TEXTY["cs"]):
    """Vrátí (problém nebo None, popis stavu)."""
    try:
        vystup = subprocess.run([CLAUDE, "auth", "status"], capture_output=True, text=True, timeout=60).stdout
        d = json.loads(vystup)
    except Exception:
        return t["nejde"], t["nejde"]
    if not d.get("loggedIn"):
        return t["odhlaseny"], t["odhlaseny"]
    exp = d.get("loginExpiresAt")
    if not exp:
        return None, t["bez_data"]
    konec = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))
    zbyva = (konec - datetime.datetime.now(datetime.timezone.utc)).days
    popis = t["plati"].format(datum=exp[:10], dni=zbyva)
    if zbyva < 5:
        return t["vyprsi"].format(datum=exp[:10], dni=zbyva), popis
    return None, popis


def tajne():
    with open(TAJNE) as f:
        return f.read().strip()


def posli(n, titulek, text):
    zpusob = n.get("zpusob")
    if zpusob == "ntfy":
        data = json.dumps({"topic": n["ntfy_tema"], "title": titulek, "message": text, "priority": 4}).encode()
        req = urllib.request.Request(n.get("ntfy_server", "https://ntfy.sh"), data=data,
                                     headers={"Content-Type": "application/json", "User-Agent": UA})
        urllib.request.urlopen(req, timeout=30)
    elif zpusob == "gmail":
        m = EmailMessage()
        m["From"] = n["gmail_adresa"]
        m["To"] = n.get("prijemce", n["gmail_adresa"])
        m["Subject"] = titulek
        m.set_content(text)
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as s:
            s.login(n["gmail_adresa"], tajne().replace(" ", ""))
            s.send_message(m)
    elif zpusob == "resend":
        mail = {"from": n["odesilatel"], "to": [n["prijemce"]], "subject": titulek, "text": text}
        req = urllib.request.Request("https://api.resend.com/emails", data=json.dumps(mail).encode(),
                                     headers={"Authorization": f"Bearer {tajne()}",
                                              "Content-Type": "application/json", "User-Agent": UA})
        urllib.request.urlopen(req, timeout=30)
    else:
        sys.exit(f"Neznámý způsob upozornění {zpusob!r} v {NASTAVENI} (čekám ntfy, gmail nebo resend).")


def uloz_heslo(t):
    heslo = getpass.getpass(t["zadej"]).strip()
    if not heslo:
        sys.exit(t["prazdne"])
    os.makedirs(os.path.dirname(TAJNE), exist_ok=True)
    fd = os.open(TAJNE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(heslo + "\n")
    print(t["ulozeno"].format(soubor=TAJNE))


def main(args):
    n = nacti_nastaveni()
    t = texty(n)
    if "--uloz-heslo" in args:
        return uloz_heslo(t)
    if n is None:
        print(t["nenastaveno"].format(soubor=NASTAVENI))
        return 1 if "--zkouska" in args else 0
    nazev = n.get("nazev_serveru", "VPS")
    if "--zkouska" in args:
        posli(n, t["zkouska_titulek"].format(nazev=nazev), t["zkouska_text"])
        print(t["odeslano"])
        return 0
    problem, popis = stav(t)
    if "--nanecisto" in args:
        print("STAV:", popis)
        print("POSLAL BY:", problem if problem else t["vse_ok"])
    elif problem:
        posli(n, t["titulek"].format(nazev=nazev), problem)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
