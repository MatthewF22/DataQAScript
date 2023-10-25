import csv
import os
from subprocess import Popen
import colorama
from colorama import Fore
import numpy as np
# ----------User Inputs---------------------------------------------#
# Define the outer folder with the datafiles you want to validate
# Make sure any backslashes are doubled -> For example: 'C:\Users' should actually be 'C:\\Users'
dir = "C:\\Users\\Matth\\PycharmProjects\\Datafiles\\testData"

# Define the csv file that contains the list of Do Not Sell cocodes
dns_file = 'C:\\Users\\Matth\\PycharmProjects\\DNS cocodes\\do_not_sell_2022_q1.csv'
# ------------------------------------------------------------------#

# GET DNS CODES FROM DNS CSV
with open(dns_file, 'r') as dns_csv:
    dns_raw = dns_csv.readlines()

# delete the new line character off of the end of each co_code
dns = [line[:-1] for line in dns_raw]
# the first cocode in the file has some unreadable characters that we need to clean
#dns[0] = dns[0][3:]
# Uncomment this line to see what is being cleaned
print('Raw file contents:\n', dns_raw, '\n\nCleaned File:\n', dns)

# CREATE OUTPUT CSV
# This csv will open when the program finishes and list out any errors that it recieved
try:
    outfile = open('diff.txt', 'w')
    outfile.write('CO_CODE:  ' + ',' + 'FILEPATH:  ' + ',' + 'ISSUE:  ' + '\n')
except:
    print("Please close diff.txt and re-run this program")
    x = input()


# FUNCTION TO FIND ERRORS
def find_errors(filepath, outfile, dns):
    # Read in the data from the datafile
    datafile_content = []
    rawItems = []
    with open(filepath, 'r') as datafile:
        for row in datafile:
            datafile_content.append(row.split(',')[0])
            rawItems.append(row.split(','))  # Takes all the data from each line and seperates it into singular pieces in
        # chars var used for telling if file is blank
        datafile.seek(0)  # move cursor to start of file
        chars = datafile.readlines()
        datafile.seek(0)
        #Delete new line characters off the ends of the csv file lines
        items = [line[:len(rawItems)] for line in rawItems]
        #print(items)
        print("\033[93mAmount of Columns:\033[0m " + str(len(items[0])) + Fore.RESET)
        outfile.write("Amount of Columns: " + str(len(items[0])) + '\n')


    # ---'Double Quote Check' --- Throw if there is a double quote inside the file
    for list in items:
        i = 0
        for pos in list:
            i += 1
            if pos.__contains__('""'):
                outfile.write(pos + ', in column ' + str(i) + ' ,' + os.path.basename(filepath) + ',check for double quotes\n')
                print(pos + ', in column ' + str(i) + ' ,' + os.path.basename(filepath) + ',check for double quotes\n')

    # ---'Decimal check'--- Throw if there is a numeric field with decimals
    usedCol = []
    for list in items:
        i = 3
        for pos in list[3:]:
            i += 1
            value = pos[:1]
            if value.isdigit():
                isNum = True
            else:
                isNum = False
            if pos.__contains__(".") and isNum == True and str(i) not in usedCol:
                outfile.write(pos + ' in column ' + str(i) + ' ,' + os.path.basename(filepath) + ',check for decimal in numeric field\n')
                print(pos + ' in column ' + str(i) + ' ,' + os.path.basename(filepath) + ',check for decimal in numeric field\n')
                usedCol.append(str(i))

    # ---'Date format check'--- Throw if there is an incorrect date format
    usedColumn = []
    for list in items:
        col = 0
        for i in list:
            col += 1
            #Check if each figure in each list contains a - or a /
            if str(col) not in usedColumn and i.__contains__("-") or i.__contains__("/"):
                outfile.write(i + ' in column ' + str(col) + ' ,' + os.path.basename(filepath) + ',check for potential date issue\n')
                print(i + ' in column ' + str(col) + ' ,' + os.path.basename(filepath) + ',check for potential date issue\n')
                usedColumn.append(str(col))

    # ----'Numeric Issue in cocode'---- Throw if there is non numeric characters in the cocode or it is not 5 digits in length
    for index in range(len(datafile_content)):
        if len(datafile_content[index]) != 5 or not datafile_content[index].isnumeric():
            outfile.write(datafile_content[index] + ',' + os.path.basename(filepath) + ',not numeric in cocode or not 5 digits\n')
            print(datafile_content[index] + ',' + os.path.basename(filepath) + ',not numeric in cocode or not 5 digits\n')

    # ----'Blank Issue'---- Throw if there is only whitespace in datafile
    empty = True
    for line in chars:
        if line and not line.isspace():
            empty = False
    if empty == True:
        outfile.write('BLANK ,' + os.path.basename(filepath) + ',Blank\n')
        print('BLANK ,' + os.path.basename(filepath) + ',Blank\n')

    # ----'Header Issue'---- If datafile is not 'Blank', check for 'Header' issue
    else:
        # look for headers in the data
        first_row = chars[0]
        first_row = first_row.split(',')
        # Throw 'Header' issue if first column of first row is not a numeric cocode.
        if not first_row[0].isnumeric():
            outfile.write(
                ';'.join(str(e) for e in first_row[:-1]) + ',' + os.path.basename(filepath) + ',Header' + '\n')
            print(';'.join(str(e) for e in first_row[:-1]) + ',' + os.path.basename(filepath) + ',Header' + '\n')

    # ----'Size Issue'---- Throw if datafile is less than 50 bytes (arbitrary value)
    if os.path.getsize(filepath) < 50:
        size = str(os.path.getsize(filepath))
        outfile.write(',' + os.path.basename(filepath) + ',Size Issue: ' + size +' bytes\n')
        print(' ,' + os.path.basename(filepath) + ',Size Issue: ' + size + ' bytes\n')

    # ----'Do Not Sell Issue'---- Throw if a DNS cocode is present in the datafile
    for index in range(len(datafile_content)):
        # Check if dns cocodes are present
        if datafile_content[index] in dns:
            outfile.write(datafile_content[index] + ',' + os.path.basename(filepath) + ',' + 'do not sell' + '\n')
            print(datafile_content[index] + ',' + os.path.basename(filepath) + ',' + 'do not sell' + '\n')

        # ----'Cocode Order Issue'----
        # Check if the cocodes are in non-decreasing order
        if index > 0:
            if datafile_content[index] < datafile_content[index - 1]:
                outfile.write(datafile_content[index] + ',' + os.path.basename(filepath) + ',' + 'cocode order' + '\n')
                print(datafile_content[index] + ',' + os.path.basename(filepath) + ',' + 'cocode order' + '\n')


# ITERATE THROUGH DATAFILES
# For every folder in the Datafiles folder
for folder in os.listdir(dir):
    print('\nNow validating directory named:', folder)
    outfile.write("Validating Directory named: " + folder + '\n')
    # For every datafile in the folder
    for filename in os.listdir(os.path.join(dir, folder)):
        print("--------------------------------------------------------")
        print("\033[92mChecking file:\033[0m " , filename , "\n")
        outfile.write("Checking File Fame: " + filename + '\n')
        # Create the filepath for a particular datafile
        filepath = os.path.join(dir, os.path.join(folder, filename))
        # Run that datafile through the find_errors function as defined above
        find_errors(filepath, outfile, dns)
        print("\033[91mDone with file:\033[0m" ,filename, '\n')
        print("--------------------------------------------------------")
        print("\033[95mThis is a color\033[0m")
        outfile.write("---------------------------------------------------------------------" + '\n')

# This opens a csv with that contains any issues with the file
p = Popen('diff.txt', shell=True)
