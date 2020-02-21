import core
from constants import *


## Decompiles a Twine HTML into Twee
## Parses and locates all media sources (images, audio, video)
## Copies all into a nice new directory
## which can then be used for the ExeGen stuff


class TMO(core.Core):
    html_file_path = None
    tweego_path = None
    twee_data = None

    def __init__(self, html_file):
        self.html_file_path = html_file
        self.tweego_path = self.libs[TWEEGO_LOCATION]

    def run(self):
        pass

    def decompile_to_twee(self):
        self.twee_data = self.run_command_store_output([self.tweego_path, "-d", str(self.html_file_path)])

    def locate_media_files(self):
        audio_files = []
        image_files = []
        video_files = []
        # need a way to locate media paths and sort based on type

    def build_new_dir_structure(self):
        pass

    def copy_media_files(self):
        pass

    def replace_media_paths(self):
        pass

    def write_out_new_source(self):
        pass