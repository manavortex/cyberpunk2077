@ECHO OFF
setlocal enabledelayedexpansion

REM helper script for troubleshooting: https://wiki.redmodding.org/cyberpunk-2077-modding/help/users-troubleshooting
REM Up-to-date with 1.6.3_hotfix after the DLSS patch

REM for indenting user output
set "tab=    "
set separator=--------------------------------------------------------------------------------------------------------

REM ==================================================================
REM Make sure that we're in the cyberpunk directory
REM yell at user if we aren't
REM ==================================================================

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

pushd "!CYBERPUNKDIR!"


REM make sure that we're inside the cyberpunk dir
if not exist ".\bin\x64\Cyberpunk2077.exe" (
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
if not exist ".\_MOD_REMOVER_BACKUPS" (
  mkdir ".\_MOD_REMOVER_BACKUPS"
)

REM Initialize counter variable
set /a count=0

REM Count the number of subdirectories
for /f %%i in ('dir /b /ad ".\_MOD_REMOVER_BACKUPS" 2^>nul ^| find /c /v ""') do set count=%%i

REM Check if the count is greater than 5
if %count% gtr 5 (
    call :delete_old_backups
) 

set TIMESTAMP=
for /f "tokens=1-5 delims=/: " %%d in ("%date% %time%") do (
    set TIMESTAMP=%%d_%%e_%%f_%%g_%%h
)

set "BACKUP_DIRECTORY=.\_MOD_REMOVER_BACKUPS\!TIMESTAMP!"
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
	set "absolute_source=.\%%~P"
	set "absolute_dest=.\!BACKUP_DIRECTORY!\%%~P"
    
    if exist "!absolute_source!" (
        REM Check if the source is a directory
        if exist "!absolute_source!\." (
            REM Move directory and create the destination directory structure if needed
			robocopy "!absolute_source!" "!absolute_dest!" /E /MOVE /CREATE /njh /njs /ndl /nc /ns > nul		
			if not exist "!absolute_source!" (
				mkdir "!absolute_source!"
			)
        ) else (
            REM Move file and create the destination directory if needed
            mkdir "!BACKUP_DIRECTORY!\%%~P\.."
            move "!absolute_source!" "!absolute_dest!"
        )
    )
	REM append it to array so we can print it later
	set /A numRenamedFiles+=1
	set renamed_paths_list[!numRenamedFiles!]=%%~P
)

REM pop them in an array for proper iterating
set numDeletedFiles=0
set "deleted_paths_list="

for %%P in (!delete_paths!) do (  
  set "absolute_path=.\%%~P"
  if exist "!absolute_path!" (
	set /A numDeletedFiles+=1
	set deleted_paths_list[!numDeletedFiles!]=%%~P
	call :delete_file_or_folder_without_prompt "!absolute_path!"
  )
)

REM now that we're done deleting, make sure that r6\cache\modded exist to prevent file access errors
if not exist ".\r6\cache" (
  mkdir ".\r6\cache"
)
if not exist ".\r6\cache\modded" (
  mkdir ".\r6\cache\modded"
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
  echo The following files were deleted: >> "!LOGFILE!"
  echo !separator! >> "!LOGFILE!"
  for /L %%i in (1,1,%numDeletedFiles%) do echo !tab!!deleted_paths_list[%%i]! >> "!LOGFILE!"
  echo. >> "!LOGFILE!"
)

echo !separator! >> "!LOGFILE
echo. >> "!LOGFILE!"
echo .


echo You can find this output in !LOGFILE!
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

popd
goto :eof

  
:delete_file_or_folder_without_prompt
  set "file=%*"
  if not exist !file! goto :eof
  
  if exist !file!\* (
    rd /s /q !file!
  ) else (      
   del /f /q !file!
  )
  goto :eof  

:delete_old_backups

	echo You have more than 5 old mod remover backups under !CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS.	
		echo You really should delete them before your disk runs full.
		set /p user_input="Delete files now? [Y] "
		if /i not "%user_input%"=="Y" goto :eof 
		
		echo.
		echo !separator!
		echo Script will delete your old backups now. Last chance to copy them!
		echo.
		pause
		for /d %%i in ("!CYBERPUNKDIR!\_MOD_REMOVER_BACKUPS\*") do (
			rd /s /q "%%i"
		)
		goto :eof
		

endlocal