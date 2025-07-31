"""
This module contains the table model for the logfile as well as
connects to the database.
"""

from os.path import join

from kivy import platform

settings_file = "settings.ini"

# Since the testing is done on a desktop, the path is written for desktop. Hence, the filename is changed
# to an android-compatible path when the app is actually run on an android phone
if platform == "android":
    from android.storage import (
        app_storage_path,  # This module is only available on android platform
    )

    storage = app_storage_path()
    settings_file = join(storage, settings_file)
