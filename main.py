'''#to creating  a file 

#1) mode - x - create a file'''
'''# open("diwali.txt","r")

#2) mode - w - create a file and you write inside that file'''


'''file = open("navratri.txt","w")

file.write("Garba khelo bohot khelo or bolo jai mata di")

file = open("navratri.txt","a")

file.write("\npresentation achi rakho job ho jayega ")

file.close()

#deleting the file
from pathlib import Path
import os
p = Path("navratri.txt")
os.remove(p)'''

'''#another way of opening and working with a file

with open("diwali.txt","a") as fs:
    fs.write("hello how are you")
'''


print("press 1 - for creating a folder")
print("press 2 - for read a folder")
print("press 3 - for updating a folder")
print("press 4 - for deleting a folder")
print("press 5 - for creating a file")
print("press 6 - for reading a file")
print("press 7 - for updating a file")
print("press 8 - for deleting a file")