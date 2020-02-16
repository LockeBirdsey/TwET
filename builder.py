from pathlib import Path
from queue import Queue, Empty
from time import sleep
import PySimpleGUI as sg
from datetime import datetime
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
            [sg.Frame(layout=[[sg.Text('NPM Location:', size=entry_size), sg.Text(libs[NPM_LOCATION])],
                              [sg.Text('NPX Location:', size=entry_size), sg.Text(libs[NPX_LOCATION])],
                              [sg.Text('TweeGo Location:', size=entry_size),
                               sg.InputText(key="_TWEEGOLOC_", default_text=libs[TWEEGO_LOCATION],
                                            size=text_field_size),
                               sg.FileBrowse()]], title="Libraries")],
            [sg.Frame(layout=[[sg.Text('Project Name:', size=entry_size),
                               sg.InputText(key="_PROJECTNAME_", default_text="Twinee", size=text_field_size)],
                              [sg.Text('Project Directory:', size=entry_size),
                               sg.Input(key="_PROJECTDIR_", size=text_field_size),
                               sg.FolderBrowse()],
                              [sg.Text('Project HTML File:', size=entry_size),
                               sg.InputText(key="_PROJECTHTML_", size=text_field_size), sg.FileBrowse()],
                              [sg.Text('Project Output Directory:', size=entry_size),
                               sg.Input(key="_PROJECTOUTPUTDIR_", size=text_field_size),
                               sg.FolderBrowse()]], title="Project Details")]
        ]
        tab2_layout = [
            [sg.Frame(layout=[
                [sg.Text("Name:", size=entry_size), sg.InputText(key="__NAME__", size=text_field_size)],
                [sg.Text("Email:", size=entry_size), sg.InputText(key="__EMAIL__", size=text_field_size)],
                [sg.Text("Repository:", size=entry_size), sg.InputText(key="__REPO__", size=text_field_size)],
                [sg.Text("Version:", size=entry_size), sg.InputText(key="__VERSION__", size=text_field_size)],
                [sg.Text("Keywords (comma separated):", size=entry_size),
                 sg.InputText(key="__KEYWORDS__", size=text_field_size)],
                [sg.Text("Icon Location:", size=entry_size), sg.InputText(key="__ICON_PATH__", size=text_field_size),
                 sg.FileBrowse()],
            ], title="Author Details")]
        ]
        layout = [[sg.TabGroup([[sg.Tab("Basic", tab1_layout, tooltip="Basic Settings"),
                                 sg.Tab("Advanced", tab2_layout, tooltip="Advanced Settings")]])],

                  [sg.Button('Build for ' + self.system_type), sg.Button('Build for Web'), sg.Button('Help'),
                   sg.Button('About')],
                  [sg.Button('Exit')],
                  [sg.Text("https://www.github.com/LockeBirdsey/yate")],
                  [sg.Multiline('Hello!\n', size=(entry_size[0] * 4, entry_size[1] * 8), key="dialogue",
                                autoscroll=True, disabled=True)]
                  ]

        window = sg.Window('YATE Builder', layout)
        dialogue_box = window.find_element("dialogue")

        while True:
            event, values = window.read(timeout=100)
            libs[TWEEGO_LOCATION] = values["_TWEEGOLOC_"]
            project[PROJ_NAME] = values["_PROJECTNAME_"]
            project[PROJ_HTML] = values["_PROJECTHTML_"]
            project[PROJ_DIR] = values["_PROJECTDIR_"]
            project[PROJ_OUT_DIR] = values["_PROJECTOUTPUTDIR_"]
            if event in (None, 'Exit'):  # if user closes window or clicks cancel
                break
            if event in (None, 'About'):
                sg.popup("About this program", )
            if event in (None, 'Build for Web'):
                # Where the fun begins.
                print("okay")
            if event in (None, 'Build for ' + self.system_type):
                building = True
                dialogue_box.update("Building executable for " + self.system_type + "\n", append=True)
                pod_path = Path(project[PROJ_OUT_DIR])

                # What if pod_path already contains somestuff
                # popup to ask if its already a build place

                tmp_dir = pod_path.joinpath(Path("tmp"))

                # Build tmp dir
                if tmp_dir.is_dir():
                    self.build_directories(tmp_dir, libs, project)
                else:
                    tmp_dir.mkdir()
                    self.build_directories(tmp_dir, libs, project)
            try:
                line = self.log_queue.get_nowait()  # or q.get(timeout=.1)
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

    def build_directories(self, root, libs, project):
        uuid = datetime.now().strftime('%Y%m%d%H%M%S')
        the_dir = root.joinpath(project["name"] + "-" + uuid)
        the_dir = the_dir.joinpath(project["name"])
        self.run_command_with_output([libs["npx_location"], "create-electron-app", str(the_dir)])
        # need this dir to be created before continuing
        the_dir = the_dir.joinpath("src")
        pd_path = Path(project["directory"])
        html_path = Path(project["html"])
        # shutil.copytree(project_source_directory, the_dir)
        # shutil.copy(project_html, tmp_dir.joinpath("index.html"))


if __name__ == '__main__':
    b = Builder()
    b.main()
