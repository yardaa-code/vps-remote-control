# Přihlášení Claude na serveru a úvodní otázky

## Proč to jde přes chat
Přihlášení vypíše odkaz, uživatel ho otevře v prohlížeči a dostane kód. Terminál na serveru ale uživatel
nevidí, takže kód pošle tobě do chatu a ty ho na serveru zadáš. Kód je **jednorázový**, po použití je
k ničemu, proto tady výjimečně do chatu smí.

## Postup
Všechno jako účet `claude` (`ssh claude-vps`), ne root.

1. Spusť přihlášení v pomocném screen okně `login` se záznamem výstupu a odkaz vytáhni ze záznamu.
   **Odkaz neber ze snímku okna (`hardcopy`)**: okno má 80 znaků a odkaz by byl useknutý a nefunkční.
   ```bash
   ssh claude-vps 'rm -f /tmp/login.log; screen -L -Logfile /tmp/login.log -dmS login ~/.local/bin/claude auth login --claudeai; sleep 8; grep -ao "https://[^[:space:][:cntrl:]]*" /tmp/login.log | sort -u'
   ```
   Když odkaz nenajdeš, přečti okno (`screen -S login -X hardcopy /tmp/login.txt; cat /tmp/login.txt`)
   a podívej se, co Claude píše (třeba čeká na volbu).
2. Pošli uživateli odkaz: „Otevři ho, přihlas se svým účtem Claude, potvrď a pošli mi kód, který uvidíš.“
3. Kód zadej (bez mezer okolo):
   ```bash
   ssh claude-vps 'screen -S login -X stuff "<KÓD>\r"; sleep 5; screen -S login -X hardcopy /tmp/login.txt; tail -5 /tmp/login.txt'
   ```
4. Ověř a pomocné okno zavři:
   ```bash
   ssh claude-vps '~/.local/bin/claude auth status; screen -S login -X quit; rm -f /tmp/login.txt /tmp/login.log'
   ```
   Čekáš `"loggedIn": true`. Když ne, kód byl špatně opsaný nebo vypršel, začni znovu od bodu 1.

## Opakované přihlášení (po ~4 týdnech)
Stejný postup. Pak Claude restartuj, ať si přihlášení načte: `ssh claude-vps 'screen -S claude -X quit'`
(služba ho do 20 s spustí znovu) a zkontroluj okno podle další části.

## Úvodní otázky ve screen
Po `systemctl start claude-remote` (nebo po restartu) běží Claude ve screen okně `claude`. Při prvním
spuštění se ptá na pár věcí. **Nikdy nemačkej Enter naslepo.** Vždy nejdřív přečti okno:

```bash
ssh claude-vps 'sleep 3; screen -S claude -X hardcopy /tmp/c.txt; cat /tmp/c.txt'
```

Klávesy posíláš takhle:
- Enter: `screen -S claude -X stuff $'\r'`
- šipka dolů: `screen -S claude -X stuff $'\033[B'`
- text: `screen -S claude -X stuff "text"`

Po každé klávese okno znovu přečti. Co se typicky objeví:
- **Výběr vzhledu (theme):** Enter (výchozí je v pořádku).
- **Přihlášení:** když se zeptá znovu, i když `auth status` je `true`, projdi ho stejně jako výše, jen kód
  posíláš do okna `claude`, ne `login`.
- **„Quick safety check“ / důvěřuješ této složce:** **POZOR, zvýrazněná výchozí volba je „No, exit“ a
  Enter by Claude ukončil.** Nejdřív šipka dolů na „Yes, I trust this folder“, okno přečti a ověř, že je
  zvýrazněná správná volba, teprve pak Enter. Číslo `2` tady nefunguje.
- **Nabídky novinek apod.:** přečti a zvol rozumnou výchozí možnost, při nejistotě se zeptej uživatele.

Hotovo je, když okno ukazuje `/remote-control is active`. Na závěr `rm -f /tmp/c.txt`.

Kdyby se Claude omylem ukončil, služba ho do 20 s spustí znovu a otázky přijdou znovu.

## Režim oprávnění
Klávesovou zkratku pro přepnutí režimu (Shift+Tab) **neposílej zvenku**. Režim si uživatel zvolí sám
v aplikaci. Řekni mu jen, co znamená: v automatickém režimu Claude spouští příkazy bez ptaní, proto je
server jen pro Claude.
