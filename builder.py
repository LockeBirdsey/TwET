import multiprocessing
import subprocess
import platform
from pathlib import Path
import sys
from threading import Thread
from queue import Queue, Empty
import PySimpleGUI as sg
import constants
from datetime import datetime

# Code to add widgets will go here...

# So what's the logic here?

# Do we force the user to download NPM/NPX? It looks like we have to, dang
system_type = platform.system()

# System dependent variables
which_command = "which"

if system_type is "Windows":
    which_command = "where"

libs = {
    "npm_location": "",
    "npx_location": "",
    "tweego_location": ""}

project = {
    "name": "",
    "directory": "",
    "html": ""
}

ON_POSIX = 'posix' in sys.builtin_module_names


def enqueue_output(out, queue):
    for line in iter(out.readline, b''):
        queue.put(line)
    out.close()


def get_bin_path(app_name):
    try:
        proc = test_existence(app_name)
        location = proc.stdout.split("\n")[0].strip()
        print(app_name + " found at " + location)
        return location
    except AssertionError:
        print(app_name + " was not found")
        return ""
        # We have a result, now grab the first line of output
        # Windows note: the first location returned /tends/ to be the binary itself


def run_command(commands, q):
    process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, bufsize=0,
                               text=None)
    t = Thread(target=enqueue_output, args=(process.stdout, q))
    t.daemon = True
    t.start()
    #
    # while True:
    #     try:
    #         line = q.get_nowait()  # or q.get(timeout=.1)
    #     except Empty:
    #         pass
    #     else:  # got line
    #         print(str(line, encoding="utf-8"))
    #     if not t.is_alive():
    #         break
    # print("Done")


def test_existence(app_name):
    the_process = subprocess.run([which_command, app_name], universal_newlines=True,
                                 stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
    assert (the_process.stderr is '')
    return the_process


def main():
    # 1: Check for NPM/NPX. If not, ask perms to get
    ##Test for npx/npm
    global libs
    global project
    log_queue = Queue()
    libs["npm_location"] = get_bin_path(constants.NPM)
    libs["npx_location"] = get_bin_path(constants.NPX)
    libs["tweego_location"] = get_bin_path(constants.TWEEGO)  # Still need to test for StoryFormats
    # 2: Check Tweego and Storyformats. If not detected ask perms and download, and set up
    sg.theme("LightBlue2")

    layout = [[sg.Text('NPM Location:', size=(15, 1)), sg.Text(libs["npm_location"])],
              [sg.Text('NPX Location:', size=(15, 1)), sg.Text(libs["npx_location"])],
              [sg.Text('TweeGo Location:', size=(15, 1)),
               sg.InputText(key="_TWEEGOLOC_", default_text=libs["tweego_location"]), sg.FileBrowse()],
              [sg.Text('Project Name:', size=(15, 1)), sg.InputText(key="_PROJECTNAME_", default_text="Twinee")],
              [sg.Text('Project Directory:', size=(15, 1)), sg.Input(key="_PROJECTDIR_"), sg.FolderBrowse()],
              [sg.Text('Project HTML File:', size=(15, 1)), sg.InputText(key="_PROJECTHTML_"), sg.FileBrowse()],
              [sg.Text('Project Output Directory:', size=(15, 1)), sg.Input(key="_PROJECTOUTPUTDIR_"),
               sg.FolderBrowse()],
              [sg.Button('Build for ' + system_type), sg.Button('Build for Web'), sg.Button('Help'),
               sg.Button('About')],
              [sg.Button('Exit')],
              [sg.Text("https://www.github.com/LockeBirdsey/yate")],
              [sg.Multiline('Hello!', size=(60, 5), key="dialogue")]
              ]
    window = sg.Window('YATE Builder', layout)
    dialogue_box = window.find_element("dialogue")

    while True:
        event, values = window.read()
        project_name = values["_PROJECTNAME_"]
        project_html = values["_PROJECTHTML_"]
        project_source_directory = values["_PROJECTDIR_"]
        tweego_location = values["_TWEEGOLOC_"]
        project_output_directory = values["_PROJECTOUTPUTDIR_"]
        if event in (None, 'Exit'):  # if user closes window or clicks cancel
            break
        if event in (None, 'Build for Web'):
            # Where the fun begins.
            print("okay")
        if event in (None, 'Build for ' + system_type):
            project["name"] = project_name

            pod_path = Path(project_output_directory)
            tmp_dir = pod_path.joinpath(Path("tmp"))

            # Build tmp dir
            if tmp_dir.is_dir():
                # Begin the building in a separate thread please
                # build_directories(tmp_dir, libs, project_name, log_queue)
                proc = multiprocessing.Process(target=build_directories, args=(tmp_dir, libs, project, log_queue,))
                proc.start()
            else:
                tmp_dir.mkdir()
                print("hrmm")

        try:
            line = log_queue.get_nowait()  # or q.get(timeout=.1)
        except Empty:
            print("nothing?")
            # pass
        else:  # got line
            print(str(line, encoding="utf-8"))
    window.close()


def build_directories(root, libs, project, log_queue):
    print(libs["npx_location"] + " ::")
    uuid = datetime.now().strftime('%Y%m%d%H%M%S')
    the_dir = root.joinpath(project["name"] + "-" + uuid)
    the_dir = the_dir.joinpath(project["name"])
    run_command([libs["npx_location"], "create-electron-app", str(the_dir)], log_queue)
    the_dir = the_dir.joinpath("src")
    pd_path = Path(project["directory"])
    html_path = Path(project["html"])
    # shutil.copytree(project_source_directory, tmp_dir)
    # shutil.copy(project_html, tmp_dir.joinpath("index.html"))


if __name__ == '__main__':
    main()
