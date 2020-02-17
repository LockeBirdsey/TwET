import json
import subprocess
import platform
import sys
import threading
from datetime import datetime
from queue import Queue
from threading import Thread
from constants import *


class Core:
    log_queue = None

    def __init__(self):
        self.log_queue = Queue()

    ON_POSIX = 'posix' in sys.builtin_module_names

    LIB_DICT_NAME = "libs"
    PROJECT_DICT_NAME = "project"
    AUTHOR_DICT_NAME = "author"
    UPDATED_TIME_KEY = "last_updated_at"
    BUILD_DIR_KEY = "build_directory"
    libs = {
        NPM_LOCATION: "",
        NPX_LOCATION: "",
        TWEEGO_LOCATION: ""
    }

    project = {
        PROJ_NAME: "",
        PROJ_DIR: "",
        PROJ_HTML: "",
        PROJ_PARENT_DIR: "",
        PROJ_BUILD_DIR: "",
        PROJ_VERSION: "",
        PROJ_DIMS: "",
        PROJ_ICON_LOCATION: "",
        PROJ_KEYWORDS: "",
        PROJ_LAST_UPDATED: ""
    }

    author = {
        AUTHOR_NAME: "",
        AUTHOR_EMAIL: "",
        AUTHOR_REPO: "",
    }

    entry_size = (20, 1)
    # The central YATE class
    system_type = platform.system()

    # System dependent variables
    which_command = "which"
    shell = False

    lock = threading.Lock()

    if system_type is "Windows":
        which_command = "where"
        shell = True

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(str(line, encoding="utf-8"))
        out.close()
        self.lock.release()

    def get_bin_path(self, app_name):
        try:
            proc = self.test_existence(app_name)
            location = proc.split("\n")[0].strip()
            return app_name, location
        except AssertionError:
            return app_name, ""
            # We have a result, now grab the first line of output
            # Windows note: the first location returned /tends/ to be the binary itself

    def run_command_with_output(self, commands):
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=False,
                                   bufsize=0, text=None)
        t = Thread(target=self.enqueue_output, args=(process.stdout, self.log_queue))
        self.lock.acquire(blocking=False)
        t.start()

    def find_dependencies(self):
        res = self.get_bin_path(NPM)
        self.libs[NPM_LOCATION] = res[1]
        self.lib_warning(res)

        res = self.get_bin_path(NPX)
        self.libs[NPX_LOCATION] = res[1]
        self.lib_warning(res)

        res = self.get_bin_path(TWEEGO)
        self.libs[TWEEGO_LOCATION] = res[1]
        self.lib_warning(res)  # Still need to test for StoryFormats

    def lib_warning(self, app):
        name = app[0]
        state = app[1]
        if state is not "":
            self.log_queue.put(name + " found at " + state)
        else:
            self.log_queue.put(name + " was unable to be located.")

    def test_existence(self, app_name):
        the_process = subprocess.run([self.which_command, app_name], universal_newlines=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=self.shell)
        assert (the_process.stderr is '')
        return the_process.stdout

    def create_lock_file(self, path):
        publish_time_stamp = datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        build_dir = str(path)

        # Build the data before writing it to file
        data = {self.UPDATED_TIME_KEY: publish_time_stamp, self.BUILD_DIR_KEY: build_dir,
                self.AUTHOR_DICT_NAME: self.author, self.LIB_DICT_NAME: self.libs, self.PROJECT_DICT_NAME: self.project}
        with open(path.joinpath(DETAILS_FILE_NAME), 'w', encoding="utf-8") as f:
            json.dump(data, fp=f, ensure_ascii=False, indent=4, sort_keys=True)

    def load_lock_file(self, path):
        # returns a tuple of the dictionaries
        # This method ensures that dictionary structure won't be affected
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
            self.libs = data[self.LIB_DICT_NAME]
            self.project = data[self.PROJECT_DICT_NAME]
            self.author = data[self.AUTHOR_DICT_NAME]

    def update_package_json(self, path):
        data = None
        with open(path, 'r', encoding="utf-8") as f:
            data = json.load(f)
            # keywords = data["keywords"]
            data["keywords"] = self.project[PROJ_KEYWORDS].split(",")
            data["author"]["name"] = self.author[AUTHOR_NAME]
            data["author"]["email"] = self.author[AUTHOR_EMAIL]
            data["repository"] = self.author[AUTHOR_EMAIL]
            data["version"] = self.project[PROJ_VERSION]
            data["config"]["forge"]["packagerConfig"] = {"icon": "icon"}
        with open(path, 'w', encoding="utf-8") as f:
            json.dump(data, fp=f, indent=4)
