import random
import unicodedata
# open documents for name and sirname generator
input_file = open('names.txt', encoding = 'utf-8')
names = [line.strip().split('\t') for line in input_file]
input_file.close()

input_file = open('surnames.txt', encoding = 'utf-8')
surnames = [line.strip().split('\t') for line in input_file]
input_file.close()

# Creat 2 list for names and sirnames devided according to gender
names_M = []
names_F = []
surnames_M = []
surnames_F = []

for name in names:
    if name [1] == 'muž':
        names_M = names_M + [name [0]]
    elif name [1] == 'žena':
        names_F = names_F + [name [0]]
    else:
        print('ERROR!!!')
        exit ()

for sur in surnames:
    if sur [1] == 'muž':
        surnames_M = surnames_M + [sur [0]]
    elif sur [1] == 'žena':
        surnames_F = surnames_F + [sur [0]]
    else:
        print('ERROR!!!')
        exit ()

# create the data for table Users: ID, NAME, SIRNAME, EMAIL, PASSWORD, TELEPHONE
user_table = []
line = 1

while line < 1000:
    # random generator to coose gender: 1 = men, 2 = women
    gender = random.randint(1, 2)

    if gender == 1:
        name = random.randint(0, len(names_M)-1)
        sur = random.randint(0, len(surnames_M)-1)
        for_email = surnames_M [sur].lower()

        # Cycle to remove diacritics from email name
        for_email = unicodedata.normalize('NFKD', for_email)
        email = ''
        for c in for_email:
            if not unicodedata.combining(c):
                email += c
        
        
        telephone = '775'+ str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))
        user_table = user_table + [ 
            [
            int(1000 + line), 
            names_M [name], 
            f'{surnames_M [sur][0]}{surnames_M[sur][1:].lower()}', 
            f'{names_M [name][0].lower()}.{email}@gmail.com',
            'password',
            telephone]
            ]
    if gender == 2:
        name = random.randint(0, len(names_F)-1)
        sur = random.randint(0, len(surnames_F)-1)
        for_email = surnames_F [sur].lower()

        # Cycle to remove diacritics from email name
        for_email = unicodedata.normalize('NFKD', for_email)
        email = ''
        for c in for_email:
            if not unicodedata.combining(c):
                email += c
        
        
        telephone = '775'+ str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))
        user_table = user_table + [
            [ 
            int(1000 + line), 
            names_F [name], 
            f'{surnames_F [sur][0]}{surnames_F[sur][1:].lower()}', 
            f'{names_F [name][0].lower()}.{email}@gmail.com',
            'password',
            telephone]
            ]
    line = line + 1

# download data to new file / overwrite in existing file
new_data = open ('user_table.txt', 'w', encoding = 'utf-8')
new_data.write('id; name; surname; email; password; telephone'+'\n')
for x in user_table:
    for y in x:
        new_data.write(str(y) + ';')
    new_data.write('\n')
new_data.close()
