#!/usr/bin/env python3
"""Hlídač přihlášení Claude na tomto serveru.

Přihlášení Claude vyprší zhruba po 4 týdnech a Remote Control pak potichu
přestane fungovat. Hlídač jednou denně (z cronu) zjistí `claude auth status`
a když je Claude odhlášený nebo přihlášení vyprší do 5 dní, pošle upozornění
přes ntfy (appka v mobilu), Gmail, nebo Resend.

Nastavení (bez hesel): ~/.config/claude-hlidac.json
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


def stav():
    """Vrátí (problém nebo None, popis stavu)."""
    try:
        vystup = subprocess.run([CLAUDE, "auth", "status"], capture_output=True, text=True, timeout=60).stdout
        d = json.loads(vystup)
    except Exception:
        z = "Nejde zjistit stav přihlášení Claude (příkaz `claude auth status` selhal)."
        return z, z
    if not d.get("loggedIn"):
        z = "Claude je ODHLÁŠENÝ, Remote Control nefunguje. Je potřeba se znovu přihlásit."
        return z, z
    exp = d.get("loginExpiresAt")
    if not exp:
        return None, "Přihlášený, datum vypršení neznámé."
    konec = datetime.datetime.fromisoformat(exp.replace("Z", "+00:00"))
    zbyva = (konec - datetime.datetime.now(datetime.timezone.utc)).days
    popis = f"Přihlášený, vyprší {exp[:10]} (za {zbyva} dní)."
    if zbyva < 5:
        return f"Přihlášení Claude vyprší za {zbyva} dní ({exp[:10]}). Je potřeba se znovu přihlásit.", popis
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


def uloz_heslo():
    heslo = getpass.getpass("Vlož heslo nebo klíč (při psaní není nic vidět) a stiskni Enter: ").strip()
    if not heslo:
        sys.exit("Nic nezadáno, nic jsem neuložil.")
    os.makedirs(os.path.dirname(TAJNE), exist_ok=True)
    fd = os.open(TAJNE, os.O_WRONLY | os.O_CREAT | os.O_TRUNC, 0o600)
    with os.fdopen(fd, "w") as f:
        f.write(heslo + "\n")
    print(f"Uloženo do {TAJNE} (čitelné jen pro tebe).")


def main(args):
    if "--uloz-heslo" in args:
        return uloz_heslo()
    try:
        with open(NASTAVENI) as f:
            n = json.load(f)
    except FileNotFoundError:
        print(f"Hlídač ještě není nastavený (chybí {NASTAVENI}).")
        return 1 if "--zkouska" in args else 0
    nazev = n.get("nazev_serveru", "VPS")
    titulek = f"Claude na serveru {nazev}: je potřeba se přihlásit"
    if "--zkouska" in args:
        posli(n, f"Claude na serveru {nazev}: zkouška hlídače",
              "Tohle je zkušební upozornění. Když ho vidíš, hlídač přihlášení funguje.")
        print("Zkušební upozornění odesláno.")
        return 0
    problem, popis = stav()
    if "--nanecisto" in args:
        print("STAV:", popis)
        print("POSLAL BY:", problem if problem else "nic, vše v pořádku")
    elif problem:
        posli(n, titulek, problem)
    return 0


if __name__ == "__main__":
    sys.exit(main(sys.argv[1:]))
