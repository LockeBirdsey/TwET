from configparser import ConfigParser

from constants import *


class SettingsManager:
    # Settings will typically live in working directory/twet.ini
    f_name = "twet.ini"
    libs_key = 'libraries'
    config = None

    def __init__(self):
        self.config = ConfigParser()
        self.config.read(self.f_name)

    # Write out settings
    def write_out_settings(self, libs):
        config = self.config
        if not config.has_section(self.libs_key):
            config.add_section(self.libs_key)
        # Prevent blank writing
        if self.is_safe(NPX, libs[NPX_LOCATION]):
            config.set(self.libs_key, NPX, libs[NPX_LOCATION])
        if self.is_safe(NPM, libs[NPM_LOCATION]):
            config.set(self.libs_key, NPM, libs[NPM_LOCATION])
        if self.is_safe(TWEEGO, libs[TWEEGO_LOCATION]):
            config.set(self.libs_key, TWEEGO, libs[TWEEGO_LOCATION])

        with open(self.f_name, 'w') as f:
            config.write(f)

    def is_safe(self, key, new_val):
        val = self.find_setting(key)
        if new_val is "" and val is not "":
            return False
        else:
            return True

    # Read in settings
    def read_in_settings(self):
        config = self.config
        if config.has_section(self.libs_key):
            npx_loc = config.get(self.libs_key, NPX)
            npm_loc = config.get(self.libs_key, NPM)
            tweego_loc = config.get(self.libs_key, TWEEGO)
            return npm_loc, npx_loc, tweego_loc
        return None, None, None

    def find_setting(self, key):
        config = self.config
        if config.has_option(self.libs_key, key):
            return config.get(self.libs_key, key)
        else:
            return None
