import random

# Open Users table
input_file = open('user_table.csv', encoding = 'utf-8')
user_table = [line.strip().split(';') for line in input_file]
input_file.close()

r_d_data = [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]              # List of service types IDs

# Create a list of User ID
users = []
for user in user_table:                            
    users = users + [user[0]]   

users = users[1:]


# Creation of Request/Demand table

r_d_table = []

for u in users:
    r_d_number = random.randint(0, 10)                                          # Choose the number of R/Ds for this User
    n = 0  
    data = r_d_data                                                             # 'Fake' r_d_data table for the cycle
    while n < r_d_number:
        r_d = random.randint(0, len(data)-1)                                    # Random number to choose one of R/D options from 'fake' table data
        types = random.randint(1, 2)                                            # Choose if it is a Demand or a Request  
        r_d_table = r_d_table +[[10000+n, u, types, data[r_d]]]              # Create new line in r_d_table list
        data = data[0:r_d] + data[r_d+1:]                                       # Exclude used R/D option from our 'fake' data table to avoid duplicates
        n = n + 1                                           

# download data to new file / overwrite in existing file
new_data = open ('r_d_table.csv', 'w', encoding = 'utf-8')
new_data.write('user ID; request/demand; r/d type '+'\n')
for x in r_d_table:
    for y in x:
        new_data.write(str(y) + ';')
    new_data.write('\n')
new_data.close()
