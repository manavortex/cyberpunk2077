@echo off
setlocal enabledelayedexpansion

set "currentDir=%~dp0"
set "rawDir=%currentDir:archive=raw%"

rem Loop through sibling directories
for /d %%D in ("%rawDir%..\*") do (
  if "%%~nxD" neq "%~nx0" (
    rem Loop through .ent.json files in the directory
    for %%F in ("%%D\*.ent.*") do (
        rem Replace occurrences of "arasaka_curtain" with the name of the directory
        set "filePath=%%~F"
        set "fileName=%%~nF"
        set "directoryName=%%~nxD"
        powershell -Command "(Get-Content '%%~F') | ForEach-Object { $_ -replace 'arasaka_curtain', '%%~nxD' } | Set-Content '%%~F'"
    )

    rem Loop through .app.json files in the directory
    for %%F in ("%%D\*.app.*") do (
        rem Replace occurrences of "arasaka_curtain" with the name of the directory
        set "filePath=%%~F"
        set "fileName=%%~nF"
        set "directoryName=%%~nxD"
        powershell -Command "(Get-Content '%%~F') | ForEach-Object { $_ -replace 'arasaka_curtain', '%%~nxD' } | Set-Content '%%~F'"
        REM move /y "!filePath!.temp" "!filePath!"
    )
  )
)

endlocal
