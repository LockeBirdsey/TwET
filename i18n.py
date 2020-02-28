import gettext
from pathlib import Path

from core import resource_path

localedir = Path.joinpath(Path(__file__).parent.absolute(), resource_path('locale'))
print("**************************Locale directory: " + str(localedir))
translate = gettext.translation('messages', localedir=localedir, fallback=True)
_ = translate.gettext
