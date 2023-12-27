@echo off
setlocal enabledelayedexpansion

em Set the source folder path
set "currentDirectory=%CD%"

set "archiveFolder=%currentDirectory%"
set "rawFolder=!archiveFolder:\archive\=\raw\!"

rem Iterate over files in the destination folder
for %%F in ("%rawFolder%\*") do (
    rem Extract the file name without extension
    set "fileName=%%~nF"
    
    rem Build the source file path
    set "sourceFile=%archiveFolder%\texture.xbm"
    set "targetFile=%archiveFolder%\!fileName!.xbm"
    
    rem Check if the source file exists
    if not exist "!targetFile!" (
        rem Copy the source file to the destination folder with the same name
        copy "!sourceFile!" "!targetFile!"
    )
)

echo Done.
