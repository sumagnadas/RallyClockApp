from peewee import CharField, IntegerField, TimeField, DateField, SqliteDatabase, Model

db = SqliteDatabase("logfile.db")

class EventLog(Model):
    carno = IntegerField()
    type = CharField()
    date = DateField()
    time = TimeField()

    class Meta:
        database = db

if db.get_tables() == []:
    EventLog.create_table()