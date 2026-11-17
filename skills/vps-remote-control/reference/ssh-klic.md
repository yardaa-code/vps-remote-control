# SSH klíč a první připojení (Mac i Windows)

Výsledek tohoto kroku: klíč `~/.ssh/claude_vps`, jeho veřejná část u roota na serveru a v `~/.ssh/config`
dva zástupné názvy `claude-vps` a `claude-vps-root`.

## 1. Vytvořit klíč (uděláš ty)
Nejdřív zkontroluj, že `~/.ssh/claude_vps` ještě neexistuje (**nikdy ho nepřepisuj**, uživatel by mohl
přijít o přístup). Pak:

```bash
mkdir -p ~/.ssh && ssh-keygen -t ed25519 -f ~/.ssh/claude_vps -N "" -C "claude-vps"
```

Klíč je bez hesla, aby se k serveru dalo připojit bez dalšího zadávání. Řekni uživateli, že soubor
`~/.ssh/claude_vps` je jako klíč od bytu: nikomu ho neposílat. Kdo chce klíč s heslem, na Macu jde
použít Klíčenku (`ssh-add --apple-use-keychain`), na Windows službu `ssh-agent`. Pro nováčka to
nedoporučuj, přidává to problémy po restartu počítače.

## 2. Zapsat zástupné názvy (uděláš ty)
Přečti `~/.ssh/config` (může neexistovat) a **přidej** na konec, nic stávajícího neměň:

```
Host claude-vps
  HostName <IP>
  User claude
  IdentityFile ~/.ssh/claude_vps
  IdentitiesOnly yes

Host claude-vps-root
  HostName <IP>
  User root
  IdentityFile ~/.ssh/claude_vps
  IdentitiesOnly yes
```

## 3. Nahrát klíč na server (udělá uživatel ve svém terminálu)
Tady je potřeba **heslo roota**, a to do chatu nepatří. Uživatel proto příkaz spustí ve vlastním okně
terminálu. Při prvním připojení se server zeptá `Are you sure you want to continue connecting`,
odpoví `yes`. Pak vloží heslo roota (při psaní není nic vidět, to je v pořádku).

**Mac** (aplikace Terminál):
```bash
ssh-copy-id -i ~/.ssh/claude_vps.pub root@<IP>
```

**Windows** (nabídka Start → napsat PowerShell → otevřít):
```powershell
type $env:USERPROFILE\.ssh\claude_vps.pub | ssh root@<IP> "mkdir -p ~/.ssh && chmod 700 ~/.ssh && cat >> ~/.ssh/authorized_keys && chmod 600 ~/.ssh/authorized_keys"
```

Do příkazu za uživatele doplň skutečnou IP adresu, ať jen kopíruje.

## 4. Ověřit (uděláš ty)
```bash
ssh -o BatchMode=yes claude-vps-root 'echo OK'
```
Vypíše `OK`, je hotovo. Když ne:
- `Permission denied`: klíč se nenahrál, ať uživatel zopakuje krok 3 a pošle ti, co vypsal (bez hesla).
- `Host key verification failed`: uživatel v kroku 3 nepotvrdil `yes`, ať se jednou připojí
  `ssh root@<IP>` a potvrdí.
- `Connection timed out`: špatná IP nebo server ještě není zřízený.
