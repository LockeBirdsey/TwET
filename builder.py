import shutil
from pathlib import Path
from queue import Queue, Empty
from time import sleep
import PySimpleGUI as sg
import core
from constants import *


class Builder(core.Core):
    def main(self):
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

                  [sg.Button('Setup'), sg.Button('Build for ' + self.system_type, disabled=True, key="BUILDBUTTON"),
                   sg.Button('Build for Web', disabled=True, key="BUILDWEBBUTTON"),
                   sg.Button('Help'), sg.Button('About')],
                  [sg.Button('Exit')],
                  [sg.Text("https://www.github.com/LockeBirdsey/yate")],
                  [sg.Multiline('Hello!\n', size=(entry_size[0] * 4, entry_size[1] * 8), key="dialogue",
                                autoscroll=True, disabled=True)]
                  ]

        window = sg.Window('YATE Builder', layout)
        dialogue_box = window.find_element("dialogue")

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
            if event in (None, PROJ_OUT_DIR):
                pod_path = Path(project[PROJ_OUT_DIR])
                project_dir = pod_path.joinpath(project[PROJ_NAME])
                potential_lock_path = pod_path.joinpath(DETAILS_FILE_NAME)
                if potential_lock_path.exists():
                    sg.Popup(
                        "A lock file has been detected at " + str(potential_lock_path) + "\nLoading its contents...")
                    self.load_lock_file(potential_lock_path)
                    # update widgets with new values
                    self.update_widgets(window)
                    window["BUILDBUTTON"].update(disabled=False)
                    window["BUILDWEBBUTTON"].update(disabled=False)
            if event in (None, 'Build for ' + self.system_type):
                dialogue_box.update("Building executable for " + self.system_type + "\n", append=True)
                pod_path = Path(project[PROJ_OUT_DIR])
                project_dir = pod_path.joinpath(project[PROJ_NAME])

                if project_dir.is_dir():
                    # Warn the user that the directory exists and no project was detected
                    pass
                else:
                    project_dir.mkdir()
                    building = True
                    self.init_build_directories(project_dir, libs)

            if building and not self.lock.locked() and project_dir is not None:
                self.build_directories(project_dir, libs, project)
                building = False
                pass
            try:
                line = self.log_queue.get_nowait()
            except Empty:
                if building:
                    dialogue_box.update(".", append=True)
                    sleep(0.1)
                pass
            else:  # got line
                if line is not "":
                    print(str(line, encoding="utf-8"))
                    dialogue_box.update(str(line, encoding="utf-8"), append=True)
        window.close()

    def init_build_directories(self, root, libs):
        self.run_command_with_output([libs[NPX_LOCATION], "create-electron-app", str(root)])

    def build_directories(self, root, libs, project):
        the_dir = root.joinpath("src")
        pd_path = Path(project[PROJ_DIR])
        html_path = Path(project[PROJ_HTML])

        # lets also make a file in root that has
        self.create_lock_file(root)

        # copy the source files over
        src_dir = root.joinpath("src")
        shutil.copytree(pd_path, src_dir.joinpath(pd_path.name))
        # copy and rename the main html file
        shutil.copy(html_path, src_dir.joinpath("index.html"))

    def update_widgets(self, win):
        for k, v in self.libs.items():
            try:
                win[str(k)].update(str(v))
            except:
                print("Could not find key")
        for k, v in self.project.items():
            try:
                win[str(k)].update(str(v))
            except:
                print("Could not find key")
        for k, v in self.author.items():
            try:
                win[str(k)].update(str(v))
            except:
                print("Could not find key")


if __name__ == '__main__':
    b = Builder()
    b.main()
