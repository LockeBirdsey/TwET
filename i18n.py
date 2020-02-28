import gettext


from core import resource_path

localedir = resource_path('locale')
translate = gettext.translation('twet', localedir, fallback=True)
_ = translate.gettext
