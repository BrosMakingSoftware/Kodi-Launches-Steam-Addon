# Kodi modules
import xbmc
import xbmcaddon
import xbmcgui

# Python modules
import platform
import os.path
import subprocess


# Getting addon constants
ADDON = xbmcaddon.Addon('script.kodi.launches.steam')
ADDON_ID = ADDON.getAddonInfo('id')
ADDON_NAME = ADDON.getAddonInfo('name')
ADDON_VERSION = ADDON.getAddonInfo('version')
MSG = ADDON.getLocalizedString

# Setting program constants
WINDOWS_32_EXECUTABLE_ON_X86 = '%ProgramFiles%\\Steam\\Steam.exe'
WINDOWS_32_EXECUTABLE_ON_X64 = '%ProgramFiles(x86)%\\Steam\\Steam.exe'
LINUX_EXECUTABLE_ON_x86_64 = '/usr/bin/steam'
MAC_EXECUTABLE = '~/Library/Application Support/Steam/Steam.app/Contents/MacOS/steam_osx'

# Getting main settings
useCustomExecutable = ADDON.getSetting('useCustomExecutable')


####################### Defining common methods #######################

# Method to print logs on a standard way
def log(message, level=xbmc.LOGNOTICE):
    xbmc.log("[{0}:v{1}] {2}".format(ADDON_ID, ADDON_VERSION, message), level)
# log

# Method to show "Default executable not found"
def showExecutableNotFoundDialog():
    title = MSG(32008)
    message = MSG(32009)
    xbmcgui.Dialog().ok(title, message)
# showExecutableNotFoundDialog

# Method to show "Install Steam"
def showInstallProgramDialog():
    title = MSG(32010)
    message = MSG(32011)
    xbmcgui.Dialog().ok(title, message)
# showInstallProgramDialog

# Method to ask if user wants to open Addon Settings
def showOpenSettingsDialog():
    title = MSG(32014)
    message = MSG(32015)
    if xbmcgui.Dialog().yesno(title, message):
        ADDON.openSettings()
# showOpenSettingsDialog

# Method to show all errors when default executable is not found
def showErrorDialogs():
    showExecutableNotFoundDialog()
    showInstallProgramDialog()
    showOpenSettingsDialog()
# showErrorDialogs

# Method to show "Unknown platform, but you can still use a custom executable location"
def showUnknownPlatformDialog():
    title = MSG(32016)
    message = MSG(32017)
    xbmcgui.Dialog().ok(title, message)
# showUnknownPlatformDialog

# Method to show "Custom executable not found, you should change it"
def showCustomExecutableNotFoundDialog():
    title = MSG(32018)
    message = MSG(32019)
    xbmcgui.Dialog().ok(title, message)
    showOpenSettingsDialog()
# showCustomExecutableNotFoundDialog

# Method to execute Steam using provided executable and parameters from Settings
def executeSteam(executable):
    parameters = ''
    startSteamInBigPictureMode = ADDON.getSetting('startSteamInBigPictureMode')
    if startSteamInBigPictureMode == 'true':
        bigPictureModeParameter = ADDON.getSetting('bigPictureModeParameter')
        parameters = bigPictureModeParameter

    useExtraParameters = ADDON.getSetting('useExtraParameters')
    extraParameters = ADDON.getSetting('extraParameters')
    if (useExtraParameters == 'true') and (extraParameters.strip() != ""):
        parameters = parameters + ' ' + extraParameters.lstrip().rstrip()

    log('Calling executable: {0}  with parameters: {1}'.format(executable,parameters))
    subprocess.call([executable, parameters])
# executeSteam


####################### Addon entrypoint #######################

# Starting the Addon
log("Starting Addon")

# Calling custom executable (if it is activated on Addon Settings)
if useCustomExecutable == 'true':
    customExecutable = ADDON.getSetting('customExecutable')
    if os.path.isfile(customExecutable):
        executeSteam(customExecutable)
    else:
        log('Executable not found on the custom location provided by user', xbmc.LOGERROR)
        showCustomExecutableNotFoundDialog()

# Here we enter to the logic to find the default executable location
else:
    executable = ''
    executableTemp = ''

    if platform.system() == 'Windows':
        executableTemp = os.path.expandvars(WINDOWS_32_EXECUTABLE_ON_X64)
        if os.path.isfile(executableTemp):
            executable = executableTemp
        else:
            executableTemp = os.path.expandvars(WINDOWS_32_EXECUTABLE_ON_X86)
            if os.path.isfile(executableTemp):
                executable = executableTemp
            else:
                # Windows executable not found
                log('Windows executable not found on default Program-Files paths', xbmc.LOGERROR)
                showErrorDialogs()

    else:

        if platform.system() == "Linux":
            if os.path.isfile(LINUX_EXECUTABLE_ON_x86_64):
                executable = LINUX_EXECUTABLE_ON_x86_64
            else:
                # Linux executable not found
                log('Linux executable not found on default binaries paths', xbmc.LOGERROR)
                showErrorDialogs()

        else:

            if platform.system() == "Darwin":
                executableTemp = os.path.expanduser(MAC_EXECUTABLE)
                if os.path.isfile(executableTemp):
                    executable = executableTemp
                else:
                    # Mac executable not found
                    log('MacOS executable not found on default Applications paths', xbmc.LOGERROR)
                    showErrorDialogs()

            else:
                # Unknown platform
                # This scenario is hard to get, but still possible
                log('Unknown platform, cannot check default Applications/Programs paths', xbmc.LOGERROR)
                showUnknownPlatformDialog()
                showUseCustomExecutable()

    if executable:
        executeSteam(executable)
