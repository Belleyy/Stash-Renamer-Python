import os
import sqlite3
import re
from pathlib import Path
import progressbar

# Your sqlite path
dbpath = r"C:\Users\Winter\.stash\Full.sqlite"
print("Path:", dbpath)


def gettingTagsID(name):
    cursor.execute("SELECT id from tags WHERE name=?;", [name])
    result = cursor.fetchone()
    try:
        id = str(result[0])
        print("Tag: {} [{}]".format(name,id))
    except:
        id = None
        print("Error when trying to get:{}".format(name))
    return id


def get_SceneID_fromTags(id):
    cursor.execute("SELECT scene_id from scenes_tags WHERE tag_id=?;", [id])
    record = cursor.fetchall()
    print("There is {} scene(s) with the tag_id {}".format(len(record),id))
    array_ID = []
    for row in record:
        array_ID.append(row[0])
    list = ",".join(map(str, array_ID))
    return list


def get_Perf_fromSceneID(id_scene):
    perf_list = ""
    cursor.execute(
        "SELECT performer_id from performers_scenes WHERE scene_id=?;", [id_scene])
    record = cursor.fetchall()
    #print("Performer in scene: ", len(record))
    if len(record) > 3:
        print("More than 3 performers.")
    else:
        for row in record:
            perf_id = str(row[0])
            cursor.execute(
                "SELECT name from performers WHERE id=?;", [perf_id])
            perf = cursor.fetchall()
            perf_list += str(perf[0][0]) + " "
    perf_list = perf_list.strip()
    return perf_list


def get_Studio_fromID(id):
    cursor.execute("SELECT name from studios WHERE id=?;", [id])
    record = cursor.fetchall()
    studio_name = str(record[0][0])
    return studio_name


def makeFilename(scene_information, query):
    # Date + Performer + Title + Studio (ex: 2016-12-29 Eva Lovia - Her Fantasy Ball [Sneaky Sex])
    # query = "$date $performer - $title [$studio]"
    new_filename = str(query)
    if "$date" in new_filename:
        if scene_information.get('date') == "":
            new_filename = re.sub('\$date\s*', '', new_filename)
        else:
            new_filename =new_filename.replace("$date", scene_information.get('date'))

    if "$performer" in new_filename:
        if scene_information.get('performer') == "":
            new_filename = re.sub('\$performer\s*', '', new_filename)
        else:
            new_filename = new_filename.replace("$performer", scene_information.get('performer'))

    if "$title" in new_filename:
        if scene_information.get('title') == "":
            new_filename = re.sub('\$title\s*', '', new_filename)
        else:
            new_filename = new_filename.replace("$title", scene_information.get('title'))

    if "$studio" in new_filename:
        if scene_information.get('studio') == "":
            new_filename = re.sub('\[\$studio\]', '', new_filename)
            new_filename = re.sub('\$studio\s*', '', new_filename)
        else:
            new_filename = new_filename.replace("$studio", scene_information.get('studio'))

    return new_filename


def edit_db(query, queryfilename):
    cursor.execute(query)
    record = cursor.fetchall()
    print("Scenes numbers: {}".format(len(record)))
    edit = 0
    progressbar_Index = 0
    progress = progressbar.ProgressBar(redirect_stdout=True).start(len(record))
    for row in record:
        progress.update(progressbar_Index + 1)
        progressbar_Index += 1
        scene_ID = str(row[0])
        scene_fullPath = str(row[1])
        scene_Directory = os.path.dirname(scene_fullPath)
        scene_Extension = os.path.splitext(scene_fullPath)[1]
        scene_Title = str(row[2])
        scene_Date = str(row[3])
        scene_Studio_id = str(row[4])

        # By default, title contains extensions.
        scene_Title = re.sub(scene_Extension + '$', '', scene_Title)

        #  Look for duplicate title, if a other scene have same date and title it will skip it.
        cursor.execute("SELECT path FROM scenes WHERE title=? AND date=? AND NOT id=?;", [scene_Title, scene_Date, scene_ID])
        duplicateCheck = cursor.fetchall()
        if (len(duplicateCheck) > 0):
            problem = 0
            for dupl_row in duplicateCheck:
                if (os.path.dirname(str(dupl_row[0])) == scene_Directory):
                    with open('output.txt', 'a', encoding='utf-8') as f:
                        f.write('Duplicated title detected!\n')
                        f.write('{} - {}\n'.format(scene_ID, scene_Title))
                        f.write('{} - {}\n'.format(os.path.dirname(str(dupl_row[0])), scene_Directory))
                        problem = 1
            if (problem == 1):
                print("\n")
                continue

        performer_name = get_Perf_fromSceneID(scene_ID)

        studio_name = ""
        if (scene_Studio_id and scene_Studio_id != "None"):
            studio_name = get_Studio_fromID(scene_Studio_id)

        scene_information = {
            "title": scene_Title,
            "date": scene_Date,
            "performer": performer_name,
            "studio": studio_name
        }

        newfilename = makeFilename(scene_information, queryfilename) + scene_Extension

        # Remove illegal character for Windows ('#' and ',' is not illegal you can remove it)
        newfilename = re.sub('[\\/:"*?<>|#,]+', '', newfilename)
        newpath = scene_Directory + "\\" + newfilename
        if len(newpath) > 240:
            print("The Path is too long...\n", newpath)
            reducePath = len(scene_Directory) + len(scene_Date) + len(scene_Title) + len(scene_Extension) + 3
            if reducePath < 240:
                newpath = scene_Directory + "\\" + \
                    makeFilename(scene_information,"$date - $title") + scene_Extension
                print("Reducing path to: ", newpath)
        if (newpath == scene_fullPath):
            #print("Files already renamed (Db).\n")
            continue
        else:
            #print("ID: ", scene_ID)
            #print("Path: ", scene_fullPath)
            #print("Directory:", scene_Directory)
            #print("Extension: ", scene_Extension)
            #print("Title: ", scene_Title)
            #print("Date: ", scene_Date)
            #print("Studio ID: ", scene_Studio_id)
            #print("Performer name: ", performer_name)
            #print("Studio name: ", studio_name)
            #print("-------------")
            print("OldFilename: ", os.path.basename(scene_fullPath))  # Get filename
            print("NewFilename: ", newfilename)
            print("NewPath: ", newpath)

            #
            # THIS PART WILL EDIT YOUR DATABASE, FILES (be careful and know what you do)
            #
            # Windows Rename
            if (os.path.isfile(scene_fullPath) == True):
                os.rename(scene_fullPath, newpath)
                if (os.path.isfile(newpath) == True):
                    print("File Renamed!", newpath)
                    # Database rename
                    cursor.execute("UPDATE scenes SET path=? WHERE id=?;", [newpath, scene_ID])
                    edit += 1
                    # I update the database every 10 files, you can change this number.
                    if (edit > 10):
                        sqliteConnection.commit()
                        print("[Database] Datebase Updated!")
                        edit = 0
                else:
                    print("File failed to rename ?\n{}".format(newpath), file=open("output.txt", "a", encoding='utf-8'))
            else:
                print("File don't exist in Explorer")
            print("\n")
        # break
    progress.finish()
    sqliteConnection.commit()
    return


try:
    sqliteConnection = sqlite3.connect(dbpath)
    cursor = sqliteConnection.cursor()
    print("Python successfully connected to SQLite\n")
except sqlite3.Error as error:
    print("FATAL SQLITE Error: ", error)
    input("Press Enter to continue...")
    exit(1)

# Scene with Specific Tags
id_tags_JAV = gettingTagsID('1. JAV')
if id_tags_JAV is not None:
    id_scene_JAV = get_SceneID_fromTags(id_tags_JAV)
    sqlite_query = "SELECT id,path,title,date,studio_id from scenes WHERE id in ({}) AND path LIKE 'E:\\Film\\R18\\%';".format(
        id_scene_JAV)
    # E.g.: $title == SSNI-000.mp4
    edit_db(sqlite_query, "$title")

id_tags_Anime = gettingTagsID('1. Anime')
if id_tags_Anime is not None:
    id_scene_Anime = get_SceneID_fromTags(id_tags_Anime)
    sqlite_query = "SELECT id,path,title,date,studio_id from scenes WHERE id in ({}) AND path LIKE 'E:\\Film\\R18\\%';".format(
        id_scene_Anime)
    # E.g.: $date $title == 2017-04-27 Oni Chichi.mp4
    edit_db(sqlite_query, "$date $title")

id_tags_Western = gettingTagsID('1. Western')
if id_tags_Western is not None:
    id_scene_Western = get_SceneID_fromTags(id_tags_Western)
    sqlite_query = "SELECT id,path,title,date,studio_id from scenes WHERE id in ({}) AND path LIKE 'E:\\Film\\R18\\%';".format(
        id_scene_Western)
    # E.g.: $date $performer - $title [$studio] == 2016-12-29 Eva Lovia - Her Fantasy Ball [Sneaky Sex].mp4
    edit_db(sqlite_query, "$date $performer - $title [$studio]")

# Select ALL scenes
#sqlite_query = "SELECT id,path,title,date,studio_id from scenes;"
#edit_db(sqlite_query,"$date $performer - $title [$studio]")

sqliteConnection.commit()
cursor.close()
sqliteConnection.close()
print("The SQLite connection is closed")
# Input if you want to check the console.
input("Press Enter to continue...")
