from pathlib import Path
import os
import shutil

def create_folder():
    name = input("Tell your folder name :-")
    p = Path(name)
    if p.exists():
        print("folder already exist try again ")
        create_folder()
    else:
        p.mkdir()
        print("new folder created successfully! ")

def read_folder():  
    p = Path("")
    items = list(p.rglob("*"))

    for i in items:
        i = str(i)
        for j in i:
            if j == ".":
                break
            else:
                print(i)

    # for i in range(len(items)):
    #     print(f"{i+1} : {items[i]}")


def update_folder():
    read_folder()
    name = input("which folder you to update :-")
    old_p = Path(name)

    if old_p.exists():
        new_name = input("Enter your new name:-")
        new_p = Path(new_name)
        old_p.rename(new_p)
        print("updated successfully")
    else:
        print("name does not exist try again")
        update_folder()

def delete_folder():
    read_folder()
    name = input("Tell your folder name :-")
    p = Path(name)
    if not p.exists() or not p.is_dir():
        print("this folder name does not exists please try again")
        delete_folder()
    else:
        # check whether the folder has anything inside it
        if any(p.iterdir()):
            confirm = input("this folder is not empty. Delete it with all its files? (y/n) :- ")
            if confirm.lower() != "y":
                print("delete cancelled")
                return
            shutil.rmtree(p)      # deletes folder + everything inside
        else:
            p.rmdir()             # empty folder
        print("folder deleted sucessfully")

def create_file():
    name = input("Tell your file name with extension :- ")
    p = Path(name)
    if p.exists() and p.is_file():
        print("File name already exist please Try again ")
        create_file
    else:
        with open(p,"w") as fs:
            data = input("what do you want to write :-")
            fs.write(data)
            print("file created successfully")


def read_file():
    items = read_folder()
    for i in items:
        i = str(i)
        for j in i:
            if j == ".":
                print(i)
                break

    items = read_folder()
    for i in items:
        if p.is_file():
            print(i)

    name = input("which file you want to read :-")
    p = Path(name)
    if p.exists() and p.is_file():
        with open(p,"r") as fs:
            data = fs.read()
            print("\n\n\n you file content \n\n\n")
            print(data)
    else:
        print("no such file exists please try again")        



def update_file():
    items = read_folder()
    for i in items:
        p = Path(i)
        if p.is_file():
            print(i)

    name = input("Tell your file name :-")
    p = Path(name)
    if p.exists() and p.is_file():
        print("Choose one option ")
        print("press 1 to change the name")
        print("press 2 to overwrite file content")
        print("press 3 to append new content")


        res = int(input("tell your response : -"))

        if res == 1:
            new_name = input("tell new name with extension")
            new_p = Path(new_p)
            p.rename(new_p)
            print("file name changes successfully")

        elif res ==2:
            with open(p,"w") as fs:
                data = input("what do you want to overwrite:-")
                fs.write(data)
                print("overwritten successfully")

        elif res == 3:
            with open(p,"a") as fs:
                data = input("what do you want to Append:-")
                fs.write(data)
                print("Appended successfully")

def delete_file():
    items = read_folder()
    for i in items:
        p = Path(i)
        if p.is_file():
            print(i)
    name = input("tell your file name with extension :-") 
    p = Path(name)
    if p.exists() and p.is_file():
        os.remove(p)
    else:
        print("no such file exists please try again ")
        delete_file       


             



    





print("press 1 - for creating a folder")
print("press 2 - for read a folder")
print("press 3 - for updating a folder")
print("press 4 - for deleting a folder")
print("press 5 - for creating a file")
print("press 6 - for reading a file")
print("press 7 - for updating a file")
print("press 8 - for deleting a file")



res = int(input("Tell your respone :-"))

if res == 1:
    create_folder()

if res == 2:
    items = read_folder()
    for i in range(len(items)):
        print(f"{i+1} : {items[i]}")

if res == 3:
    update_folder()    

if res == 4:
    delete_folder()

if res == 5:
    create_file()    

if res == 6:
    read_file()

if res == 7:
    update_file()

if res == 8:
    delete_file()    

