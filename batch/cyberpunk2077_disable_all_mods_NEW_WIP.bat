@ECHO OFF
setlocal enabledelayedexpansion

REM ===================================================================================================================
REM helper script for troubleshooting: https://wiki.redmodding.org/cyberpunk-2077-modding/help/users-troubleshooting
REM Up-to-date with 2.1.1, but this won't go bad
REM -------------------------------------------------------------------------------------------------------------------
REM Debug mode?
set DEBUG_MODE=0
REM ===================================================================================================================

REM for indenting user output
set "tab=    "
set separator=--------------------------------------------------------------------------------------------------------

if "%~1" == "" (
  pushd "%~dp0"
  set "CYBERPUNKDIR=!CD!"
  popd
) else (
  set param=%*
  :: remove potential quotes from string
  set param=!param:"=!
  set "CYBERPUNKDIR=!param!"
)

REM ==================================================================
REM Make sure that we're in the cyberpunk directory
REM yell at user if we aren't
REM ==================================================================

REM make sure that we're inside the cyberpunk dir
if not exist "!CYBERPUNKDIR!\bin\x64\Cyberpunk2077.exe" (
  echo.
  echo !separator!
  echo !tab!File not found !CYBERPUNKDIR!\bin\x64\Cyberpunk2077.exe
  echo !tab!Either start this script in your Cyberpunk 2077 folder,
  echo !tab!or drag and drop it from Windows Explorer on this file.
  echo.
  echo !tab!Aborting...
  echo !separator!
  pause
  goto :eof
)


REM Create directory for backups
if not exist "!CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS" (
  mkdir "!CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS"
)

REM Initialize counter variable
set /a count=0

REM Count the number of subdirectories
for /f %%i in ('dir /b /ad "!CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS" 2^>nul ^| find /c /v ""') do set count=%%i

REM Check if the count is greater than 5
if %count% gtr 5 (
    call :delete_old_backups
) 

set TIMESTAMP=
REM Get timestamped string using PowerShell and store it in a variable
for /f %%i in ('powershell Get-Date -Format "yyyy-MM-dd_HH-mm-ss"') do set "TIMESTAMP=%%i"

set "BACKUP_DIRECTORY=!CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS\!TIMESTAMP!"
if exist "!BACKUP_DIRECTORY!" (
  move "!BACKUP_DIRECTORY!" "!BACKUP_DIRECTORY!_old"
)
mkdir "!BACKUP_DIRECTORY!"

set "LOGFILE=!BACKUP_DIRECTORY!\disable_all_mods.txt"

if not exist "!LOGFILE!" (
    echo. > "!LOGFILE!"
) else (
    break > "!LOGFILE!"
)

REM =================================================================
REM the files that we want to remove/rename
REM =================================================================

REM set "rename_paths=archive\pc\mod mods bin\x64\plugins r6\scripts r6\tweaks red4ext engine\tools engine\config\platform\pc"
REM set "delete_paths=bin\x64\d3d11.dll bin\x64\global.ini bin\x64\powrprof.dll bin\x64\winmm.dll bin\x64\version.dll engine\config\base engine\config\galaxy engine\config\base
REM engine\tools r6\cache r6\config r6\inputs V2077"

set "rename_paths=archive\pc\mod mods bin\x64\plugins r6\scripts r6\tweaks red4ext engine\tools engine\config\platform\pc bin\x64\d3d11.dll bin\x64\global.ini bin\x64\powrprof.dll bin\x64\winmm.dll bin\x64\version.dll engine\config\base engine\config\galaxy engine\config\base engine\tools r6\cache r6\config r6\inputs"

REM some folders are outdated and ancient and you should NOT have them.
set "delete_paths=V2077"


REM =================================================================
REM do the actual work: move files and folders to backup dir
REM =================================================================

REM pop them in an array for proper iterating
set numRenamedFiles=0
set "renamed_paths_list="

for %%P in (%rename_paths%) do (    
  call :backup_file_or_folder %%~P
)

REM pop them in an array for proper iterating
set numDeletedFiles=0
set "deleted_paths_list="

for %%P in (!delete_paths!) do (  
  set "absolute_path=!CYBERPUNKDIR!\%%~P"
  if exist "!absolute_path!" (
	set /A numDeletedFiles+=1
	set deleted_paths_list[!numDeletedFiles!]=%%~P
	if exist !absolute_path!\* (
		rd /s /q !absolute_path!
	  ) else (      
	   del /f /q !absolute_path!
	  )
  )
)

REM now that we're done deleting, make sure that r6\cache\modded exist to prevent file access errors
if not exist "!CYBERPUNKDIR!\r6\cache" (
  mkdir "!CYBERPUNKDIR!\r6\cache"
)
if not exist "!CYBERPUNKDIR!\r6\cache\modded" (
  mkdir "!CYBERPUNKDIR!\r6\cache\modded"
)

REM =================================================================
REM show user feedback
REM =================================================================

if (!numRenamedFiles!) gtr (0) (
  echo. >> "!LOGFILE!"
  echo Your installation has been reset. Your mods and settings have been backed up to !BACKUP_DIRECTORY!: >> "!LOGFILE!"
  echo !separator! >> "!LOGFILE!"
  for /L %%i in (1,1,%numRenamedFiles%) do echo !tab!!renamed_paths_list[%%i]! >> "!LOGFILE!"
  echo.
) else (
  echo. >> "!LOGFILE!"
  echo !separator! >> "!LOGFILE!"
  echo !tab!Your installation has been reset. >> "!LOGFILE!"
)


if (!numDeletedFiles!) gtr (0) (
  echo The following outdated files were deleted: >> "!LOGFILE!"
  echo !separator! >> "!LOGFILE!"
  for /L %%i in (1,1,%numDeletedFiles%) do echo !tab!!deleted_paths_list[%%i]! >> "!LOGFILE!"
  echo. >> "!LOGFILE!"
)

echo !separator! >> "!LOGFILE!
echo. >> "!LOGFILE!"
echo .


echo You can find the full list in !LOGFILE!
echo For further help, check https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-users/user-guide-troubleshooting#a-fresh-install-starting-from-scratch
echo .
echo " !separator! "
echo "                 _  __                                                                                    "
echo " /\   /\___ _ __(_)/ _|_   _   _   _  ___  _   _ _ __    __ _  __ _ _ __ ___   ___   _ __   _____      __ "
echo " \ \ / / _ \ '__| | |_| | | | | | | |/ _ \| | | | '__|  / _` |/ _` | '_ ` _ \ / _ \ | '_ \ / _ \ \ /\ / / "
echo "  \ V /  __/ |  | |  _| |_| | | |_| | (_) | |_| | |    | (_| | (_| | | | | | |  __/ | | | | (_) \ V  V /  "
echo "   \_/ \___|_|  |_|_|  \__, |  \__, |\___/ \__,_|_|     \__, |\__,_|_| |_| |_|\___| |_| |_|\___/ \_/\_/   "
echo "                       |___/   |___/                    |___/                                             "
echo " !separator! "
echo .

pause

explorer !BACKUP_DIRECTORY!

goto :eof


:backup_file_or_folder
	set "relative_path=%*"

	set "source=!CYBERPUNKDIR!\!relative_path!"
	set "dest=!BACKUP_DIRECTORY!\!relative_path!"
	
	if not exist "!source!" goto :eof
			
	REM Check if the source is a directory
	if exist "!source!\*" (
		REM Use powershell to recursively copy directory because it doesn't suck
		powershell.exe -Command "Copy-Item -Path '!source!' -Destination '!dest!' -Recurse -Force"
		
		if "!DEBUG_MODE!"=="1" goto :log_file_operation	
		
		REM delete directory and create an empty folder
		rd /s /q "!source!"
		mkdir "!source!"
	) else (	
		REM Create the destination directory if needed
		if not exist "!dest!\.." (
			mkdir "!dest!"
		)
		powershell.exe -Command "Copy-Item -Path '!source!' -Destination '!dest!' -Force"		
		if "!DEBUG_MODE!"=="1" goto :log_file_operation	
		
		del /f /q "!source!"
	)

	REM no goto eof here, we want to run through this even without goto 
	
	:log_file_operation
		REM append it to array so we can print it later
		set /A numRenamedFiles+=1
		set renamed_paths_list[!numRenamedFiles!]=!relative_path!
		goto :eof


:delete_old_backups

	echo You have more than 5 old mod remover backups under !CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS.	
	echo You really should delete them before your disk runs full.
	set /p user_input="Delete files now? [Y] "
	
	if /i not "%user_input%"=="Y" goto :eof 
	
	echo.
	echo !separator!
	echo Script will delete your old backups now. Last chance to back them up!
	echo.
	pause
	for /d %%i in ("!CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS\*") do (
		rd /s /q "%%i"
	)
	goto :eof
		

endlocal
