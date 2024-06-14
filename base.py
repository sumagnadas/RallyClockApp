'''
This script contains the widgets which are used by
one or more of the screens shown in the app
'''

from kivy.app import App
from kivy.base import Builder
from kivy.clock import Clock
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.uix.button import Button
from kivy.uix.label import Label

from re import sub
from datetime import datetime
from models import EventLog

Builder.load_file('base.kv')

class LogRow(RecycleDataViewBehavior, BoxLayout):
    '''Class which is used as the row for displaying the events in the logfile'''

    time = StringProperty("00:00:00")
    carno = StringProperty("0")
    date = StringProperty("01-01-2004")
    type = StringProperty("Test")
    row = ObjectProperty(None)

class NumericInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline=False # set mode of input to single line
        self.input_type='number' # (For android) Show the numeric keyboard for input

    def insert_text(self, substring: str, from_undo=False):
        # If the user enters any character other than number, then it will not be accepted or entered in the input
        s = sub('[^0-9]','',substring)
        return super(NumericInput, self).insert_text(s,from_undo=from_undo)

class RallyRow(RecycleDataViewBehavior, BoxLayout):
    ''' Class which is used as the row for showing data in the Finish data capture list'''

    time = StringProperty("00:00:00")
    carno = StringProperty("0")
    prev_carno = "0"
    row = None
    row_id = NumericProperty(0)

    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        data_rv = rv.data
        self.index = data_rv.index(data)

        # row_index is different because view adds to the top but database adds to the end (if the element is 2nd in view, it will be 2nd last in database)
        self.row_id = len(data_rv) - self.index

        if not self.row:
            # store the row for updating data without searching for the row in database every time
            self.row = EventLog.select().where(EventLog.type=="Finish" and EventLog.time==data['time']).get()

            # set the prev_carno for getting the NumericInput back if user entered duplicate entry and also for finding the index from the RecycleView
            self.prev_carno = str(self.row.carno)

        # the index shound change every time a row is added as the new element is added to the top and index of the elements increases by one
        self.index = data_rv.index(data)

        return super(RallyRow, self).refresh_view_attrs(rv, index, data)
    def on_enter(self):

        app = App.get_running_app()# the app being run
        rv = app.rv# the RecycleView of the Finish screen
        log = app.sm.get_screen("Log")# the Log screen

        if not EventLog.select().where(EventLog.type=="Finish" and EventLog.carno==self.carno).count(): # See if there are any duplicates in the database
            # Find the record with id (auto-incremented integer PK for this table) and corresponding event type and set the carno to new one
            self.row = EventLog.select().where(EventLog.type=="Finish" and EventLog.id==self.row_id).get()
            self.row.carno = self.carno
            self.row.save()

            # Set the new carno in the view
            rv.data[self.index]['carno'] = self.carno

            # Save the new carno in the database and update the prev_carno to the current one
            self.prev_carno = self.carno

            # Reload the Log with the new row changes
            log.reload(row=self.row)
        else:
            # If there is a duplicate, show a popup(Not yet implemented) which confirms whether the user wants to keep it
            # If user confirms to keep it, then the carno will be set in the process in above if condition
            # If user declines, then the carno input will be returned to the previous carno and asked to enter another one
            self.carno = self.prev_carno
            print("Already present. please enter another car no.")

class TimeLabel(Label):
    '''Class for Labels showing only time'''
    time = StringProperty()
    update = BooleanProperty(True) # Checks if the time in the Label is to be updated or not
    def __init__(self, **kwargs):
        self.update = self.update if not 'update' in kwargs.keys() else kwargs['update']

        # Updates the clock every 1/60 seconds (the event is cancelled i.e. the label text is not updated if the update property is False)
        self.event = Clock.schedule_interval(self.update_clock, 1/60)

        super().__init__(**kwargs)

    def on_update(self, instance, value):
        '''Schedule the update_clock event if its not already scheduled and self.update is changed from false to true'''
        if self.update:
            Clock.schedule_interval(self.update_clock, 1/60)
        else:
            self.event.cancel()
            self.time = '00:00:00'

    def update_clock(self, dt):
      '''Sets the Label text to the current time if the update property is true'''
      self.text = str(datetime.now().time())
      self.time = self.text

    def on_time(self, instance, value):
        self.text = self.time

class RoundedButton(Button):
    '''Class for Buttons with rounded corner (styling in kv file)'''
    pass

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = list()
