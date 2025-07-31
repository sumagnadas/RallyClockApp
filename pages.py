"""
This script contains the different screens/views which
are shown to user as they interact with the app
"""

from datetime import datetime

from jnius import autoclass
from kivy.base import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty
from kivy.uix.screenmanager import Screen
from ntplib import NTPClient, NTPException

import globals
from android import mActivity
from base import Dialog

ntp = NTPClient()
time_servers = [
    "time.google.com",  # Stratum 1
    "time.facebook.com",  # Stratum 1
    "time.apple.com",  # Stratum 1
    "pool.ntp.org",  # Stratum 2
    "time.cloudflare.com",  # Stratum 2
]

Builder.load_file("pages.kv")


class Home(Screen):
    """Class for the Home page which is shown on opening the app"""

    # Hours, Minutes label of the clock on Home screen
    tm1 = ObjectProperty(None)
    tm2 = ObjectProperty(None)  # Minutes label of the clock on Home screen
    # Stores the time for the home clock
    tm = ObjectProperty(datetime(1, 1, 1, 0, 0, 0))
    fl = ObjectProperty("No")
    sync_done = ObjectProperty("No")
    _timer = [None]

    def __init__(self, **kw):

        globals.update_objs.append(self)
        globals.settings.add_callback(self.on_sync, "SETTINGS", "last_sync_time")
        self.on_sync(None, None, globals.settings["SETTINGS"]["last_sync_time"])
        delay = 0.1
        self._timer = Clock.schedule_interval(self.check_airpl, delay)

        super().__init__(**kw)

    def check_airpl(self, dt):
        Global = autoclass("android.provider.Settings$Global")
        is_airpl = Global.getString(
            mActivity.getContentResolver(), Global.AIRPLANE_MODE_ON
        )
        self.fl = "Yes" if int(is_airpl) else "No"

    def on_sync(self, s, k, v):
        dt_ob = datetime.strptime(v, "%d/%m/%y %H:%M:%S.%f")
        self.sync_done = "No" if datetime.today().date() > dt_ob.date() else "Yes"

    def on_tm(self, ins, val):
        """Adds an offset to the local time to sync it to the NTP server"""

        self.tm1.text = self.tm.strftime("%H:%M")
        self.tm2.text = self.tm.strftime("%S")


class SetPage(Screen):
    """Class for Settings/More Options screen which contains several options for using the app"""

    use_ll = ObjectProperty(None)  # State of Use Lifeline slider
    use_rt = ObjectProperty(None)  # State of Use Restart time slider
    sync_but = ObjectProperty(None)  # Sync Button
    tm = ObjectProperty(None)
    version = ObjectProperty("0.0")

    def __init__(self, **kw):
        super().__init__(**kw)

        # self.use_ll.active = globals.settings.getboolean("SETTINGS", "use_ll")
        # self.use_rt.active = globals.settings.getboolean("SETTINGS", "use_rt")

        # Change the offset if it is present
        self.on_offset("SETTINGS", "offset", globals.offset)
        globals.settings.add_callback(self.on_offset, "SETTINGS", "offset")
        self.version = kw["version"]

    def on_offset(self, sec, key, value):
        self.sync_but.text = f"Sync\nOffset from local time: {float(value):.02f}s"

    def sync(self):
        """Sync the time to an NTP server"""

        for server in time_servers:  # try different servers for time syncing
            try:
                response = ntp.request(server)
                globals.offset = response.offset
                globals.settings["SETTINGS"]["offset"] = str(globals.offset)
                globals.settings["SETTINGS"][
                    "last_sync_time"
                ] = datetime.now().strftime("%d/%m/%y %H:%M:%S.%f")
                globals.settings.write()
                Dialog(self, "-Done-").open()
                return 0  # exit the function if the time was synced
            except NTPException:
                continue
        # For debugging purposes (only shown if the time couldn't be synced)
        Dialog(self, "Done").open()
        return 1
