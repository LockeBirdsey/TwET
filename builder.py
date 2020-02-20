import multiprocessing
import shutil
from pathlib import Path
from queue import Empty
from time import sleep
import PySimpleGUI as sg
import core
from constants import *
from icon_tool import IconTool
import re


class Builder(core.Core):
    build_state = BuildState.NOTHING
    dialogue_box = None
    # This is a bad hack and the PySimpleGUI dev should feel bad
    PROGRESS_BAR_MAX = 100
    arbitrary_waiting_value = 0
    return_code = 0

    def main(self):
        build_state = BuildState.NOTHING
        self.find_dependencies()
        libs = self.libs
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
                              [sg.Text("Author Name:", size=entry_size),
                               sg.InputText(key=AUTHOR_NAME, size=text_field_size, default_text="Your Name")],
                              [sg.Text("Version:", size=entry_size),
                               sg.InputText(key=PROJ_VERSION, size=text_field_size, default_text="1.0.0")],
                              [sg.Text('Project Directory:', size=entry_size),
                               sg.Input(key=PROJ_DIR, size=text_field_size), sg.FolderBrowse()],
                              [sg.Text('Project HTML File:', size=entry_size),
                               sg.InputText(key=PROJ_HTML, size=text_field_size), sg.FileBrowse()],
                              [sg.Text('Project Output Directory:', size=entry_size,
                                       tooltip="Where you want the executable to be stored"),
                               sg.Input(key=PROJ_PARENT_DIR, size=text_field_size, enable_events=True),
                               sg.FolderBrowse()],
                              ],
                      title="Project Details")]
        ]
        tab2_layout = [
            [sg.Frame(layout=[
                [sg.Text("Email:", size=entry_size), sg.InputText(key=AUTHOR_EMAIL, size=text_field_size)],
                [sg.Text("Repository:", size=entry_size), sg.InputText(key=AUTHOR_REPO, size=text_field_size)],
                [sg.Text("Window Dimensions:", size=entry_size), sg.InputText(key=PROJ_DIMS, size=text_field_size)],
                [sg.Text("Keywords (comma separated):", size=entry_size),
                 sg.InputText(key=PROJ_KEYWORDS, size=text_field_size)],
                [sg.Text("Icon Location:", size=entry_size), sg.InputText(key=PROJ_ICON_LOCATION, size=text_field_size),
                 sg.FileBrowse()],
            ], title="Author Details")]
        ]
        layout = [[sg.TabGroup([[sg.Tab("Essential", tab1_layout, tooltip="Basic Settings"),
                                 sg.Tab("Optional", tab2_layout, tooltip="Advanced Settings")]])],

                  [sg.Button('Setup New Build Files',
                             tooltip="Sets up the project build directory by installing various Electron packages",
                             key="SETUPBUTTON"),
                   sg.Button("Update Information", key="UPDATEBUTTON", disabled=True),
                   sg.Button('Build for ' + self.system_type, disabled=True, key="BUILDBUTTON"),
                   sg.Button('Build for Web', disabled=True, key="BUILDWEBBUTTON"),
                   sg.Button('Help'), sg.Button('About')],
                  [sg.Button('Exit')],
                  [sg.Multiline('Hello!\n', size=(entry_size[0] * 4, entry_size[1] * 8), key="dialogue",
                                autoscroll=True, disabled=True)],
                  [sg.ProgressBar(100, size=(entry_size[0] * 2.8, entry_size[1] * 6), orientation='h',
                                  key="PROGRESSBAR")]
                  ]

        window = sg.Window('Twine Executable Generation Tool', layout)
        self.dialogue_box = window.find_element("dialogue")

        while True:
            event, values = window.read(timeout=100)
            self.update_dictionaries(values)
            if event in (None, 'Exit'):  # if user closes window or clicks cancel
                win_keys = window.AllKeysDict
                for k in win_keys:
                    try:
                        window[k].update(disabled=True)
                    except:
                        pass
                self.terminate_processes()
                break
            if event in (None, 'About'):
                sg.popup("About this program\n"
                         "Made by Locke Birdsey (@lockebirdsey)\n"
                         "Submit bugs at https://github.com/LockeBirdsey/TwEGeT/issues", title="About TwEGeT")
            if event in (None, "BUILDWEBBUTTON"):
                # It's basically the same except with some things missing
                build_state = BuildState.BUILDING_WEB
            if event in (None, "SETUPBUTTON"):
                build_state = BuildState.SETUP
                self.build_new()
            if event in (None, "UPDATEBUTTON"):
                self.update_dictionaries(values)
                self.create_lock_file(Path(self.project[PROJ_BUILD_DIR]))
            if event in (None, "Help"):
                sg.popup(HELP_STRING, title="Help with TwEGeT")
            if event in (None, PROJ_PARENT_DIR):
                potential_lock_path = Path(self.project[PROJ_PARENT_DIR]).joinpath(DETAILS_FILE_NAME)
                if potential_lock_path.exists():
                    sg.Popup(
                        "A lock file has been detected at " + str(potential_lock_path) + "\nLoading its contents...")
                    self.load_lock_file(potential_lock_path)
                    # update widgets with new values
                    self.update_widgets(window)
                    self.activate_buttons(window)
            if event in (None, "BUILDBUTTON"):
                build_state = BuildState.BUILDING_NEW
                self.logger.info("Building executable for " + self.system_type)
                self.create_lock_file(Path(self.project[PROJ_BUILD_DIR]))
                self.update_package_json(Path(self.project[PROJ_BUILD_DIR]).joinpath(YARN_PACKAGE_FILE))
                # icon setup
                if self.project[PROJ_ICON_LOCATION] != "":
                    icon_path = Path(self.project[PROJ_ICON_LOCATION])
                    icon_tool = IconTool(icon_path)
                    icon_tool.convert(Path(self.project[PROJ_BUILD_DIR]), target_system=self.system_type)
                    self.logger.info("Creating " + self.system_type + " compatible icons")
                self.run_command_with_output([self.libs[NPM_LOCATION] + self.cmd_extension, "run", "make"],
                                             cwd=self.project[PROJ_BUILD_DIR])
            # The buildstates
            if build_state == BuildState.SETUP:
                if not self.lock.locked():
                    self.build_directories(Path(self.project[PROJ_BUILD_DIR]))
                    self.activate_buttons(window)
                    build_state = BuildState.NOTHING
                    # TODO Generate build files
            elif build_state == BuildState.BUILDING_NEW:
                if not self.lock.locked():
                    build_state = BuildState.NOTHING
            elif build_state == BuildState.BUILDING_WEB:
                zip_path = Path(self.project[PROJ_BUILD_DIR]).joinpath(self.project[PROJ_NAME])
                shutil.make_archive(zip_path, 'zip', (Path(self.project[PROJ_BUILD_DIR]).joinpath(ELECTRON_SOURCE_DIR)))
                # TODO thread this command so for very large zip files we can update the progress bar
                self.logger.info("Zip file located at " + str(zip_path) + ".zip")
                build_state = BuildState.NOTHING
            elif build_state == BuildState.UPDATING:
                pass

            try:
                line = self.log_queue.get_nowait()
                self.reset_progress_bar(window)
            except Empty:
                if build_state != BuildState.NOTHING:
                    self.arbitrary_waiting_value += 1
                    self.PROGRESS_BAR_MAX += 1
                    self.update_progress_bar(window)
                    sleep(0.1)
                pass
            else:
                self.update_dialogue(self.queue_handler.format(line))

        window.close()
        quit(self.return_code)

    def init_build_directories(self, root):
        self.run_command_with_output([self.libs[NPX_LOCATION] + self.cmd_extension, "create-electron-app", str(root)])

    def build_directories(self, root):
        # lets make a file in root that has
        self.logger.info("Building lock file at " + str(Path(root).joinpath(DETAILS_FILE_NAME)))
        self.create_lock_file(root)
        src_dir = root.joinpath(ELECTRON_SOURCE_DIR)
        self.copy_files(src_dir)

    def copy_files(self, root):
        # copy the source files over
        pd_path = Path(self.project[PROJ_DIR])
        html_path = Path(self.project[PROJ_HTML])
        self.logger.info(
            "Copying the source files over from " + str(pd_path) + " to " + str(root.joinpath(pd_path.name)))
        shutil.copytree(pd_path, root.joinpath(pd_path.name))
        # copy and rename the main html file
        self.logger.info(
            "Copying the main HTML file over from " + str(html_path) + " to " + str(root.joinpath("index.html")))
        shutil.copy(html_path, root.joinpath("index.html"))

    def build_new(self):
        pod_path = Path(self.project[PROJ_PARENT_DIR])
        project_dir = pod_path.joinpath(self.project[PROJ_NAME])
        self.logger.info("Building project into " + str(project_dir))
        if project_dir.is_dir():
            # Warn the user that the directory exists and no project was detected
            sg.Popup("A directory already exists here and cannot be used.\nPlease select a different directory")
        else:
            project_dir.mkdir()
            self.init_build_directories(project_dir)
        return project_dir

    def update_dialogue(self, message, append=True):
        message = message.rstrip()
        # print(message)  # shadow
        ansi_list = self.cut_ansi_string_into_parts(message)
        for ansi_item in ansi_list:
            if ansi_item[1] == 'Reset':
                ansi_item[1] = None
            self.dialogue_box.update(ansi_item[0] + '\n', text_color_for_value=ansi_item[1],
                                     background_color_for_value=ansi_item[2], append=True,
                                     autoscroll=True)
        # self.dialogue_box.update(message, append=append)

    def activate_buttons(self, win):
        win["BUILDBUTTON"].update(disabled=False)
        win["BUILDWEBBUTTON"].update(disabled=False)
        win["UPDATEBUTTON"].update(disabled=False)

    def update_widgets(self, win):
        for k, v in self.libs.items():
            if k in win.AllKeysDict:
                win[str(k)].update(str(v))
        for k, v in self.project.items():
            if k in win.AllKeysDict:
                win[str(k)].update(str(v))
        for k, v in self.author.items():
            if k in win.AllKeysDict:
                win[str(k)].update(str(v))

    def update_dictionaries(self, values):
        if values != None:
            for k, v in self.libs.items():
                if k in values:
                    self.libs[k] = values[str(k)]
            for k, v in self.project.items():
                if k in values:
                    self.project[k] = values[str(k)]
            for k, v in self.author.items():
                if k in values:
                    self.author[k] = values[str(k)]
            self.project[PROJ_BUILD_DIR] = str(Path(self.project[PROJ_PARENT_DIR]).joinpath((self.project[PROJ_NAME])))

    def update_progress_bar(self, win):
        bar = win["PROGRESSBAR"]
        bar.UpdateBar(self.arbitrary_waiting_value, self.PROGRESS_BAR_MAX)

    def reset_progress_bar(self, win):
        bar = win["PROGRESSBAR"]
        self.arbitrary_waiting_value = 0
        self.PROGRESS_BAR_MAX = 100
        bar.UpdateBar(0, self.PROGRESS_BAR_MAX)

    # Taken from
    # https://github.com/PySimpleGUI/PySimpleGUI/blob/master/DemoPrograms/Demo_Script_Launcher_ANSI_Color_Output.py
    def cut_ansi_string_into_parts(self, string_with_ansi_codes):
        """
        Converts a string with ambedded ANSI Color Codes and parses it to create
        a list of tuples describing pieces of the input string.
        :param string_with_ansi_codes:
        :return: [(sty, str, str, str), ...] A list of tuples. Each tuple has format: (text, text color, background color, effects)
        """
        color_codes_english = ['Black', 'Red', 'Green', 'Yellow', 'Blue', 'Magenta', 'Cyan', 'White', 'Reset']
        color_codes = ["30m", "31m", "32m", "33m", "34m", "35m", "36m", "37m", "0m"]
        effect_codes_english = ['Italic', 'Underline', 'Slow Blink', 'Rapid Blink', 'Crossed Out']
        effect_codes = ["3m", "4m", "5m", "6m", "9m"]
        background_codes = ["40m", "41m", "42m", "43m", "44m", "45m", "46m", "47m"]
        background_codes_english = ["Black", "Red", "Green", "Yellow", "Blue", "Magenta", "Cyan", "White"]

        ansi_codes = color_codes + effect_codes

        tuple_list = []

        string_list = string_with_ansi_codes.split("\u001b[")

        if (len(string_list)) == 1:
            string_list = string_with_ansi_codes.split("\033[")

        for teststring in string_list:
            if teststring == string_with_ansi_codes:
                tuple_list += [(teststring, None, None, None)]
                break
            if any(code in teststring for code in ansi_codes):
                static_string = None
                color_used = None
                effect_used = None
                background_used = None
                for color in range(0, len(color_codes)):
                    if teststring.startswith(color_codes[color]):
                        working_thread = teststring.split(color_codes[color])
                        ansi_strip = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
                        static_string = ansi_strip.sub('', working_thread[1])
                        color_used = color_codes_english[color]
                for effect in range(0, len(effect_codes)):
                    if teststring.startswith(effect_codes[effect]):
                        working_thread = teststring.split(effect_codes[effect])
                        ansi_strip = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
                        static_string = ansi_strip.sub('', working_thread[1])
                        effect_used = effect_codes_english[effect]
                for background in range(0, len(background_codes)):
                    if teststring.startswith(background_codes[background]):
                        working_thread = teststring.split(background_codes[background])
                        ansi_strip = re.compile(r'\x1B[@-_][0-?]*[ -/]*[@-~]')
                        static_string = ansi_strip.sub('', working_thread[1])
                        background_used = background_codes_english[background]
                try:
                    if not tuple_list[len(tuple_list) - 1][0]:
                        if not tuple_list[len(tuple_list) - 1][1] == None:
                            color_used = tuple_list[len(tuple_list) - 1][1]
                        if not tuple_list[len(tuple_list) - 1][2] == None:
                            background_used = tuple_list[len(tuple_list) - 1][2]
                        if not tuple_list[len(tuple_list) - 1][3] == None:
                            effect_used = tuple_list[len(tuple_list) - 1][3]
                        tuple_list += [(static_string, color_used, background_used, effect_used)]
                    else:
                        tuple_list += [(static_string, color_used, background_used, effect_used)]
                except Exception:
                    tuple_list += [(static_string, color_used, background_used, effect_used)]

        new_tuple_list = []

        for x in range(0, len(tuple_list)):
            if tuple_list[x][0]:
                new_tuple_list += [(tuple_list[x][0], tuple_list[x][1], tuple_list[x][2], tuple_list[x][3])]

        return new_tuple_list


if __name__ == '__main__':
    b = Builder()
    b.main()
