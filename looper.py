#Loops through folders inside a root path and runs a .py script on each of the folders. Each folder represents a single subject with subject data inside.
#By: Ahmed Elbokl, 2021

#SETUP -------------------------------------------------------------------------------------------------------------------------------------------------------

#FULL root path containing all the subject folders
root_path = 'E:\Dropbox\Programming\Python\Preprocessing\subjects'

#FULL path of the .py script you want to run on each subject folder
script = 'E:\Dropbox\Programming\Python\Preprocessing\preprocessing.py'

#Target Tag (If this tag is found in subject folder name, the script will run on that folder. Leave empty '' to run on all folders) e.g 'DO'
target_tag = ''

#Exclude Tag (If this tag is found in subject folder name, the script will not run on that folder. Leave empty '' to exclude nothing) e.g 'bad'
exclude_tag = 'bad'

#END SETUP ---------------------- Do not change code below this line unless you know what you're doing -------------------------------------------------------

import os

#change to root path
os.chdir(root_path)

#get list of folders in current working directory (exluding files)
folders = [f for f in os.listdir() if os.path.isdir(f)]

#If target tag is not empty, only run on folders with target tag
if target_tag != '':
    folders = [f for f in folders if target_tag.lower() in f.lower()]

#If exclude tag is not empty, exclude folders with exclude tag
if exclude_tag != '':
    folders = [f for f in folders if exclude_tag.lower() not in f.lower()]

#Check is folders is empty and if so, exit
if len(folders) == 0:
    print('## No folders to work on in root path ##')
    exit()

#Start the loop
print('Initiating Looper on root path:', root_path)

#loop through folders
for folder in folders:
    
    #set current working directory to folder
    os.chdir(folder)

    #print current folder
    print('--------------------------------------------------------')
    print('Running script on: ' + folder)
    print('--------------------------------------------------------')

    #run the script
    os.system('python ' + script)

    #script finished on this folder
    print('Script done on: ' + folder)

    #return to root directory
    os.chdir(root_path)

#End of loop
print('--------------------------------------------------------')
print('Looper ended')
print('--------------------------------------------------------')
