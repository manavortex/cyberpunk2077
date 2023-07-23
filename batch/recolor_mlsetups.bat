@echo off
setlocal enabledelayedexpansion

REM this script will create a bunch of mlsetup variants for you via string substitution. 
REM You need to set the two values below.

REM color to replace in source file
set "originalColor=40df5b_69039f"

REM file to copy and rename
set "sourceFile=original_.mlsetup.json"

pushd "%~dp0"

set "destinationFolder=."

set "appearanceNames[0]=white"
set "appearanceNames[1]=black"
set "appearanceNames[2]=silver"
set "appearanceNames[3]=gold"
set "appearanceNames[4]=blue"
set "appearanceNames[5]=lightblue"
set "appearanceNames[6]=pink"
set "appearanceNames[7]=rose"
set "appearanceNames[8]=violet"
set "appearanceNames[9]=lightgreen"
set "appearanceNames[10]=yellow"
set "appearanceNames[11]=orange"
set "appearanceNames[12]=scarlet"

set "original_color=40df5b_69039f"

set "appearanceColors[0]=9f647c_a1b637"
set "appearanceColors[1]=40df5b_d42857"
set "appearanceColors[2]=b5bdfd_d42857"
set "appearanceColors[3]=cbddbb_69039f"
set "appearanceColors[4]=305986_null"
set "appearanceColors[5]=5a5170_69039f"
set "appearanceColors[6]=058279_69039f"
set "appearanceColors[7]=f9cb05_a1b637"
set "appearanceColors[8]=2251f0_69039f"
set "appearanceColors[9]=45be12_69039f"
set "appearanceColors[10]=6c74fa_null"
set "appearanceColors[11]=cbbe5d_null"
set "appearanceColors[12]=35f4d2_null"

for /L %%i in (0,1,12) do (
    set "fileName=bustier_!appearanceNames[%%i]!.mlsetup.json"
    copy "%destinationFolder%\%sourceFile%" "%destinationFolder%\!fileName!"
    
    rem Text replacement
    set "replacement=!appearanceColors[%%i]!" 
    echo !replacement!
    rem Text replacement using PowerShell
    powershell -Command "(Get-Content '%destinationFolder%\!fileName!') -replace '!originalColor!', '!replacement!' | Set-Content '%destinationFolder%\!fileName!'"
)

echo All files created successfully.
pause
