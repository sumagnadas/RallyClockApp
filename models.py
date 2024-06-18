'''
This module contains the table model for the logfile as well as
connects to the database.
'''
from gspread import service_account
from peewee import BooleanField, CharField, IntegerField, TimeField, DateField, SqliteDatabase, Model
from playhouse.migrate import SqliteMigrator, migrate
from kivy import platform
from os.path import join

# Default file for saving log
db_file = "logfile.db"

# Since the testing is done on a desktop, the path is written for desktop. Hence, the filename is changed
# to an android-compatible path when the app is actually run on an android phone
if platform == "android":
    from android.storage import app_storage_path # This module is only available on android platform
    db_file = join(app_storage_path(), db_file)


db = SqliteDatabase(db_file)
sheet = service_account(filename='credentials.json').open("Rally Clock Data").sheet1

class EventLog(Model):
    '''Basic Structure of the logfile database table'''

    carno = IntegerField()
    location = CharField()
    date = DateField()
    time = TimeField()
    rtime = CharField(default="")
    LL = BooleanField(default=False)

    class Meta:
        database = db

    def upload():
        log = EventLog.select()
        data = list()
        data.append(['Car no.', 'Time', 'Restart Time', 'Lifeline','Location','Date'])
        for i in log:
            data.append([i.carno, str(i.time), i.rtime, 'Yes' if i.LL else 'No', i.location, str(i.date)])
        sheet.append_rows(data)
        print("Done")


if db.get_tables() == []:# if the table doesn't exist, then create one
    EventLog.create_table()

# Backwards compatibility
cols = [i.name for i in db.get_columns('eventlog')]
if 'rtime' not in cols:
    mg = SqliteMigrator(db)
    migrate(mg.add_column('eventlog','rtime',EventLog.rtime),
            mg.add_column('eventlog','LL',EventLog.LL))