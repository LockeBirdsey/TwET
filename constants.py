from enum import Enum


class BuildState(Enum):
    NOTHING = 1
    UPDATING = 2
    BUILDING_NEW = 3
    BUILDING_WEB = 4
    SETUP = 5
    PENDING = 6;


NPM = "npm"
NPX = "npx"
TWEEGO = "tweego"
DETAILS_FILE_NAME = "tweget.json"
YARN_PACKAGE_FILE = "package.json"

# Keys
## Lib keys
NPM_LOCATION = "npm_location"
NPX_LOCATION = "npx_location"
TWEEGO_LOCATION = "tweego_location"

## Project keys
PROJ_NAME = "name"
PROJ_DIR = "directory"
PROJ_HTML = "html"
PROJ_PARENT_DIR = "output_directory"
PROJ_BUILD_DIR = "build_directory"
PROJ_VERSION = "version"
PROJ_DIMS = "dimensions"
PROJ_ICON_LOCATION = "icon_location"
PROJ_KEYWORDS = "keywords"
PROJ_LAST_UPDATED = "last_updated"

## Author Keys
AUTHOR_NAME = "Name"
AUTHOR_EMAIL = "Email"
AUTHOR_REPO = "Repository"
