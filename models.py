'''
This module contains the table model for the logfile as well as
connects to the database.
'''

from peewee import CharField, IntegerField, TimeField, DateField, SqliteDatabase, Model

db = SqliteDatabase("logfile.db")

class EventLog(Model):
    '''Basic Structure of the logfile database table'''

    carno = IntegerField()
    type = CharField()
    date = DateField()
    time = TimeField()

    class Meta:
        database = db

if db.get_tables() == []:# if the table doesn't exist, then create one
    EventLog.create_table()