@echo off
setlocal enabledelayedexpansion

rem Get the path of the current directory
set "currentDir=%~dp0"

rem Get the name of the "arasaka_curtain.mesh" file
set "sourceFile=%currentDir%arasaka_curtain.mesh"

rem Loop through sibling directories
for /d %%D in ("%currentDir%..\*") do (
    rem Check if the directory contains a file ending in ".mesh"
    if exist "%%D\*.mesh" (
        rem Overwrite the existing ".mesh" file with "arasaka_curtain.mesh"
        copy /y "!sourceFile!" "%%D\%%~nD.mesh"
        echo Overwritten "%%D\%%~nD.mesh" with "arasaka_curtain.mesh"
    )
)

endlocal
