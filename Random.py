import random
import unicodedata
vstup = open('jmena.txt', encoding = 'utf-8')
jmena = [radek.strip().split('\t') for radek in vstup]
vstup.close()

vstup = open('prijmeni.txt', encoding = 'utf-8')
prijmeni = [radek.strip().split('\t') for radek in vstup]
vstup.close()


jmena_M = []
jmena_Z = []
prijmeni_M = []
prijmeni_Z = []

for jmeno in jmena:
    if jmeno [1] == 'muž':
        jmena_M = jmena_M + [jmeno [0]]
    elif jmeno [1] == 'žena':
        jmena_Z = jmena_Z + [jmeno [0]]
    else:
        print('CYBA!!!')
        end

for prij in prijmeni:
    if prij [1] == 'muž':
        prijmeni_M = prijmeni_M + [prij [0]]
    elif jmeno [1] == 'žena':
        prijmeni_Z = prijmeni_Z + [prij [0]]
    else:
        print('CYBA!!!')
        end

tabulka_uzivatel = []
radek = 1

while radek < 1000:
    pohlavi = random.randint(1, 2)
    if pohlavi == 1:
        jm = random.randint(0, len(jmena_M)-1)
        pr = random.randint(0, len(prijmeni_M)-1)
        for_email = prijmeni_M [pr].lower()
        for_email = unicodedata.normalize('NFKD', for_email)
        email = ''
        for c in for_email:
            if not unicodedata.combining(c):
                email += c
        telefon = '775'+ str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))
        tabulka_uzivatel = tabulka_uzivatel + [ 
            [
            int(1000 + radek), 
            jmena_M [jm], 
            f'{prijmeni_M [pr][0]}{prijmeni_M[pr][1:].lower()}', 
            f'{jmena_M [jm][0]}.{email}@gmail.com',
            'password',
            telefon]
            ]
    if pohlavi == 2:
        jm = random.randint(0, len(jmena_Z)-1)
        pr = random.randint(0, len(prijmeni_Z)-1)
        for_email = prijmeni_Z [pr].lower()
        for_email = unicodedata.normalize('NFKD', for_email)
        email = ''
        for c in for_email:
            if not unicodedata.combining(c):
                email += c
        telefon = '775'+ str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))
        tabulka_uzivatel = tabulka_uzivatel + [
            [ 
            int(1000 + radek), 
            jmena_Z [jm], 
            f'{prijmeni_Z [pr][0]}{prijmeni_Z[pr][1:].lower()}', 
            f'{jmena_Z [jm][0]}.{email}@gmail.com',
            'password',
            telefon]
            ]
    radek = radek + 1

#print(tabulka_uzivatel)


soubor = open ('uzivatele.txt', 'w', encoding = 'utf-8')
soubor.write('id; jmeno; prijmeni; email; heslo; telefon'+'\n')
for x in tabulka_uzivatel:
    for y in x:
        soubor.write(str(y) + ';')
    soubor.write('\n')
soubor.close()
