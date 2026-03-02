from pwn import *

# --- DEFINIZIONE DELLE OPERAZIONI ---

def SOMMA(a, b):
    return a + b

def POTENZA(a, b):
    return pow(a, b)

def DIFFERENZA(a, b):
    return a - b

def PRODOTTO(a, b):
    return a * b

def DIVISIONE_INTERA(a, b):
    return a // b   # divisione intera corretta


# --- CONNESSIONE AL SERVER ---

p = remote('2048.challs.olicyber.it', 10007)
count = 0

print("\n[+] Connessione stabilita. Inizio a risolvere le operazioni...\n")


# --- LOOP PRINCIPALE ---

while count < 2048:

    # Leggo tutto ciò che il server ha inviato finora
    output = p.recv(timeout=0.2)

    # Se non arriva nulla, continuo ad aspettare
    if not output:
        continue

    # Decodifico e pulisco
    testo = output.decode().strip()

    # Stampo l’output ricevuto (utile per debug)
    print(f"[SERVER] {testo}")

    # Prendo l’ultima riga, che contiene l’operazione
    righe = testo.split("\n")
    ultima = righe[-1].split()

    # Estraggo operazione e numeri
    operazione = ultima[0]
    a = int(ultima[1])
    b = int(ultima[2])

    # Switch-case delle operazioni
    match operazione:
        case 'SOMMA':
            res = SOMMA(a, b)
        case 'DIFFERENZA':
            res = DIFFERENZA(a, b)
        case 'PRODOTTO':
            res = PRODOTTO(a, b)
        case 'POTENZA':
            res = POTENZA(a, b)
        case 'DIVISIONE_INTERA':
            res = DIVISIONE_INTERA(a, b)
        case _:
            print(f"[!] Operazione sconosciuta: {operazione}")
            continue

    # Invio il risultato al server
    p.sendline(str(res).encode())

    print(f"[YOU] {operazione} {a} {b} = {res}\n")

    count += 1


# --- DOPO LE 2048 OPERAZIONI ---

print("\n[+] Tutte le operazioni inviate. Attendo la flag...\n")

finale = p.recvall(timeout=2).decode(errors="ignore")
print(finale)

print("\n🎉 FLAG TROVATA!! 🎉\n")
