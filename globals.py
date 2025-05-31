from datetime import datetime, timedelta

from kivy.base import Builder
from kivy.config import ConfigParser

from models import settings_file

Builder.load_file("base.kv")
settings = ConfigParser()
settings.read(settings_file)
if settings.sections() == []:
    settings["SETTINGS"] = {
        "stage": "Time Control In",
        "day": "1",
        "stg_no": "1",
        "use_ll": "True",
        "offset": "0",
        "up_count": "0",
        "use_rt": "True",
        "start_time": "1",
        "last_sync_time": "31/01/22 23:59:59.999999",
    }
    settings.write()

# Backwards Compatibility
if "use_ll" not in settings.options("SETTINGS"):
    settings["SETTINGS"]["use_ll"] = "True"
    settings.write()

if "offset" not in settings.options("SETTINGS"):
    settings["SETTINGS"]["offset"] = "0"
    settings.write()

if "up_count" not in settings.options("SETTINGS"):
    settings["SETTINGS"]["up_count"] = "0"
    settings.write()

if "use_rt" not in settings.options("SETTINGS"):
    settings["SETTINGS"]["use_rt"] = "True"
    settings.write()

if "start_time" not in settings.options("SETTINGS"):
    settings["SETTINGS"]["start_time"] = "1"
    settings.write()

if "last_sync_time" not in settings.options("SETTINGS"):
    settings["SETTINGS"]["last_sync_time"] = "31/01/22 23:59:59.999999"
    settings.write()

offset = settings.getfloat("SETTINGS", "offset")
prev_offset = (
    0  # offset due to the addition of timedelta object (see update_clock function)
)
update_objs = list()  # list of objects which contain a clock or code involving clock
synced_time = datetime(1, 1, 1, 1, 1, 1)  # Time object synced with NTP server


def showhide_widget(widget, hide=True):
    if not hide:
        if hasattr(widget, "saved_attrs"):
            widget.height = widget.saved_attrs[0]
            widget.size_hint_y = widget.saved_attrs[1]
            widget.opacity = widget.saved_attrs[2]
            widget.disabled = widget.saved_attrs[3]
    elif hide:
        if not widget.disabled:
            print(
                f"meow:{(widget.height,widget.size_hint_y,widget.opacity,widget.disabled,)}"
            )
            widget.saved_attrs = (
                widget.height,
                widget.size_hint_y,
                widget.opacity,
                widget.disabled,
            )
            (widget.height, widget.size_hint_y, widget.opacity, widget.disabled) = (
                0,
                None,
                0,
                True,
            )


def update_clock(dt):
    """Adds an offset to the local time to sync it to the NTP server"""

    global prev_offset, offset, synced_time, update_objs
    t1 = datetime.now()
    synced_time = datetime.now() + timedelta(seconds=offset, microseconds=prev_offset)
    t2 = datetime.now()

    # when the timedelta object is added, the process can take some time(in microseconds order)
    # and hence a lag occurs in the time (even if very little)
    # Further accumulation of this delay can offset the time by seconds, or even minutes
    # To counteract this, the previous offset is saved which is added on the next run
    # An offset is still there as adding on the same run will make it kind of like a paradox as
    # then there will be another offset and so on
    prev_offset = (t2 - t1).microseconds
    for obj in update_objs:
        obj.tm = synced_time.time()
