#!/usr/bin/makensis

; BEGIN NSIS TEMPLATE HEADER
!define /file APPDIR "APPDIR"
!define /file FILENAME "FILENAME"
!define /file APPNAME "APPNAME"
!define /file VERSION "VERSION"
!define /file AUTHOR "AUTHOR"
!define /file PUBLISHER "PUBLISHER"
!define /file DESCRIPTION "DESCRIPTION"
!define /file ICON "ICON"
!define /file LICENSE "LICENSE"
!define /file INSTALLSIZE "INSTALLSIZE"
!define /file ARCH "ARCH"
; END NSIS TEMPLATE HEADER

; Marker file to tell the uninstaller that it's a user installation
!define USER_INSTALL_MARKER _user_install_marker

SetCompressor lzma

!if "${NSIS_PACKEDVERSION}" >= 0x03000000
    Unicode true
    ManifestDPIAware true
!endif

!define MULTIUSER_EXECUTIONLEVEL Highest
!define MULTIUSER_INSTALLMODE_DEFAULT_CURRENTUSER
!define MULTIUSER_MUI
!define MULTIUSER_INSTALLMODE_COMMANDLINE
!define MULTIUSER_INSTALLMODE_INSTDIR "${APPNAME}"
!if ${ARCH} == "AMD64"
    !define MULTIUSER_INSTALLMODE_FUNCTION correctProgramFiles
!endif
!include MultiUser.nsh
!include FileFunc.nsh

; Modern UI installer stuff
!include "MUI2.nsh"
!define MUI_ABORTWARNING
!define MUI_ICON "${ICON}"
!define MUI_UNICON "${ICON}"

; UI pages
!insertmacro MUI_PAGE_WELCOME
!if ${LICENSE} != "None"
	!insertmacro MUI_PAGE_LICENSE "${LICENSE}"
!endif
!insertmacro MULTIUSER_PAGE_INSTALLMODE
!insertmacro MUI_PAGE_DIRECTORY
!insertmacro MUI_PAGE_INSTFILES
!insertmacro MUI_PAGE_FINISH
!insertmacro MUI_UNPAGE_CONFIRM
!insertmacro MUI_UNPAGE_INSTFILES

; UI languages
!insertmacro MUI_LANGUAGE "English"
!insertmacro MUI_LANGUAGE "French"
!insertmacro MUI_LANGUAGE "German"
!insertmacro MUI_LANGUAGE "Spanish"
!insertmacro MUI_LANGUAGE "SpanishInternational"
!insertmacro MUI_LANGUAGE "SimpChinese"
!insertmacro MUI_LANGUAGE "TradChinese"
!insertmacro MUI_LANGUAGE "Japanese"
!insertmacro MUI_LANGUAGE "Italian"
!insertmacro MUI_LANGUAGE "Dutch"
!insertmacro MUI_LANGUAGE "Danish"
!insertmacro MUI_LANGUAGE "Swedish"
!insertmacro MUI_LANGUAGE "Norwegian"
!insertmacro MUI_LANGUAGE "NorwegianNynorsk"
!insertmacro MUI_LANGUAGE "Russian"
!insertmacro MUI_LANGUAGE "Portuguese"
!insertmacro MUI_LANGUAGE "PortugueseBR"
!insertmacro MUI_LANGUAGE "Polish"
!insertmacro MUI_LANGUAGE "Ukrainian"
!insertmacro MUI_LANGUAGE "Czech"
!insertmacro MUI_LANGUAGE "Slovak"
!insertmacro MUI_LANGUAGE "Slovenian"
!insertmacro MUI_LANGUAGE "Arabic"
!insertmacro MUI_LANGUAGE "Hebrew"
!insertmacro MUI_LANGUAGE "Indonesian"
!insertmacro MUI_LANGUAGE "Mongolian"
!insertmacro MUI_LANGUAGE "Albanian"
!insertmacro MUI_LANGUAGE "Belarusian"
!insertmacro MUI_LANGUAGE "Esperanto"
!insertmacro MUI_LANGUAGE "Asturian"
!insertmacro MUI_LANGUAGE "Basque"
!insertmacro MUI_LANGUAGE "ScotsGaelic"
!insertmacro MUI_LANGUAGE "Vietnamese"
!insertmacro MUI_LANGUAGE "Armenian"
!insertmacro MUI_LANGUAGE "Corsican"
!insertmacro MUI_LANGUAGE "Tatar"
!insertmacro MUI_LANGUAGE "Hindi"

; UI languages without lang strings
; !insertmacro MUI_LANGUAGE "Korean"
; !insertmacro MUI_LANGUAGE "Finnish"
; !insertmacro MUI_LANGUAGE "Greek"
; !insertmacro MUI_LANGUAGE "Croatian"
; !insertmacro MUI_LANGUAGE "Bulgarian"
; !insertmacro MUI_LANGUAGE "Hungarian"
; !insertmacro MUI_LANGUAGE "Thai"
; !insertmacro MUI_LANGUAGE "Romanian"
; !insertmacro MUI_LANGUAGE "Latvian"
; !insertmacro MUI_LANGUAGE "Macedonian"
; !insertmacro MUI_LANGUAGE "Estonian"
; !insertmacro MUI_LANGUAGE "Turkish"
; !insertmacro MUI_LANGUAGE "Lithuanian"
; !insertmacro MUI_LANGUAGE "Serbian"
; !insertmacro MUI_LANGUAGE "SerbianLatin"
; !insertmacro MUI_LANGUAGE "Farsi"
; !insertmacro MUI_LANGUAGE "Luxembourgish"
; !insertmacro MUI_LANGUAGE "Breton"
; !insertmacro MUI_LANGUAGE "Icelandic"
; !insertmacro MUI_LANGUAGE "Malay"
; !insertmacro MUI_LANGUAGE "Bosnian"
; !insertmacro MUI_LANGUAGE "Kurdish"
; !insertmacro MUI_LANGUAGE "Irish"
; !insertmacro MUI_LANGUAGE "Uzbek"
; !insertmacro MUI_LANGUAGE "Galician"
; !insertmacro MUI_LANGUAGE "Afrikaans"
; !insertmacro MUI_LANGUAGE "Catalan"
; !insertmacro MUI_LANGUAGE "Pashto"
; !insertmacro MUI_LANGUAGE "Georgian"
; !insertmacro MUI_LANGUAGE "Welsh"

Name "${APPNAME} ${VERSION}"
!if ${VERSION} != "None"
    OutFile "${FILENAME}-${VERSION}-${ARCH}.exe"
!else
    OutFile "${FILENAME}-${ARCH}.exe"
!endif
ShowInstDetails show
ShowUninstDetails show

Var cmdLineInstallDir

Section -SETTINGS
    SetOutPath "$INSTDIR"
    SetOverwrite ifnewer
SectionEnd

Section "!${APPNAME}" sec_app
    !if ${ARCH} == "AMD64"
        SetRegView 64
    !else
        SetRegView 32
    !endif
    SectionIn RO
    File ${ICON}

    SetOutPath "$INSTDIR"
    ; delete old module files
    IfFileExists "$INSTDIR\_internal" 0 +1
        RMDir /r "$INSTDIR\_internal"

    File /r "${APPDIR}\*"

    ; Marker file for per-user install
    StrCmp $MultiUser.InstallMode CurrentUser 0 +3
        FileOpen $0 "$INSTDIR\${USER_INSTALL_MARKER}" w
        FileClose $0
        SetFileAttributes "$INSTDIR\${USER_INSTALL_MARKER}" HIDDEN

    WriteUninstaller $INSTDIR\uninstall.exe

    CreateDirectory "$SMPROGRAMS\${APPNAME}"
    CreateShortCut "$SMPROGRAMS\${APPNAME}\${APPNAME}.lnk" "$INSTDIR\${FILENAME}.exe" "" "$INSTDIR\${ICON}"

    ; Add ourselves to Add/Remove Programs
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "DisplayName" "${APPNAME}"
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "UninstallString" '"$INSTDIR\uninstall.exe"'
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "InstallLocation" "$INSTDIR"
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "DisplayIcon" "$INSTDIR\${ICON}"
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "Publisher" "${PUBLISHER}"
    WriteRegStr SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "DisplayVersion" "${VERSION}"
    WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "NoModify" 1
    WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "NoRepair" 1
    WriteRegDWORD SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}" \
        "EstimatedSize" "${INSTALLSIZE}"

    ; Check if we need to reboot
    IfRebootFlag 0 noreboot
        MessageBox MB_YESNO "A reboot is required to finish the installation. Do you wish to reboot now?" \
            /SD IDNO IDNO noreboot
        Reboot
    noreboot:
SectionEnd

Section "Uninstall"
    !if ${ARCH} == "AMD64"
        SetRegView 64
    !else
        SetRegView 32
    !endif
    SetShellVarContext all
    IfFileExists "$INSTDIR\${USER_INSTALL_MARKER}" 0 +3
        SetShellVarContext current
        Delete "$INSTDIR\${USER_INSTALL_MARKER}"

    RMDir /r /REBOOTOK "$SMPROGRAMS\${APPNAME}"
    RMDir /r /REBOOTOK "$INSTDIR"
    DeleteRegKey SHCTX "Software\Microsoft\Windows\CurrentVersion\Uninstall\${APPNAME}"
SectionEnd

; Functions

Function .onMouseOverSection
    ; Find which section the mouse is over, and set the corresponding description.
    FindWindow $R0 "#32770" "" $HWNDPARENT
    GetDlgItem $R0 $R0 1043 ; description item (must be added to the UI)

    StrCmp $0 ${sec_app} "" +2
        SendMessage $R0 ${WM_SETTEXT} 0 "STR:${APPNAME}"
FunctionEnd

Function .onInit
    ; Multiuser.nsh breaks /D command line parameter. Parse /INSTDIR instead.
    ; Cribbing from https://nsis-dev.github.io/NSIS-Forums/html/t-299280.html
    ${GetParameters} $0
    ClearErrors
    ${GetOptions} '$0' "/INSTDIR=" $1
    IfErrors +2  ; Error means flag not found
        StrCpy $cmdLineInstallDir $1
    ClearErrors

    !insertmacro MULTIUSER_INIT

    ; If cmd line included /INSTDIR, override the install dir set by MultiUser
    StrCmp $cmdLineInstallDir "" +2
        StrCpy $INSTDIR $cmdLineInstallDir
FunctionEnd

Function un.onInit
    !insertmacro MULTIUSER_UNINIT
FunctionEnd

Function correctProgramFiles
    ; The multiuser machinery doesn't know about the different Program files
    ; folder for 64-bit applications. Override the install dir it set.
    StrCmp $MultiUser.InstallMode AllUsers 0 +2
        StrCpy $INSTDIR "$PROGRAMFILES64\${MULTIUSER_INSTALLMODE_INSTDIR}"
FunctionEnd