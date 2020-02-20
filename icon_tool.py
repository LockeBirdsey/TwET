# Resizes the icon and places in the icon directory
# Runs system specific command to make nice icons
import base64
from io import BytesIO
from pathlib import Path

from PIL import Image

import core


class IconTool(core.Core):
    image_path = None
    is_in_base64 = False

    def __init__(self, image_path):
        self.image_path = image_path

    def convert_to_base64(self):
        # img_str = base64.b64encode(buff.getvalue())

        img = Image.open(self.image_path)
        img.thumbnail((256, 256))
        bio = BytesIO()
        img.save(bio, format="PNG")
        del img
        return bio.getvalue()

    def convert(self, output_path, target_system=None):
        src_img = Image.open(self.image_path, 'r')
        if target_system is None:
            target_dims = [16, 32, 64, 128, 256, 512, 1024]
            for i in target_dims:
                new_img = src_img.resize(i, i)
                new_img.save(output_path.joinpath("icon_" + str(i) + "x" + str(i) + ".png"))
        elif target_system == "Windows":
            target_dims = [16, 32, 128, 256, 512]
            src_img.save(output_path.joinpath("icon.ico"), format="ICO")
        elif target_system == "Darwin":
            target_dims = [16, 32, 64, 128, 256, 512, 1024]
            if src_img.mode == "RGBA":
                src_img = src_img.convert("RGB")
            src_img.save(output_path.joinpath("icons.icons"), format="ICNS")
