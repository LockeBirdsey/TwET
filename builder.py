from pathlib import Path
from queue import Queue, Empty
from time import sleep
import PySimpleGUI as sg
from datetime import datetime
import core


class Builder(core.Core):
    def main(self):
        # 1: Check for NPM/NPX. If not, ask perms to get
        self.find_dependencies()
        project = self.project
        building = False
        libs = self.libs
        project = self.project
        self.log_queue = Queue()

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
                  [sg.Button('Build for ' + self.system_type), sg.Button('Build for Web'), sg.Button('Help'),
                   sg.Button('About')],
                  [sg.Button('Exit')],
                  [sg.Text("https://www.github.com/LockeBirdsey/yate")],
                  [sg.Multiline('Hello!\n', size=(75, 8), key="dialogue", autoscroll=True, disabled=True)]
                  ]
        window = sg.Window('YATE Builder', layout)
        dialogue_box = window.find_element("dialogue")

        while True:
            event, values = window.read(timeout=100)
            project["name"] = values["_PROJECTNAME_"]
            project["html"] = values["_PROJECTHTML_"]
            project["directory"] = values["_PROJECTDIR_"]
            libs["tweego_location"] = values["_TWEEGOLOC_"]
            project["output_directory"] = values["_PROJECTOUTPUTDIR_"]
            if event in (None, 'Exit'):  # if user closes window or clicks cancel
                break
            if event in (None, 'Build for Web'):
                # Where the fun begins.
                print("okay")
            if event in (None, 'Build for ' + self.system_type):
                building = True
                dialogue_box.update("Building executable for " + self.system_type + "\n", append=True)
                pod_path = Path(project["output_directory"])
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
        self.run_command([libs["npx_location"], "create-electron-app", str(the_dir)])
        # need this dir to be created before continuing
        the_dir = the_dir.joinpath("src")
        pd_path = Path(project["directory"])
        html_path = Path(project["html"])
        # shutil.copytree(project_source_directory, the_dir)
        # shutil.copy(project_html, tmp_dir.joinpath("index.html"))


if __name__ == '__main__':
    b = Builder()
    b.main()
