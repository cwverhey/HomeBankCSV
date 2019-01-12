; example2.nsi
;
; This script is based on example1.nsi, but it remember the directory, 
; has uninstall support and (optionally) installs start menu shortcuts.
;
; It will install example2.nsi into a directory that the user selects,

;--------------------------------

; The name of the installer
Name "Install HomeBank CSV Converter"

; The file to write
OutFile "HomeBankCSVInstaller.exe"

; The default installation directory
InstallDir "$PROGRAMFILES\HomeBank CSV"

; Registry key to check for directory (so if you install again, it will 
; overwrite the old one automatically)
InstallDirRegKey HKLM "Software\HomeBankCSV" "Install_Dir"

; Request application privileges for Windows Vista
RequestExecutionLevel admin

;--------------------------------

; Pages

Page components
Page directory
Page instfiles

UninstPage uninstConfirm
UninstPage instfiles

;--------------------------------

; The stuff to install
Section "HomeBank CSV Converter"

  SectionIn RO
  
  ; Set output path to the installation directory.
  SetOutPath $INSTDIR
  
  ; Put file there
  File "dist\HomeBankCSV.exe"
  File "dist\MSVCR100.dll"
  File "dist\python34.dll"
  File "dist\tcl86t.dll"
  File "dist\tk86t.dll"
  File /r /x encoding /x demos /x images /x tzdata /x msgs /x tk*.lib /x tcl*.sh /x tcl*.lib /x itcl* /x sqlite* /x tdbc* /x dde* /x reg* /x tcl8 /x thread* /x tix* "dist\tcl"
  
  
  
  ; Write the installation path into the registry
  WriteRegStr HKLM SOFTWARE\HomeBankCSV "Install_Dir" "$INSTDIR"
  
  ; Write the uninstall keys for Windows
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HomeBankCSV" "DisplayName" "HomeBank CSV Converter"
  WriteRegStr HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HomeBankCSV" "UninstallString" '"$INSTDIR\uninstall.exe"'
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HomeBankCSV" "NoModify" 1
  WriteRegDWORD HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HomeBankCSV" "NoRepair" 1
  WriteUninstaller "$INSTDIR\uninstall.exe"
  
SectionEnd

; Optional section (can be disabled by the user)
Section "Start Menu Shortcuts"

  CreateDirectory "$SMPROGRAMS\HomeBank CSV"
  CreateShortcut "$SMPROGRAMS\HomeBank CSV\Uninstall.lnk" "$INSTDIR\uninstall.exe" "" "$INSTDIR\uninstall.exe" 0
  CreateShortcut "$SMPROGRAMS\HomeBank CSV\HomeBank CSV.lnk" "$INSTDIR\HomeBankCSV.exe" "" "$INSTDIR\HomeBankCSV.exe" 0
  
SectionEnd

;--------------------------------

; Uninstaller

Section "Uninstall"
  
  ; Remove registry keys
  DeleteRegKey HKLM "Software\Microsoft\Windows\CurrentVersion\Uninstall\HomeBankCSV"
  DeleteRegKey HKLM SOFTWARE\HomeBankCSV

  ; Remove files and uninstaller
  Delete $INSTDIR\HomeBankCSV.exe
  Delete $INSTDIR\MSVCR100.dll
  Delete $INSTDIR\python34.dll
  Delete $INSTDIR\tcl86t.dll
  Delete $INSTDIR\tk86t.dll
  RMDir  /r $INSTDIR\tcl
  Delete $INSTDIR\HomeBankCSV.log
  Delete $INSTDIR\uninstall.exe

  ; Remove shortcuts, if any
  Delete "$SMPROGRAMS\HomeBank CSV\*.*"

  ; Remove directories used
  RMDir "$SMPROGRAMS\HomeBank CSV"
  RMDir "$INSTDIR"

SectionEnd
