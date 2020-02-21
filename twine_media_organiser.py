import os
import shutil
from pathlib import Path
import re
import core
from constants import *


##
# Decompiles a Twine HTML into Twee
# Parses and locates all media sources (images, audio, video)
# Copies all into a nice new directory
# which can then be used for the ExeGen stuff
##

class TMO(core.Core):
    html_file_path = None
    html_name = None
    relative_root = None
    tweego_path = None
    twee_data = None
    output_dir = None
    audio_files = {}
    image_files = {}
    video_files = {}
    img_dir = None
    audio_dir = None
    video_dir = None
    twee_path = None
    updated_html_path = None

    def __init__(self, html_file, output_dir):
        self.html_file_path = html_file
        self.relative_root = Path(self.html_file_path).parent
        self.html_name = Path(self.html_file_path).stem
        self.tweego_path = self.libs[TWEEGO_LOCATION]
        self.output_dir = Path(output_dir)
        self.img_dir = self.output_dir.joinpath(IMG)
        self.audio_dir = self.output_dir.joinpath(AUDIO)
        self.video_dir = self.output_dir.joinpath(VIDEO)
        self.twee_path = Path(self.output_dir).joinpath(self.html_name + ".twee")
        self.updated_html_path = Path(self.output_dir).joinpath(self.html_name + "_organised.html")

    def run(self):
        self.decompile_to_twee()
        self.locate_media_files()
        self.announce_media_finds()
        self.build_new_dir_structure()
        self.copy_media_files()
        self.replace_media_paths()
        self.write_out_new_source()
        self.convert_to_html()

    def decompile_to_twee(self):
        self.twee_data = self.run_command_store_output([self.tweego_path, "-d", str(self.html_file_path)])

    def locate_media_files(self):
        # need a way to locate media paths and sort based on type
        no_white_text = self.twee_data.split()
        # Find path
        # Check if absolute
        # Add to respective list
        for s in no_white_text:
            s = self.clean_path(s)
            if any(x in s for x in AUDIO_SUFFIXES):
                self.audio_files[s] = s
            if any(x in s for x in IMAGE_SUFFIXES):
                self.image_files[s] = s
            if any(x in s for x in VIDEO_SUFFIXES):
                self.video_files[s] = s

    def announce_media_finds(self):
        self.logger.info("Audio found:")
        for k in self.audio_files:
            self.logger.info(k)
        self.logger.info("Images found:")
        for k in self.image_files:
            self.logger.info(k)
        self.logger.info("Video found:")
        for k in self.video_files:
            self.logger.info(k)

    def build_new_dir_structure(self):
        if not self.output_dir.exists():
            self.output_dir.mkdir()
        if not self.img_dir.exists():
            self.img_dir.mkdir()
        if not self.audio_dir.exists():
            self.audio_dir.mkdir()
        if not self.video_dir.exists():
            self.video_dir.mkdir()

    # Will currently only deal in absolute paths
    # The Sith approach
    def copy_media_files(self):
        try:
            for k, v in self.audio_files.items():
                f = Path(v)
                f_name = f.name
                f_dest = self.audio_dir.joinpath(f_name)
                f_src = v
                if not f.is_absolute():
                    f_src = self.relative_root.joinpath(f)
                shutil.copy(f_src, f_dest)
                self.audio_files[k] = str(f_dest)
            for k, v in self.image_files.items():
                f = Path(v)
                f_name = f.name
                f_dest = self.img_dir.joinpath(f_name)
                f_src = v
                if not f.is_absolute():
                    f_src = self.relative_root.joinpath(f)
                shutil.copy(f_src, f_dest)
                self.image_files[k] = str(f_dest)
            for k, v in self.video_files.items():
                f = Path(v)
                f_name = f.name
                f_dest = self.video_dir.joinpath(f_name)
                f_src = v
                if not f.is_absolute():
                    f_src = self.relative_root.joinpath(f)
                shutil.copy(f_src, f_dest)
                self.video_files[k] = str(f_dest)
        except PermissionError as e:
            self.logger.info(
                "A permissions error has occurred, likely due to overwrite attempt. (" + e.strerror + " with " + e.filename+")")

    # This can be done above
    # But it will happen afterwards in case of failure
    def replace_media_paths(self):
        for k, v in self.audio_files.items():
            self.twee_data = self.twee_data.replace(k, v)
        for k, v in self.image_files.items():
            self.twee_data = self.twee_data.replace(k, v)
        for k, v in self.video_files.items():
            self.twee_data = self.twee_data.replace(k, v)

    def write_out_new_source(self):
        with open(self.twee_path, 'w') as f:
            f.write(self.twee_data)

    def convert_to_html(self):
        self.run_command_store_output([self.tweego_path, str(self.twee_path), "-o ", str(self.updated_html_path)])

    def clean_path(self, string):
        # there's a LOT of cases here
        cleansed = ""
        str_split = string.split("[")
        if len(str_split) == 1:
            str_split = string.split("\"")
            if len(str_split) == 1:
                pass
            else:
                cleansed = self.find_pathlike_in_arr(str_split)
        else:
            cleansed = self.find_pathlike_in_arr(str_split)

        sub_string = '[*?"<>|\[\]]'
        return re.sub(sub_string, '', cleansed)

    def find_pathlike_in_arr(self, arr):
        for i in arr:
            if any(x in i for x in AUDIO_SUFFIXES) or any(x in i for x in VIDEO_SUFFIXES) or any(
                    x in i for x in IMAGE_SUFFIXES):
                return i
        return ""


if __name__ == '__main__':
    test = TMO("C:\\Users\\lollb\\Documents\\Twine\\Stories\\mediatest.html", "C:\\Users\\lollb\\test")
    test.libs[TWEEGO_LOCATION] = str(Path("C:\\Users\\lollb\\bin\\tweego.exe"))
    test.run()
