"""Testy hlídače přihlášení. Nic neodesílá ven: síť i SMTP jsou podvržené.

Spuštění: python3 -m unittest discover testy
"""
import datetime, importlib.util, io, json, os, sys, tempfile, unittest
from contextlib import redirect_stdout
from pathlib import Path
from unittest import mock

SKRIPT = Path(__file__).resolve().parent.parent / "skills/vps-remote-control/scripts/claude-hlidac.py"


def nacti_hlidace(domov, claude_bin):
    with mock.patch.dict(os.environ, {"HOME": domov, "CLAUDE_BIN": claude_bin}):
        spec = importlib.util.spec_from_file_location("hlidac", SKRIPT)
        h = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(h)
    return h


class Hlidac(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.domov = self.tmp.name
        self.claude = os.path.join(self.domov, "falesny-claude")
        self.h = nacti_hlidace(self.domov, self.claude)
        os.makedirs(os.path.join(self.domov, ".config"))

    def tearDown(self):
        self.tmp.cleanup()

    def falesny_stav(self, stav):
        with open(self.claude, "w") as f:
            f.write("#!/bin/sh\necho '%s'\n" % json.dumps(stav))
        os.chmod(self.claude, 0o755)

    def vyprsi_za(self, dni):
        konec = datetime.datetime.now(datetime.timezone.utc) + datetime.timedelta(days=dni, hours=1)
        return {"loggedIn": True, "loginExpiresAt": konec.strftime("%Y-%m-%dT%H:%M:%SZ")}

    def nastav(self, n, heslo=None):
        with open(self.h.NASTAVENI, "w") as f:
            json.dump(n, f)
        if heslo:
            with open(self.h.TAJNE, "w") as f:
                f.write(heslo + "\n")

    def spust(self, *args):
        out = io.StringIO()
        with redirect_stdout(out):
            kod = self.h.main(list(args))
        return kod, out.getvalue()

    # --- stav přihlášení ---
    def test_v_poradku_nic_neposle(self):
        self.falesny_stav(self.vyprsi_za(20))
        problem, popis = self.h.stav()
        self.assertIsNone(problem)
        self.assertIn("za 20 dní", popis)

    def test_brzke_vyprseni_je_problem(self):
        self.falesny_stav(self.vyprsi_za(3))
        problem, _ = self.h.stav()
        self.assertIn("vyprší za 3 dní", problem)

    def test_odhlaseny_je_problem(self):
        self.falesny_stav({"loggedIn": False})
        problem, _ = self.h.stav()
        self.assertIn("ODHLÁŠENÝ", problem)

    def test_rozbity_vystup_je_problem(self):
        with open(self.claude, "w") as f:
            f.write("#!/bin/sh\necho 'Not logged in'\n")
        os.chmod(self.claude, 0o755)
        problem, _ = self.h.stav()
        self.assertIn("Nejde zjistit", problem)

    def test_chybejici_claude_je_problem(self):
        problem, _ = self.h.stav()  # falešný claude vůbec neexistuje
        self.assertIn("Nejde zjistit", problem)

    # --- režimy spuštění ---
    def test_bez_nastaveni_cron_tise_skonci(self):
        self.assertEqual(self.spust()[0], 0)

    def test_bez_nastaveni_zkouska_selze(self):
        self.assertEqual(self.spust("--zkouska")[0], 1)

    def test_nanecisto_nic_neodesle(self):
        self.falesny_stav({"loggedIn": False})
        self.nastav({"zpusob": "ntfy", "ntfy_tema": "t"})
        with mock.patch("urllib.request.urlopen") as u:
            kod, out = self.spust("--nanecisto")
        u.assert_not_called()
        self.assertIn("POSLAL BY: Claude je ODHLÁŠENÝ", out)

    def test_cron_v_poradku_nic_neodesle(self):
        self.falesny_stav(self.vyprsi_za(20))
        self.nastav({"zpusob": "ntfy", "ntfy_tema": "t"})
        with mock.patch("urllib.request.urlopen") as u:
            self.spust()
        u.assert_not_called()

    # --- tři způsoby odeslání ---
    def test_ntfy(self):
        self.falesny_stav({"loggedIn": False})
        self.nastav({"zpusob": "ntfy", "ntfy_tema": "claude-abc", "nazev_serveru": "Forpsi"})
        with mock.patch("urllib.request.urlopen") as u:
            self.spust()
        req = u.call_args[0][0]
        self.assertEqual(req.full_url, "https://ntfy.sh")
        telo = json.loads(req.data)
        self.assertEqual(telo["topic"], "claude-abc")
        self.assertIn("Forpsi", telo["title"])
        self.assertIn("ODHLÁŠENÝ", telo["message"])

    def test_gmail(self):
        self.falesny_stav({"loggedIn": False})
        self.nastav({"zpusob": "gmail", "gmail_adresa": "a@gmail.com"}, heslo="abcd efgh ijkl mnop")
        with mock.patch("smtplib.SMTP_SSL") as smtp:
            self.spust()
        s = smtp.return_value.__enter__.return_value
        s.login.assert_called_once_with("a@gmail.com", "abcdefghijklmnop")
        zprava = s.send_message.call_args[0][0]
        self.assertEqual(zprava["To"], "a@gmail.com")
        self.assertIn("ODHLÁŠENÝ", zprava.get_content())

    def test_resend(self):
        self.falesny_stav({"loggedIn": False})
        self.nastav({"zpusob": "resend", "odesilatel": "hlidac@domena.cz", "prijemce": "ja@domena.cz"}, heslo="re_xyz")
        with mock.patch("urllib.request.urlopen") as u:
            self.spust()
        req = u.call_args[0][0]
        self.assertEqual(req.get_header("Authorization"), "Bearer re_xyz")
        self.assertTrue(req.get_header("User-agent"))
        self.assertEqual(json.loads(req.data)["to"], ["ja@domena.cz"])

    def test_zkouska_posle_i_kdyz_je_vse_v_poradku(self):
        self.falesny_stav(self.vyprsi_za(20))
        self.nastav({"zpusob": "ntfy", "ntfy_tema": "t"})
        with mock.patch("urllib.request.urlopen") as u:
            self.spust("--zkouska")
        self.assertIn("zkouška", json.loads(u.call_args[0][0].data)["title"])

    def test_neznamy_zpusob(self):
        self.falesny_stav({"loggedIn": False})
        self.nastav({"zpusob": "sms"})
        with self.assertRaises(SystemExit):
            self.spust()

    # --- jazyk ---
    def test_anglicke_upozorneni(self):
        self.falesny_stav({"loggedIn": False})
        self.nastav({"zpusob": "ntfy", "ntfy_tema": "t", "nazev_serveru": "Hetzner", "jazyk": "en"})
        with mock.patch("urllib.request.urlopen") as u:
            self.spust()
        telo = json.loads(u.call_args[0][0].data)
        self.assertEqual(telo["title"], "Claude on server Hetzner: login needed")
        self.assertIn("LOGGED OUT", telo["message"])

    def test_anglicky_stav_vyprseni(self):
        self.falesny_stav(self.vyprsi_za(3))
        problem, _ = self.h.stav(self.h.TEXTY["en"])
        self.assertIn("expires in 3 days", problem)

    def test_neznamy_jazyk_je_cesky(self):
        self.assertIs(self.h.texty({"jazyk": "xx"}), self.h.TEXTY["cs"])

    def test_jazyky_maji_stejne_texty(self):
        self.assertEqual(self.h.TEXTY["cs"].keys(), self.h.TEXTY["en"].keys())

    # --- uložení hesla ---
    def test_uloz_heslo_jen_pro_vlastnika(self):
        with mock.patch("getpass.getpass", return_value=" tajne "):
            self.spust("--uloz-heslo")
        self.assertEqual(self.h.tajne(), "tajne")
        self.assertEqual(os.stat(self.h.TAJNE).st_mode & 0o777, 0o600)


if __name__ == "__main__":
    unittest.main()
