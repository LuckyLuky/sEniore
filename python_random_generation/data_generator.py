import random
import unicodedata

# Open documents for name and surname generator
input_file = open('names.csv', encoding = 'utf-8')
names = [line.strip().split(';') for line in input_file]
input_file.close()

input_file = open('surnames.csv', encoding = 'utf-8')
surnames = [line.strip().split(';') for line in input_file]
input_file.close()

# Create 4 empty lists (for now empty)
names_M = []        # Male Names
names_F = []        # Female Names

surnames_M = []     # Male Surnames
surnames_F = []     # Female Surnames

# Fill in two Name lists according to gender
for name in names: 
    if name [1] == 'muž':
        names_M = names_M + [name [0]]
    elif name [1] == 'žena':
        names_F = names_F + [name [0]]
    else:
        print('ERROR!!!') # For possible error check
        exit ()

# Fill in two Surname lists according to gender
for sur in surnames:
    if sur [1] == 'muž':
        surnames_M = surnames_M + [sur [0]]
    elif sur [1] == 'žena':
        surnames_F = surnames_F + [sur [0]]
    else:
        print('ERROR!!!') # For possible error check
        exit ()


# Create table Users (now empty)
user_table = []
line = 1

while line < 1000: 
    gender = random.randint(1, 2) # random generator to coose gender: 1 = men, 2 = women

    # For male:
    if gender == 1: 
        name = random.randint(0, len(names_M)-1)                                # random number to choose the name
        sur = random.randint(0, len(surnames_M)-1)                              # random number to choose the surname
        for_email = f'{names_M [name][0].lower()}.{surnames_M [sur].lower()}'   # creates email in format 'n.surname'

        # Cycle to remove diacritics from email name
        for_email = unicodedata.normalize('NFKD', for_email)
        email = ''
        for c in for_email:
            if not unicodedata.combining(c):
                email += c
        
        # Telephone number generator
        telephone = '775'+ str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))
        
        # Adding data to user table
        user_table = user_table + [ 
            [
            int(1000 + line),                   # ID
            names_M [name],                     # NAME
            surnames_M [sur],                   # SURNAME
            f'{email}@gmail.com',               # EMAIL
            'password',                         # PASSWORD
            telephone]                          # TELEPHONE
            ]
    
    # For female:
    if gender == 2:
        name = random.randint(0, len(names_F)-1)                                # random number to choose the name
        sur = random.randint(0, len(surnames_F)-1)                              # random number to choose the surname
        for_email = f'{names_F [name][0].lower()}.{surnames_F [sur].lower()}'   # creates email in format 'n.surname'

        # Cycle to remove diacritics from email name
        for_email = unicodedata.normalize('NFKD', for_email)
        email = ''
        for c in for_email:
            if not unicodedata.combining(c):
                email += c
        
        # Telephone number generator
        telephone = '775'+ str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))+str(random.randint(0, 9))
        
        # Adding data to user table
        user_table = user_table + [
            [ 
            int(1000 + line),                   # ID
            names_F [name],                     # NAME
            surnames_F [sur],                # SURNAME
            f'{email}@gmail.com',               # EMAIL
            'password',                         # PASSWORD
            telephone]                          # TELEPHONE
            ]
    line = line + 1


# download data to new file / overwrite in existing file
new_data = open ('user_table.csv', 'w', encoding = 'utf-8')
new_data.write('id; name; surname; email; password; telephone'+'\n')
for x in user_table:
    for y in x:
        new_data.write(str(y) + ';')
    new_data.write('\n')
new_data.close()