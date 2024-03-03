#!/bin/bash

# ===================================================================================================================
# helper script for troubleshooting: https://wiki.redmodding.org/cyberpunk-2077-modding/help/users-troubleshooting
# Up-to-date with 2.1.1
# -------------------------------------------------------------------------------------------------------------------
# Debug mode?
DEBUG_MODE=0
HEADLESS=
# ===================================================================================================================

# for indenting user output
tab="    "
separator="--------------------------------------------------------------------------------------------------------"

CYBERPUNKDIR=$(pwd)

# check if headless was in the parameters
for i in "$@"; do
    if [ "$i" = "headless" ]; then
        HEADLESS=1
    fi
done

# ==================================================================
# Make sure that we're in the cyberpunk directory
# yell at user if we aren't
# ==================================================================

# make sure that we're inside the cyberpunk dir
if [ ! -f "$CYBERPUNKDIR/bin/x64/Cyberpunk2077.exe" ]; then
  if [ "$HEADLESS" = "1" ]; then exit 1; fi
  
  echo
  echo $separator
  echo "$tab""File not found $CYBERPUNKDIR/bin/x64/Cyberpunk2077.exe"
  echo "$tab""Please start this script directly from your Cyberpunk 2077 game directory!"
  echo
  echo "$tab""Aborting..."
  echo $separator
 
  read -r -p "Press any key to continue . . . " -n1 -s
  exit
fi

# Create directory for backups
if [ ! -d "$CYBERPUNKDIR/_MOD_REMOVER_BACKUPS" ]; then
  mkdir "$CYBERPUNKDIR/_MOD_REMOVER_BACKUPS"
fi

# Initialize counter variable
count=$(find "$CYBERPUNKDIR/_MOD_REMOVER_BACKUPS" -mindepth 1 -maxdepth 1 -type d | wc -l)

# Check if the count is greater than 5
if [ $count -gt 5 ]; then
  if [ "$HEADLESS" != "1" ]; then delete_old_backups; fi
fi 

# shellcheck disable=SC2317
delete_old_backups() {

	echo "You have more than 5 old mod remover backups under $CYBERPUNKDIR/_MOD_REMOVER_BACKUPS."
	echo "You really should delete them before your disk runs full."
	read -r -p "Should ModRemover auto-delete the files for you? (Only if you type [Y]) " user_input
	
	if [ "$user_input" != "Y" ]; then return; fi 
	
	echo
	echo "$separator"
	echo "Script will delete your old backups now. Last chance to back them up!"
	echo
	read -r -p "Press any key to continue . . . " -n1 -s

	find "$CYBERPUNKDIR/_MOD_REMOVER_BACKUPS" -mindepth 1 -maxdepth 1 -type d -print0 | xargs rm -rf
}

TIMESTAMP=$(date +"%Y-%m-%d_%H-%M-%S")

BACKUP_DIRECTORY="$CYBERPUNKDIR/_MOD_REMOVER_BACKUPS/$TIMESTAMP"
if [ -d "$BACKUP_DIRECTORY" ]; then
  mv "$BACKUP_DIRECTORY" "$BACKUP_DIRECTORY"_old
fi
mkdir "$BACKUP_DIRECTORY"

LOGFILE="$BACKUP_DIRECTORY/disable_all_mods.txt"

if [ ! -f "$LOGFILE" ]; then
    touch "$LOGFILE"
else
    > "$LOGFILE"
fi

if [ "$HEADLESS" = "1" ]; then
	if [ $? -ne 0 ]; then exit 1; fi
fi

# =================================================================
# the files that we want to remove/rename
# =================================================================
rename_paths=("archive/pc/mod" "mods" "bin/x64/plugins" "r6/scripts" "r6/tweaks" "red4ext" "engine/tools" "engine/config/platform/pc" "bin/x64/d3d11.dll" "bin/x64/global.ini" "bin/x64/powrprof.dll" "bin/x64/winmm.dll" "bin/x64/version.dll" "engine/config/base" "engine/config/galaxy" "engine/config/base" "engine/tools" "r6/cache" "r6/config" "r6/input")

# some folders are outdated and ancient and you should NOT have them.
delete_paths=("V2077")

# =================================================================
# do the actual work: move files and folders to backup dir
# =================================================================

# pop them in an array for proper iterating
numRenamedFiles=0
renamed_paths_list=()

relative_path=""
log_file_operation() {
		# append it to array so we can print it later
		numRenamedFiles=$((numRenamedFiles+1))
		renamed_paths_list+=("$relative_path")
}

backup_file_or_folder() {
	relative_path=$1

	source="$CYBERPUNKDIR/$relative_path"
	dest="$BACKUP_DIRECTORY/$relative_path"
	
	if [ ! -e "$source" ]; then return; fi
			
	if [ ! -f "$source" ]; then return; fi
			

	# Check if the source is a directory
	if [ -d "$source" ]; then

		# Create the destination directory if needed
		[ ! -d "$(dirname "$dest")" ] && mkdir -p "$(dirname "$dest")"

		cp -r "$source" "$dest"
		
		if [ "$DEBUG_MODE" = "1" ]; then log_file_operation; fi
		
		# delete directory and create an empty folder
		rm -rf "$source"
		mkdir "$source"
		log_file_operation	
		return
	fi

	if [ -f "$source" ]; then
		# Create the destination directory if needed
		[ ! -d "$(dirname "$dest")" ] && mkdir -p "$(dirname "$dest")"

		cp "$source" "$dest"
		
		if [ "$DEBUG_MODE" = "1" ]; then log_file_operation; fi
		
		rm -f "$source"	
		log_file_operation	
		return
	fi
}


for P in "${rename_paths[@]}"; do
  backup_file_or_folder "$P"
done

# pop them in an array for proper iterating
numDeletedFiles=0
deleted_paths_list=()

for P in "${delete_paths[@]}"; do
  relative_path=$P
  absolute_path="$CYBERPUNKDIR/$relative_path"
  if [ -e "$absolute_path" ]; then
	numDeletedFiles=$((numDeletedFiles+1))
	deleted_paths_list+=("$relative_path")
	if [ -d "$absolute_path" ]; then
		rm -rf "$absolute_path"
	else
		rm -f "$absolute_path"
	fi
  fi
done

if [ "$HEADLESS" = "1" ]; then
	if [ $? -ne 0 ]; then exit 1; fi
fi

# =================================================================
# show user feedback
# =================================================================

if [ $numRenamedFiles -gt 0 ]; then
  {
	echo "";
	echo "Your installation has been reset. Your mods and settings have been backed up to $BACKUP_DIRECTORY:";
  	echo "$separator";
	for i in "${renamed_paths_list[@]}"; do echo "$tab$i"; done
  } >> "$LOGFILE"
else
  {
	echo ""
  	echo $separator
  	echo "$tab""Your installation has been reset." 
  } >> "$LOGFILE"
fi

if [ $numDeletedFiles -gt 0 ]; then
  {
	echo "";
	echo "The following outdated files were deleted:";
  	echo "$separator";
	for i in "${deleted_paths_list[@]}"; do echo "$tab$i"; done
	echo "";
  } >> "$LOGFILE"
fi

echo $separator >> "$LOGFILE"
echo >> "$LOGFILE"

if [ "$HEADLESS" = "1" ]; then
	exit
fi

echo
echo
echo "Your installation has been reset:"
echo "All modded and potentially-modded files were moved to"
echo "$tab$BACKUP_DIRECTORY"
echo
echo "You can find the full list of files in $LOGFILE"
echo
echo "For further help, check https://wiki.redmodding.org/cyberpunk-2077-modding/for-mod-users/user-guide-troubleshooting#a-fresh-install-starting-from-scratch"
echo
echo " $separator "
echo "                 _  __                                                                                    "
echo " /\   /\___ _ __(_)/ _|_   _   _   _  ___  _   _ _ __    __ _  __ _ _ __ ___   ___   _ __   _____      __ "
echo " \ \ / / _ \ '__| | |_| | | | | | | |/ _ \| | | | '__|  / _\` |/ _\` | '_ \` _ \ / _ \ | '_ \ / _ \ \ /\ / / "
echo "  \ V /  __/ |  | |  _| |_| | | |_| | (_) | |_| | |    | (_| | (_| | | | | | |  __/ | | | | (_) \ V  V /  "
echo "   \_/ \___|_|  |_|_|  \__, |  \__, |\___/ \__,_|_|     \__, |\__,_|_| |_| |_|\___| |_| |_|\___/ \_/\_/   "
echo "                       |___/   |___/                    |___/                                             "
echo " $separator "
echo .

read -r -p "Press any key to continue . . . " -n1 -s

gio open "$BACKUP_DIRECTORY"  > /dev/null 2>&1
if [ $? -ne 0 ]; then
    echo "Failed to open backup directory You can find your files here:"
	echo "$BACKUP_DIRECTORY"
	echo "Press any key to close this window."
fi

exit


