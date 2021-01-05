# SQLITE Renamer for Stash
Use your database (Sqlite) to rename file in Windows.

## Important
By doing this, you will make definitive change to your Database and Files!

## Requirement
- Python (Tested on Python v3.9.1 64bit, Win10)
- ProgressBar2 Module (https://github.com/WoLpH/python-progressbar)
- Stash Database (https://github.com/stashapp/stash)

## Usage
- I recommend make a copy of your database.
- You need to set your Database path (Line 9)

## First Run
I recommend to comment action (`os.rename(scene_fullPath,newpath)` and `sqliteConnection.commit()`), by doing this nothing will be edited.

You can uncomment the break (Line 139), so it will stop after the first file.

You can look into the console to see if this work correctly for you.

## Other things

If you want to only select scene with a certain tag, you can take a look at this [old version](https://github.com/Belleyy/Stash-Renamer-Python/blob/7ac97cd2c81767628b2011778c58feeae1267423/RenameFilesTags.py).
