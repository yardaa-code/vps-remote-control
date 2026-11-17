# Objednání serveru u Forpsi

Doporučená varianta: **Classic VPS Mini+**, systém **Ubuntu 24.04**, cca **85 Kč měsíčně**
(cena z listopadu 2026, ať si ji uživatel na webu Forpsi ověří). Pro Claude to stačí, náročná práce
(přemýšlení) běží u Anthropicu, server jen spouští příkazy.

## Co řekni uživateli
1. Na webu Forpsi najdi **VPS**, varianta **Classic VPS Mini+**.
2. Jako systém vyber **Ubuntu 24.04** (ne jinou verzi, ne jiný systém).
3. Když objednávka nabízí vložit **SSH klíč**, zatím přeskoč, nahrajeme ho v dalším kroku.
4. Objednej a zaplať. Po zřízení najdeš v administraci Forpsi (případně v e-mailu) **IP adresu**
   serveru a **heslo roota**.
5. **Heslo roota si ulož do správce hesel** (nebo aspoň bezpečně poznamenej). Po nastavení se jím přes
   internet přihlásit nepůjde, ale bude potřeba v **konzoli Forpsi**, kdyby se server zasekl.
6. IP adresu mi napiš sem do chatu, heslo ne.

## Konzole Forpsi (nouzový vstup)
V administraci serveru u Forpsi je **konzole**: okno přímo do serveru, které funguje i tehdy, když SSH
nejde. Přihlašuje se v ní `root` a heslo roota. Použije se jen při problémech, viz `problemy.md`
(typicky: po aktualizaci systému přestane SSH odpovídat).

## Jiný poskytovatel
Funguje kterýkoli VPS s **Ubuntu 24.04** a přístupem jako root (Hetzner, Wedos, DigitalOcean…).
Stačí nejmenší varianta s 1 GB paměti. Postup dál je stejný, jen nouzová konzole se jmenuje jinak.
