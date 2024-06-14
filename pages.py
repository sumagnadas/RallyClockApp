from kivy.base import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty, NumericProperty
from kivy.clock import Clock
from kivy.uix.recycleview import RecycleView
from kivy.uix.recycleview.views import RecycleDataViewBehavior
from kivy.uix.boxlayout import BoxLayout
from kivy.uix.textinput import TextInput
from kivy.graphics import Color, RoundedRectangle
from re import sub
from datetime import datetime
from models import EventLog

Builder.load_file("pages.kv")

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
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = list()

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

class Home(Screen):
    '''Class for the Home page which is shown on opening the app'''

    loc_but = ObjectProperty(None)

    def _btnchg(self, obj,i):
        '''Changes the color of the RoundedButton when pressed(due to custom layout, there is no appearance change of button when it is pressed by the user)'''

        with obj.canvas:
            App.get_running_app()._color[i] = Color(200/255, 200/255, 200/255,0.9)
            App.get_running_app()._rect[i] = RoundedRectangle(pos=obj.pos, size=obj.size)

    def on_b1(self, obj):
        print("button1")
        self._btnchg(obj, 0)
        print(obj)

    def on_b2(self, obj):
        print("button2")
        self._btnchg(obj, 1)
        print(obj)

    def on_b3(self, obj):
        '''Goes to Page3 Screen'''

        self.manager.current = "Page3"
        self._btnchg(obj, 2)

    def on_b4(self, obj):
        '''Goes to Log Screen'''

        self.manager.get_screen("Log").reload()
        self.manager.current = "Log"
        self._btnchg(obj, 3)

    def on_b5(self, obj):
        '''Goes to Stage Selection Screen'''
        self.manager.current = "StageSel"
        self._btnchg(obj, 4)

    def on_b6(self, obj):
        print("button4c")
        self._btnchg(obj, 5)
        print(obj)

    def on_set(self, obj):
        print("settings")
        self._btnchg(obj, 6)
        print(obj)

class SetPage(SettingsWithNoMenu):
    pass

class StageSel(Screen):
    '''Class for Stage, Rally Day selection Screen'''

    show_stg_sel = BooleanProperty(True) # Whether to show the dropdown for Stage No. Selection or not
    stg_sel = ObjectProperty(None) # Layout/Widget for Stage No. Selection dropdown
    stg_sel_drop = ObjectProperty(None) # Dropdown Widget for Stage No. Selection dropdown
    stg_sel_text = ObjectProperty(None)  # Text for Stage No. Selection dropdown
    box = ObjectProperty(None) # Layout/Widget Containing all the children widgets for this screen

    def on_stage(self, value):
        '''
        Show different text or hide the stage no/regroup no selection dropdown widget altogether according
        to the selection of current stage. Also show the Stage, Day no, Stage no. on the Home Screen.
        '''

        s = value.split(" ") # This variable is used to show the text on the home screen according to the stage and day no.
        s = s[0][0] + s[1][0]

        list1 = ("Rally Start of the day" , "Rally Finish of the day")
        list2 = ("Start of Special Stage", "Arrival in Special Stage", "Finish of Special Stage")
        list3 = ('Service IN', 'Service OUT', 'Regroup IN', 'Regroup OUT')

        # Dont show stage no./regroup no. selection widget if the stage is "Rally Start" or "Rally Finish"
        if value in list1:
            if self.stg_sel in self.box.children:
                self.show_stg_sel = False
                self.box.remove_widget(self.stg_sel)
        else:
            if self.stg_sel not in self.box.children: # show the widget again if it wasnt already shown
                self.show_stg_sel = True
                self.box.add_widget(self.stg_sel, index=1)

            # Keeping the text format of the button on the home screen similar to the NRS app
            if value in list2:
                # button text format stuff
                s = value.split(" ")
                s = "S" + s[0][0]

                # Change the dropdown label text and dropdown values according to the value selected
                self.stg_sel_text.text = "Stage No."
                values = [str(i) for i in range(1,31)]
                values.sort(key=int)
                self.stg_sel_drop.values = values
                self.stg_sel_drop.text = values[0]
            elif value in list3:
                # Change the dropdown label text and dropdown values according to the value selected
                self.stg_sel_text.text = "Service/Regroup No."
                values = [str(i) for i in range(1,6)]
                values.sort(key=int)
                self.stg_sel_drop.values = values
                self.stg_sel_drop.text = values[0]

        # Change button text format for the middle portion
        self.but_text_ch(curr_stg=s)

    def but_text_ch(self, day_no="",curr_stg="",stg_no=""):
        '''
        Change the Stage selection button text with a format similar to that of NRS app

        Button text format:"Location
                            D{day_no}-{curr_stg}-{stg_no}"
        '''

        app = App.get_running_app()
        string = app.loc_but.text

        # if day no. has changed
        if day_no:
            app.loc_but.text = string[:10] + day_no + string[11:]

        # if current stage has changed
        elif curr_stg:
            app.loc_but.text = string[:12] + curr_stg + string[14:]

        # if stage no./regroup no has changed (not present when at stage "Rally Start" or "Rally Finish")
        elif stg_no:
            string = string[:-1] + stg_no
            app.loc_but.text = string

        # if the stage no/regroup no selection widget wasnt present but the button text still has stage no., this will remove it.
        # on the other hand, if the stage no/regroup no selection widget is present but the button text doesnt have stage no., this will add it
        if not self.stg_sel in self.box.children and app.loc_but.text[-1].isnumeric():
            app.loc_but.text = app.loc_but.text[:-2]
        elif self.stg_sel in self.box.children and not app.loc_but.text[-1].isnumeric():
            app.loc_but.text = app.loc_but.text + f"-{self.stg_sel_drop.text}"

    def on_no(self, value):
        self.but_text_ch(stg_no=value)

class Page3(Screen):
    '''Class for the Page3 Screen'''

    rv = ObjectProperty(None)
    def __init__(self, **kw):
        '''Initial input of the records to the RecycleView from the log file'''

        super().__init__(**kw)
        for i in EventLog.select().where(EventLog.type=="Finish"):
            self.rv.data.insert(0,{'time':str(i.time), 'carno':str(i.carno)})

    def on_capture(self, time):
        '''Adds the new row to the RecycleView(at the top) and to the logfile database(at the end)'''

        row = EventLog.insert(carno=0,type="Finish",date=time.date(), time=time.time())
        row.execute()
        self.rv.data.insert(0, {'time': str(time.time()),'carno': '0'})
        self.manager.get_screen("Log").reload()

class ViewLog(Screen):
    rv = ObjectProperty(None)
    def __init__(self, **kw):
        super().__init__(**kw)

        # Adds all the events present in the logfile
        log = EventLog.select()
        for i in log:
            self.rv.data.insert(0,{'time':str(i.time), 'carno':str(i.carno), 'date':str(i.date), 'type':i.type, 'row':i})
        self.prev_log = log if log.count() else None

    def reload(self, row = None):
        '''Adds the row into the Log Screen after a data capture is done of any event type (starting/finish)'''

        new_log = EventLog.select()
        print(new_log.count())

        if self.prev_log:# if there were data in the logfile
            for i in new_log:
                if i not in self.prev_log:
                    self.rv.data.insert(0,{'time':str(i.time), 'carno':str(i.carno), 'date':str(i.date), 'type':i.type, 'row':i})
                    print(self.rv.data)
        else:# if there were no data in the logfile and new data was just added
            for i in new_log:
                self.rv.data.insert(0,{'time':str(i.time), 'carno':str(i.carno), 'date':str(i.date), 'type':i.type, 'row':i})
                print(self.rv.data)

        # this is added for change in any kind of data in a pre-existing record
        if row:
            for i in self.rv.data:
                if row == i['row']:
                    index = self.rv.data.index(i)
                    self.rv.data[index]= {'time': str(row.time), 'date': str(row.date), 'carno': str(row.carno), 'type': row.type, 'row': i['row']}
        self.prev_log = new_log