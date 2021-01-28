import os
import sqlite3
import re
#import subprocess
from pathlib import Path
import progressbar

# Your sqlite path
dbpath = Path(r"C:\Users\Winter\.stash\Full.sqlite")
print("Path:",dbpath)

def get_Perf_fromSceneID(id_scene):
    perf_list=""
    cursor.execute("SELECT performer_id from performers_scenes WHERE scene_id =" + id_scene + ";")
    record = cursor.fetchall()
    print("Performer in scene: ",len(record))
    if len(record) > 3:
        print("More than 3 performers.")
    else:
        for row in record:
            cursor.execute("SELECT name from performers WHERE id =" + str(row[0]) + ";")
            perf = cursor.fetchall()
            #print("Name: ",perf[0][0])
            perf_list+=str(perf[0][0]) + " "
    return perf_list

def get_Studio_fromID(id):
    cursor.execute("SELECT name from studios WHERE id =" + id + ";")
    record = cursor.fetchall()
    studio_name=str(record[0][0])
    return studio_name

try:
    sqliteConnection = sqlite3.connect(dbpath)
    cursor = sqliteConnection.cursor()
    print("Database successfully connected to SQLite\n")
    edit=0
    sqlite_select_Query = "SELECT id,path,title,date,studio_id from scenes;"
    cursor.execute(sqlite_select_Query)
    record = cursor.fetchall()
    print("Total Rows: ", len(record))
    progressbar_Index = 0
    progress = progressbar.ProgressBar(redirect_stdout=True).start(len(record))
    for row in record:
        progress.update(progressbar_Index + 1)
        progressbar_Index+=1
        scene_ID=str(row[0])
        scene_fullPath=str(row[1])
        scene_Directory = os.path.dirname(scene_fullPath)
        scene_Extension=os.path.splitext(scene_fullPath)[1]
        scene_Title=str(row[2])
        scene_Date=str(row[3])
        scene_Studio_id=str(row[4])

        # By default, title contains extensions.
        scene_Title = re.sub(scene_Extension + '$', '', scene_Title)

        #  Look for duplicate title, if a other scene have same date and title it will skip it.
        cursor.execute("SELECT path FROM scenes WHERE title='" + scene_Title.replace("'", "''") + "' AND date='" + scene_Date + "' AND NOT id='" + scene_ID + "';")
        duplicateCheck = cursor.fetchall()
        if (len(duplicateCheck) > 0):
            problem=0
            for dupl_row in duplicateCheck:
                if (os.path.dirname(str(dupl_row[0])) == scene_Directory):
                    with open('output.txt', 'a') as f:
                        f.write('Duplicated title detected!\n')
                        f.write('{} - {}\n'.format(scene_ID, scene_Title))
                        f.write('{} - {}\n'.format(os.path.dirname(str(dupl_row[0])), scene_Directory))
                    problem=1
            if (problem == 1):
                print("\n")
                continue

        performer_name=get_Perf_fromSceneID(scene_ID)

        studio_name = ""
        if (scene_Studio_id and scene_Studio_id != "None"):
            studio_name=get_Studio_fromID(scene_Studio_id)

        # Date + Performer + Title + Studio (ex: 2016-12-29 Eva Lovia - Her Fantasy Ball [Sneaky Sex])
        newfilename=""
        if scene_Date:
            newfilename+=re.sub('\s+$', '', scene_Date)
        if performer_name:
            newfilename+=" " + re.sub('\s+$', '', performer_name)
        newfilename+=" - " + re.sub('\s+$', '', scene_Title)
        if studio_name != "":
            newfilename+=" [" + studio_name + "]"
        newfilename+=scene_Extension

        #Remove illegal character for Windows ('#' and ',' is not illegal you can remove it)
        newfilename = re.sub('[\\/:"*?<>|#,]+', '', newfilename) 
        newpath = scene_Directory + "\\" + newfilename
        if (newpath == scene_fullPath):
            #print("Files already renamed (Db).")
            #print("\n")
            continue
        else:
            print("ID: ",scene_ID)
            print("Path: ",scene_fullPath)
            print("Directory:",scene_Directory)
            print("Extension: ",scene_Extension)
            print("Title: ",scene_Title)
            print("Date: ",scene_Date)
            print("Studio ID: ",scene_Studio_id)
            print("Performer name: ",performer_name)
            print("Studio name: ",studio_name)
            print("-------------")
            print("OldFilename: ",os.path.basename(scene_fullPath)) # Get filename
            print("NewFilename: ",newfilename)
            print("NewPath: ",newpath)

            # 
            # THIS PART WILL EDIT YOUR DATABASE, FILES (be careful and know what you do)
            #
            # Windows Rename
            if (os.path.isfile(scene_fullPath) == True):
                os.rename(scene_fullPath,newpath)
                if (os.path.isfile(newpath) == True):
                    print("File Renamed!", newpath)
                    # Database rename
                    cursor.execute("UPDATE scenes SET path='" + newpath.replace("'", "''") + "' WHERE id=" + scene_ID + ";")
                    edit+=1
                    # I update the database every 10 files, you can change this number.
                    if (edit > 10):
                        sqliteConnection.commit()
                        print("[Database] Datebase Updated!")
                        edit=0
                else:
                    print("Error ?",newpath, file=open("output.txt", "a"))
            else:
                print("File don't exist in Explorer")
            print("\n")
        #break
    progress.finish()
    cursor.close()
except sqlite3.Error as error:
    print("SQLITE Error: ", error)
finally:
    if (sqliteConnection):
        sqliteConnection.commit()
        sqliteConnection.close()
        print("The SQLite connection is closed")
# Input if you want to check the console.
input("Press Enter to continue...")
