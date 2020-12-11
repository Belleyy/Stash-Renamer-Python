import os
import sqlite3
import re
import subprocess
from pathlib import Path
import time
import progressbar

# Your sqlite path
dbpath = Path(r"C:\Users\Winter\.stash\Full.sqlite")
print("Path:",dbpath)

def gettingTagsID(name):
    sqlite_select_Tags = "SELECT id from tags WHERE name = '" + name + "';"
    cursor.execute(sqlite_select_Tags)
    result = cursor.fetchone()
    try:
        id = result[0]
        print(name+":", id)
    except:
        id = 'null'
        print("Error while getting: " + name)
    return str(id)

def get_SceneID_fromTags(id):
    sqlite_select_Query = "SELECT scene_id from scenes_tags WHERE tag_id = '" + id + "';"
    cursor.execute(sqlite_select_Query)
    record = cursor.fetchall()
    print("[SceneTags](ID"+id+") Total Rows:",len(record))
    array_ID=[]
    for row in record:
        array_ID.append(row[0])
    list=",".join(map(str,array_ID))
    return list

def get_Perf_fromScene(id_scene):
    perf_list=""
    cursor.execute("SELECT performer_id from performers_scenes WHERE scene_id =" + id_scene + ";")
    record = cursor.fetchall()
    print("Performer in scene: ",len(record))
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
    #print("Studio name: ",studio_name)
    return studio_name

try:
    sqliteConnection = sqlite3.connect(dbpath)
    cursor = sqliteConnection.cursor()
    print("Database successfully connected to SQLite")

    # The name of your tags
    id_tags = gettingTagsID('TAGS')
    print("\n")

    edit=0
    if (id_tags != "null"):
        # Get all ID (scenes) with the tags
        id_scene=get_SceneID_fromTags(id_tags)
        sqlite_select_Query = "SELECT id,path,title,date,studio_id from scenes WHERE id in (" + id_scene + ");"
        cursor.execute(sqlite_select_Query)
        record = cursor.fetchall()
        print("Total Rows: ", len(record))
        for i in progressbar.progressbar(range(len(record)), redirect_stdout=True):
            for row in record:
                scene_ID=str(row[0])
                scene_fullPath=str(row[1])
                scene_Directory = os.path.dirname(scene_fullPath)
                scene_Extension=os.path.splitext(scene_fullPath)[1]
                scene_Title=str(row[2])
                scene_Date=str(row[3])
                scene_Studio_id=str(row[4])

                print("ID: ",scene_ID)
                print("Path: ",scene_fullPath)
                print("Directory:",scene_Directory)
                print("Extension: ",scene_Extension)
                print("Title: ",scene_Title)
                print("Date: ",scene_Date)

                #  Look for duplicate title
                problem=0
                cursor.execute("SELECT path FROM scenes WHERE title='" + scene_Title.replace("'", "''") + "' AND NOT id='" + scene_ID + "';")
                duplicateCheck = cursor.fetchall()
                if (len(duplicateCheck) > 0):
                    for dupl_row in duplicateCheck:
                        if (os.path.dirname(str(dupl_row[0])) == scene_Directory):
                            print("Duplicate title detected!", file=open("output.txt", "a"))
                            print(scene_ID + " - " + scene_Title, file=open("output.txt", "a"))
                            print(os.path.dirname(str(dupl_row[0])) + " - " + scene_Directory, file=open("output.txt", "a"))
                            problem=1
                    if (problem == 1):
                        # Skip this file to avoid overwrite files
                        print("\n")
                        continue


                performer_name=get_Perf_fromScene(scene_ID)
                print("Performer name: ",performer_name)


                studio_name=get_Studio_fromID(scene_Studio_id)
                print("Studio name: ",studio_name)

                # Title + Extension
                newfilename = str(scene_Title + scene_Extension)

                # Date + Performer + Title
                #if not scene_Date: # Date is not set
                #    newfilename = str(performer_name + "- " + scene_Title + scene_Extension)
                #else:
                #    if (performer_name.isspace() or not performer_name): # Don't have performer
                #        newfilename = str(scene_Date  + " " + scene_Title + scene_Extension)
                #    else:
                #        newfilename = str(scene_Date + " " + performer_name + "- " + scene_Title + scene_Extension)

                #################################
            
                newfilename = re.sub('[\\/:"*?<>|#,]+', '', newfilename) #Remove illegal character for Windows (# and , is not illegal you can remove it)
                newpath = scene_Directory + "\\" + newfilename
                print("NewFilename: ",newfilename)
                print("NewPath: ",newpath)
                if (newpath == scene_fullPath):
                    print("Files already renamed (Db).")
                    print("\n")
                    continue
                else:
                    # THIS PART WILL EDIT YOUR DATABASE, FILES (be careful and know what you do)

                    # Windows Rename
                    if (os.path.isfile(scene_fullPath) == True):
                        os.rename(scene_fullPath,newpath)
                        if (os.path.isfile(newpath) == True):
                            print("File Renamed!", newpath)
                        else:
                            print("Error, rename doesn't work ?",newpath, file=open("output.txt", "a"))
                    else:
                        print("File don't exist in Explorer")

                    # Database rename
                    cursor.execute("UPDATE scenes SET path='" + newpath + "' WHERE id=" + scene_ID + ";")
                    edit+=1
                    if (edit > 10):
                        sqliteConnection.commit()
                        print("[Database] Update database!")
                        edit=0

                    # Rclone rename
                    #rclone_CURRENT=scene_fullPath.replace('H:','gdcrypt:').replace("\\","/")
                    #rclone_NEW=newpath.replace('H:','gdcrypt:').replace("\\","/")
                    #rclone_Process = subprocess.Popen(['rclone', 'moveto', rclone_CURRENT, rclone_NEW, '-v', '--log-file=C:\\Users\\Winter\\Documents\\RcloneLog.log'],shell=True)
                    #rclone_Process.communicate()
                    #print("\n")

    cursor.close()
except sqlite3.Error as error:
    print("Error while connecting to sqlite", error)
finally:
    if (sqliteConnection):
        sqliteConnection.commit()
        sqliteConnection.close()
        print("The SQLite connection is closed")
