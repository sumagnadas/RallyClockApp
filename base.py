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
from kivy.uix.popup import Popup
from kivy.uix.modalview import ModalView
from kivy.config import ConfigParser

from datetime import datetime,time
from models import EventLog, settings_file

Builder.load_file('base.kv')
settings = ConfigParser()
settings.read(settings_file)
if settings.sections() == []:
    settings['SETTINGS'] = {'stage': "Time Control In",
                            'day': '1',
                            'stg_no': '1',
                            'use_ll': 'True'}
    settings.write()

if 'use_ll' not in settings.options('SETTINGS'):
    settings['SETTINGS']['use_ll'] = 'True'
    settings.write()
class LLPopup(Popup):
    def __init__(self, row,**kwargs):
        self.row = row
        super().__init__(**kwargs)

class Dialog(ModalView):
    fsz = ObjectProperty(None)
    text = ObjectProperty(None)
    def __init__(self, parent,text,**kwargs):
        super().__init__(**kwargs)
        self.height = parent.height * 0.1
        self.width = parent.width *0.4
        self.text.text = text

    def show(self):
        self.open()
        Clock.schedule_interval(lambda dt: self.dismiss(),5)

class NavigationBar(BoxLayout):
    '''Class for the Navigation Bar in all the screens'''
    pass

class LogRow(RecycleDataViewBehavior, BoxLayout):
    '''Class which is used as the row for displaying the events in the logfile'''

    tm = ObjectProperty(time(0,0,0))
    rtm = ObjectProperty(time(0,0,0),allownone=True)
    is_rtm = BooleanProperty(False)
    carno = StringProperty("0")
    row = ObjectProperty(None)
    LL = BooleanProperty(False)
    use_ll = BooleanProperty(settings.getboolean('SETTINGS','use_ll'))
    ll_row = ObjectProperty(None)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload_ll('SETTINGS','use_ll', None)
        settings.add_callback(self.reload_ll, 'SETTINGS','use_ll')

    def reload_ll(self,section, key,value):
        self.use_ll = settings.getboolean(section,key)
        if not self.use_ll and self.ll_row in self.children:
            self.remove_widget(self.ll_row)
        elif self.use_ll and self.ll_row not in self.children:
            self.add_widget(self.ll_row)

class NumericInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline=False # set mode of input to single line
        self.input_type='number' # (For android) Show the numeric keyboard for input
        self.input_filter='int'

class RallyRow(RecycleDataViewBehavior, BoxLayout):
    ''' Class which is used as the row for showing data in the Finish data capture list'''

    tm = ObjectProperty(time(0,0,0))
    LL = BooleanProperty(False)
    use_ll = BooleanProperty(settings.getboolean('SETTINGS','use_ll'))
    ll_but = ObjectProperty(None)
    is_rtm = BooleanProperty(False)
    rtm = ObjectProperty(time(0,0,0),allownone=True)
    carno = StringProperty("")
    prev_carno = ""
    row = None
    row_id = NumericProperty(0)

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.reload_ll('SETTINGS','use_ll', None)
        settings.add_callback(self.reload_ll, 'SETTINGS','use_ll')
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
        data_rv = rv.data

        # the index shound change every time a row is added as the new element is added to the top and index of the elements increases by one
        self.index = data_rv.index(data)

        # row_index is different because view adds to the top but database adds to the end (if the element is 2nd in view, it will be 2nd last in database)
        row_id = len(data_rv) - self.index
        print(self.row_id)
        print(data)

        if not self.row_id:
            # store the row for updating data without searching for the row in database every time
            row = EventLog.select().where(EventLog.id==row_id).get()

            # set the prev_carno for getting the NumericInput back if user entered duplicate entry and also for finding the index from the RecycleView
            self.prev_carno = str(row.carno)

        self.row_id=row_id

        return super(RallyRow, self).refresh_view_attrs(rv, index, data)

    def on_enter(self):

        app = App.get_running_app()# the app being run
        rv = app.rv# the RecycleView of the Finish screen
        log = app.sm.get_screen("Log")# the Log screen

        if not EventLog.select().where(EventLog.carno==self.carno).count(): # See if there are any duplicates in the database
            # Find the record with id (auto-incremented integer PK for this table) and corresponding event type and set the carno to new one
            row = EventLog.select().where(EventLog.id==self.row_id).get()
            row.carno = self.carno
            row.save()

            # Set the new carno in the view
            rv.data[self.index]['carno'] = self.carno

            # Save the new carno in the database and update the prev_carno to the current one
            self.prev_carno = self.carno

            # Reload the Log with the new row changes
            log.reload(row=row)
        else:
            # If there is a duplicate, show a popup(Not yet implemented) which confirms whether the user wants to keep it
            # If user confirms to keep it, then the carno will be set in the process in above if condition
            # If user declines, then the carno input will be returned to the previous carno and asked to enter another one
            self.carno = self.prev_carno
            print("Already present. please enter another car no.")

    def on_LL(self,instance, value):
        row = EventLog.select().where(EventLog.id==self.row_id).get()
        row.LL = self.LL
        print(self.LL)
        row.save()
        app = App.get_running_app()
        log = app.sm.get_screen("Log")
        log.reload(row=row)
        print('Lifeline Given')

    def on_ll(self):
        LLPopup(row=self).open()

    def reload_ll(self,section, key,value):
        self.use_ll = settings.getboolean(section,key)
        if not self.use_ll and self.ll_but in self.children:
            self.remove_widget(self.ll_but)
        elif self.use_ll and self.ll_but not in self.children:
            self.add_widget(self.ll_but)

class TimeLabel(Label):
    '''Class for Labels showing only time'''

    tm = ObjectProperty(time(0,0,0))
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
            self.time = time(0,0,0)

    def update_clock(self, dt):
      '''Sets the Label text to the current time if the update property is true'''
      self.tm = datetime.now().time()

    def on_tm(self, instance, value):
        self.text = self.tm.strftime("%H:%M:%S")

class RoundedButton(Button):
    '''Class for Buttons with rounded corner (styling in kv file)'''

    pass

class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = list()
