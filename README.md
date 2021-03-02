# SQLITE Renamer for Stash
Using metadata from your database (SQLITE) to rename your file.

## Important
By doing this, you will make definitive change to your Database and Files!

## Requirement
- Python (Tested on Python v3.9.1 64bit, Win10)
- ProgressBar2 Module (https://github.com/WoLpH/python-progressbar)
- Stash Database (https://github.com/stashapp/stash)
- Windows 10 ? (No idea if this work for all OS)

## Usage
- I recommend make a copy of your database. (Use "backup" in Stash Settings)
- You need to set your Database path (Line 7)

## First Run
Set `USE_DRY` to True (Line 11), by doing this nothing will be changed.
- This will create a file `rename_dryrun.txt` that show how the path/file will be changed.
You can uncomment the break (Line 232), so it will stop after the first file.

## Filename template
Available: `$date` `$performer` `$title` `$studio` `$height`

The script will replace these field with the data from the database.
Exemple:
| Template        | Result           
| ------------- |:-------------:
$title|Her Fantasy Ball.mp4
$title $height|Her Fantasy Ball 1080p.mp4
$date $title|2016-12-29 Her Fantasy Ball.mp4
$date $performer - $title [$studio]|2016-12-29 Eva Lovia - Her Fantasy Ball [Sneaky Sex].mp4

## Function
| Function        | Description           
| ------------- |-------------
`gettingTagsID(tag_name)`|Return the ID of this tag.
`get_SceneID_fromTags(id)`|Return a list with all scenes ID that have this tags.


## Change scenes by tags

If you want differents formats by tags. Create a dict with `tag` (The name of the tag in Stash) & `filename` (Filename template)
```py
tags_dict = {
    '1': {
        'tag': '1. JAV',
        'filename': '$title'
    },
    '2': {
        'tag': '1. Anime',
        'filename': '$date $title'
    }
}

for _, dict_section in tags_dict.items():
    tag_name = dict_section.get("tag")
    filename_template = dict_section.get("filename")
    id_tags = gettingTagsID(tag_name)
    if id_tags is not None:
        id_scene = get_SceneID_fromTags(id_tags)
        option_sqlite_query = "WHERE id in ({})".format(id_scene)
        edit_db(filename_template,option_sqlite_query)
        print("====================")
```

If you only want change 1 tag:
```py
id_tags = gettingTagsID('1. JAV')
if id_tags is not None:
    id_scene = get_SceneID_fromTags(id_tags)
    option_sqlite_query = "WHERE id in ({})".format(id_scene)
    edit_db("$date $performer - $title [$studio]",option_sqlite_query)
```
## Change all scenes

```py
edit_db("$date $performer - $title [$studio]")
```

## Optionnal SQLITE

If you only want change a specific path, use the second parameter to `edit_db`, it will add it to the sqlite query. [(Documentation ?)](https://www.tutorialspoint.com/sqlite/sqlite_where_clause.htm)
Exemple (Only take file that have the path `E:\\Film\\R18`):
```py
option_sqlite_query = "WHERE path LIKE 'E:\\Film\\R18\\%'"
edit_db("$date $performer - $title [$studio]",option_sqlite_query)
```
