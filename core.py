import subprocess
import platform
import sys
from threading import Thread
import constants


class Core:
    ON_POSIX = 'posix' in sys.builtin_module_names
    log_queue = None

    libs = {
        "npm_location": "",
        "npx_location": "",
        "tweego_location": ""}

    project = {
        "name": "",
        "directory": "",
        "html": "",
        "output_directory": ""
    }
    # The central YATE class
    system_type = platform.system()

    # System dependent variables
    which_command = "which"

    if system_type is "Windows":
        which_command = "where"

    def enqueue_output(self, out, queue):
        for line in iter(out.readline, b''):
            queue.put(line)
        out.close()

    def get_bin_path(self, app_name):
        try:
            proc = self.test_existence(app_name)
            location = proc.stdout.split("\n")[0].strip()
            print(app_name + " found at " + location)
            return location
        except AssertionError:
            print(app_name + " was not found")
            return ""
            # We have a result, now grab the first line of output
            # Windows note: the first location returned /tends/ to be the binary itself

    def run_command(self, commands):
        process = subprocess.Popen(commands, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, shell=True, bufsize=0,
                                   text=None)
        t = Thread(target=self.enqueue_output, args=(process.stdout, self.log_queue))
        t.daemon = True
        t.start()
        return t

    def find_dependencies(self):
        self.libs["npm_location"] = self.get_bin_path(constants.NPM)
        self.libs["npx_location"] = self.get_bin_path(constants.NPX)
        self.libs["tweego_location"] = self.get_bin_path(constants.TWEEGO)  # Still need to test for StoryFormats

    def test_existence(self, app_name):
        the_process = subprocess.run([self.which_command, app_name], universal_newlines=True,
                                     stdout=subprocess.PIPE, stderr=subprocess.PIPE, shell=True)
        assert (the_process.stderr is '')
        return the_process
