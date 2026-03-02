from pwn import *

def SOMMA(a, b):
    return a+b;

def POTENZA(a,b):
    return pow(a,b);

def DIFFERENZA(a,b):
    return a-b;

def PRODOTTO(a,b):
    return a*b;

def DIVISIONE_INTERA(a,b):
    return a//b;

p= remote('2048.challs.olicyber.it', '10007');
count=0;

while count <= 2048 :

    output = p.recv(timeout=0.7);

    testo=output.decode().strip();

    righe=testo.split('\n');
    ultima=righe[-1].split();

    if count == 2048:

        operazione=ultima[0];
        a=int(ultima[1]);
        b=int(ultima[2]);

        match operazione:
            case 'SOMMA':
                res = SOMMA(a,b);

            case 'DIFFERENZA':
                res = DIFFERENZA(a,b);

            case 'PRODOTTO':
                res = PRODOTTO(a,b);

            case 'POTENZA':
                res = POTENZA(a,b);

            case 'DIVISIONE_INTERA':
                res = DIVISIONE_INTERA(a,b);

        p.sendline(str(res).encode());

    count+=1;

print(output);