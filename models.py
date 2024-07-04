'''
This module contains the table model for the logfile as well as
connects to the database.
'''
from peewee import BooleanField, CharField, IntegerField, TimeField, DateField, SqliteDatabase, Model
from playhouse.migrate import SqliteMigrator, migrate
from kivy import platform
from os.path import join

# Default file for saving log
db_file = "logfile.db"
settings_file = "settings.ini"

# Since the testing is done on a desktop, the path is written for desktop. Hence, the filename is changed
# to an android-compatible path when the app is actually run on an android phone
if platform == "android":
    from android.storage import app_storage_path # This module is only available on android platform
    storage = app_storage_path()
    db_file = join(storage, db_file)
    settings_file = join(storage, settings_file)

db = SqliteDatabase(db_file)

class EventLog(Model):
    '''Basic Structure of the logfile database table'''

    carno = IntegerField()
    location = CharField()
    date = DateField()
    time = TimeField()
    rtime = TimeField(null=True)
    LL = BooleanField(default=False)
    is_rtm = BooleanField(default=False)

    class Meta:
        database = db

    def upload(sheet):
        log = EventLog.select()
        data = list()
        data.append(['Car no.', 'Time', 'Restart Time', 'Lifeline','Location','Date'])
        for i in log:
            rtime = str(i.rtime) if i.is_rtm else ''
            LL = 'Yes' if i.LL else 'No'
            data.append(['' if not i.carno else str(i.carno), str(i.time), rtime, LL, i.location, str(i.date)])
        sheet.append_rows(data)


if db.get_tables() == []:# if the table doesn't exist, then create one
    EventLog.create_table()

# Backwards compatibility
cols = [i.name for i in db.get_columns('eventlog')]
if 'rtime' in cols:
    mg = SqliteMigrator(db)
    migrate(mg.alter_column_type('eventlog','rtime',TimeField(null=True)))