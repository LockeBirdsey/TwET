import subprocess
import platform
import PySimpleGUI as sg

# Code to add widgets will go here...

# So what's the logic here?

# Do we force the user to download NPM/NPX? It looks like we have to, dang

system_type = platform.system()

# System dependent variables
which_command = "which"

if system_type is "Windows":
    which_command = "where"

# Constants
NPM = "npm"
NPX = "npx"
TWEEGO = "tweego"


def get_bin_path(app_name):
    try:
        proc = test_existence(app_name)
        location = proc.stdout.split("\n")[0]
        print(app_name + " found at " + location)
        return location
    except AssertionError:
        print(app_name + " was not found")
        return ""
        # We have a result, now grab the first line of output
        # Windows note: the first location returned /tends/ to be the binary itself


def test_existence(app_name):
    the_process = subprocess.run([which_command, app_name], universal_newlines=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    assert (the_process.stderr is '')
    return the_process


# 1: Check for NPM/NPX. If not, ask perms to get
##Test for npx/npm
npm_location = get_bin_path(NPM)
npx_location = get_bin_path(NPX)
tweego_location = get_bin_path(TWEEGO)  # Still need to test for StoryFormats
# 2: Check Tweego and Storyformats. If not detected ask perms and download, and set up
sg.theme("LightBlue2")

layout = [[sg.Text('NPM Location:', size=(15, 1)), sg.Text(npm_location)],
          [sg.Text('NPX Location:', size=(15, 1)), sg.Text(npx_location)],
          [sg.Text('TweeGo Location:', size=(15, 1)), sg.Text(tweego_location)],
          [sg.Text('Name of project:', size=(15, 1)), sg.InputText(key="_PROJECTNAME_")],
          [sg.Text('Directory of project:', size=(15, 1)), sg.Input(key="_PROJECTDIR_"), sg.FolderBrowse()],
          [sg.Button('Ok'), sg.Button('Exit')],
          [sg.Text("https://www.github.com/LockeBirdsey/yate")]
          ]
window = sg.Window('YATE Setup', layout)

while True:
    event, values = window.read()
    project_name = values["_PROJECTNAME_"]
    project_directory = values["_PROJECTDIR_"]
    if event in (None, 'Exit'):  # if user closes window or clicks cancel
        break
    if event in (None, "Ok"):
        # Where the fun begins.
        print("okay")

    # print('You entered ', values[0])

window.close()

print(project_name)
print(project_directory)
