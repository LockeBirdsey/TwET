import shutil
from pathlib import Path
from queue import Queue, Empty
from time import sleep
import PySimpleGUI as sg
import core
from constants import *


class Builder(core.Core):
    build_state = BuildState.NOTHING
    dialogue_box = None
    # This is a bad hack and the PySimpleGUI dev should feel bad
    PROGRESS_BAR_MAX = 100
    arbitrary_waiting_value = 0

    def main(self):
        build_state = BuildState.NOTHING
        self.find_dependencies()
        libs = self.libs
        project = self.project
        self.log_queue = Queue()
        entry_size = self.entry_size
        text_field_size = (int(entry_size[0] * 2.5), entry_size[1])

        building = False
        sg.theme("LightBlue2")
        tab1_layout = [
            [sg.Frame(
                layout=[[sg.Text('NPM Location:', size=entry_size), sg.Text(libs[NPM_LOCATION], key=NPM_LOCATION)],
                        [sg.Text('NPX Location:', size=entry_size), sg.Text(libs[NPX_LOCATION], key=NPX_LOCATION)],
                        [sg.Text('TweeGo Location:', size=entry_size),
                         sg.InputText(key=TWEEGO_LOCATION, default_text=libs[TWEEGO_LOCATION],
                                      size=text_field_size), sg.FileBrowse()]],
                title="Libraries")],
            [sg.Frame(layout=[[sg.Text('Project Name:', size=entry_size),
                               sg.InputText(key=PROJ_NAME, default_text="Twinee", size=text_field_size)],
                              [sg.Text('Project Directory:', size=entry_size),
                               sg.Input(key=PROJ_DIR, size=text_field_size), sg.FolderBrowse()],
                              [sg.Text('Project HTML File:', size=entry_size),
                               sg.InputText(key=PROJ_HTML, size=text_field_size), sg.FileBrowse()],
                              [sg.Text('Project Output Directory:', size=entry_size),
                               sg.Input(key=PROJ_OUT_DIR, size=text_field_size, enable_events=True),
                               sg.FolderBrowse()]],
                      title="Project Details")]
        ]
        tab2_layout = [
            [sg.Frame(layout=[
                [sg.Text("Name:", size=entry_size), sg.InputText(key=AUTHOR_NAME, size=text_field_size)],
                [sg.Text("Email:", size=entry_size), sg.InputText(key=AUTHOR_EMAIL, size=text_field_size)],
                [sg.Text("Repository:", size=entry_size), sg.InputText(key=AUTHOR_REPO, size=text_field_size)],
                [sg.Text("Version:", size=entry_size), sg.InputText(key=PROJ_VERSION, size=text_field_size)],
                [sg.Text("Window Dimensions:", size=entry_size), sg.InputText(key=PROJ_DIMS, size=text_field_size)],
                [sg.Text("Keywords (comma separated):", size=entry_size),
                 sg.InputText(key=PROJ_KEYWORDS, size=text_field_size)],
                [sg.Text("Icon Location:", size=entry_size), sg.InputText(key=PROJ_ICON_LOCATION, size=text_field_size),
                 sg.FileBrowse()],
            ], title="Author Details")]
        ]
        layout = [[sg.TabGroup([[sg.Tab("Basic", tab1_layout, tooltip="Basic Settings"),
                                 sg.Tab("Advanced", tab2_layout, tooltip="Advanced Settings")]])],

                  [sg.Button('Setup',
                             tooltip="Sets up the project build directory by installing various Electron packages"),
                   sg.Button('Build for ' + self.system_type, disabled=True, key="BUILDBUTTON"),
                   sg.Button('Build for Web', disabled=True, key="BUILDWEBBUTTON"),
                   sg.Button('Help'), sg.Button('About')],
                  [sg.Button('Exit')],
                  [sg.Text("https://www.github.com/LockeBirdsey/yate")],
                  [sg.ProgressBar(100, size=(entry_size[0] * 2.55, entry_size[1] * 6), orientation='h',
                                  key="PROGRESSBAR")],
                  [sg.Multiline('Hello!\n', size=(entry_size[0] * 4, entry_size[1] * 8), key="dialogue",
                                autoscroll=True, disabled=True)]
                  ]

        window = sg.Window('Twine Executable Generation Tool', layout)
        self.dialogue_box = window.find_element("dialogue")

        while True:
            event, values = window.read(timeout=100)
            libs[TWEEGO_LOCATION] = values[TWEEGO_LOCATION]
            project[PROJ_NAME] = values[PROJ_NAME]
            project[PROJ_HTML] = values[PROJ_HTML]
            project[PROJ_DIR] = values[PROJ_DIR]
            project[PROJ_OUT_DIR] = values[PROJ_OUT_DIR]
            if event in (None, 'Exit'):  # if user closes window or clicks cancel
                break
            if event in (None, 'About'):
                sg.popup("About this program", )
            if event in (None, 'Build for Web'):
                # It's basically the same except with some things missing
                print("okay")
                build_state = BuildState.BUILDING_WEB
            if event in (None, 'Setup'):
                build_state = BuildState.SETUP
                build_dir = self.build_new()
            if event in (None, PROJ_OUT_DIR):
                pod_path = Path(project[PROJ_OUT_DIR])
                project_dir = pod_path.joinpath(project[PROJ_NAME])
                potential_lock_path = pod_path.joinpath(DETAILS_FILE_NAME)
                if potential_lock_path.exists():
                    build_state = BuildState.UPDATING
                    sg.Popup(
                        "A lock file has been detected at " + str(potential_lock_path) + "\nLoading its contents...")
                    self.load_lock_file(potential_lock_path)
                    # update widgets with new values
                    self.update_widgets(window)
                    self.activate_buttons(window)

            if event in (None, 'Build for ' + self.system_type):
                build_state = BuildState.BUILDING_NEW
                self.update_dialogue("Building executable for " + self.system_type, append=True)

            if build_state is BuildState.SETUP:
                if not self.lock.locked():
                    self.build_directories(build_dir)
                    self.activate_buttons(window)
                    build_state = BuildState.NOTHING
            elif build_state is BuildState.BUILDING_NEW:
                pass
            elif build_state is BuildState.BUILDING_WEB:
                pass
            elif build_state is BuildState.UPDATING:
                pass

            try:
                line = self.log_queue.get_nowait()
                self.arbitrary_waiting_value = 0
                self.PROGRESS_BAR_MAX = 100
                self.update_progress_bar(window)
            except Empty:
                if build_state is not BuildState.NOTHING:
                    self.arbitrary_waiting_value += 1
                    self.PROGRESS_BAR_MAX += 1
                    self.update_progress_bar(window)
                    sleep(0.1)
                pass
            else:  # got line
                if line is not "":
                    print(str(line, encoding="utf-8"))
                    self.update_dialogue(str(line, encoding="utf-8"), append=True)
        window.close()

    def init_build_directories(self, root):
        self.run_command_with_output([self.libs[NPX_LOCATION], "create-electron-app", str(root)])

    def build_directories(self, root):
        # lets make a file in root that has
        self.update_dialogue("building lock file at " + str(Path(root).joinpath(DETAILS_FILE_NAME)))
        self.create_lock_file(root)
        src_dir = root.joinpath("src")
        self.copy_files(src_dir)

    def copy_files(self, root):
        # copy the source files over
        pd_path = Path(self.project[PROJ_DIR])
        html_path = Path(self.project[PROJ_HTML])
        self.update_dialogue(
            "Copying the source files over from " + str(pd_path) + " to " + str(root.joinpath(pd_path.name)))
        shutil.copytree(pd_path, root.joinpath(pd_path.name))
        # copy and rename the main html file
        self.update_dialogue(
            "Copying the main HTML file over from " + str(html_path) + " to " + str(root.joinpath("index.html")))
        shutil.copy(html_path, root.joinpath("index.html"))

    def build_new(self):
        print("upa")
        pod_path = Path(self.project[PROJ_OUT_DIR])
        project_dir = pod_path.joinpath(self.project[PROJ_NAME])
        self.update_dialogue("Building project into " + str(project_dir))
        if project_dir.is_dir():
            # Warn the user that the directory exists and no project was detected
            sg.Popup("A directory already exists here and cannot be used.\nPlease select a different directory")
        else:
            project_dir.mkdir()
            self.init_build_directories(project_dir)
        return project_dir

    def update_dialogue(self, message, append=True):
        message = message.rstrip()+"\n"
        print(message)  # shadow
        self.dialogue_box.update(message, append=append)

    def activate_buttons(self, win):
        win["BUILDBUTTON"].update(disabled=False)
        win["BUILDWEBBUTTON"].update(disabled=False)

    def update_widgets(self, win):
        for k, v in self.libs.items():
            win[str(k)].update(str(v))
        for k, v in self.project.items():
            win[str(k)].update(str(v))
        for k, v in self.author.items():
            win[str(k)].update(str(v))

    def update_progress_bar(self, win):
        bar = win["PROGRESSBAR"]
        bar.UpdateBar(self.arbitrary_waiting_value, self.PROGRESS_BAR_MAX)


if __name__ == '__main__':
    b = Builder()
    b.main()
