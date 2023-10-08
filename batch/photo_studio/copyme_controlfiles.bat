@echo off
setlocal enabledelayedexpansion

rem Get the path of the current directory
set "currentDir=%~dp0"

rem Get the name of the "arasaka_curtain.mesh" file
set "sourceEnt=%currentDir%_arasaka_curtain.ent"
set "sourceApp=%currentDir%_arasaka_curtain.app"

rem Loop through sibling directories
for /d %%D in ("%currentDir%..\*") do (
    if "%%~nxD" neq "%~nx0" (
      rem Check if the directory contains a file ending in ".ent"
      if exist "%%D\*.ent" (
          copy /y "!sourceEnt!" "%%D\_%%~nD.ent"
          echo Overwritten "%%D\_%%~nD.ent" with "_arasaka_curtain.ent"
      )
      rem Check if the directory contains a file ending in ".app"
      if exist "%%D\*.app" (
          copy /y "!sourceApp!" "%%D\_%%~nD.app"
          echo Overwritten "%%D\_%%~nD.app" with "_arasaka_curtain.app"
      )
    )
)

endlocal
