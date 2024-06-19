'''
This script contains the different screens/views which
are shown to user as they interact with the app
'''

from kivy.app import App
from kivy.base import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu
from kivy.graphics import Color, RoundedRectangle
from models import EventLog, settings_file
import base
from gspread import service_account
from datetime import datetime
from configparser import ConfigParser

Builder.load_file("pages.kv")
settings = ConfigParser()
settings.read(settings_file)
if settings.read(settings_file) == []:
    settings['SETTINGS'] = {'stage': "Time Control In",
                            'day': '1',
                            'stg_no': '1'}
    with open(settings_file,'w') as f:
            settings.write(f)

class Home(Screen):
    '''Class for the Home page which is shown on opening the app'''
    tm1 = ObjectProperty(None)
    tm2 = ObjectProperty(None)
    loc_but = ObjectProperty(None)
    sheet = None

    def __init__(self, **kw):
        Clock.schedule_interval(self.update_clock, 0.1)
        super().__init__(**kw)

    def _btnchg(self, obj,i):
        '''Changes the color of the RoundedButton when pressed(due to custom layout, there is no appearance change of button when it is pressed by the user)'''

        with obj.canvas:
            App.get_running_app()._color[i] = Color(200/255, 200/255, 200/255,0.9)
            App.get_running_app()._rect[i] = RoundedRectangle(pos=obj.pos, size=obj.size)

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
        '''
        Uploads the data to the Google Sheets where itcan be downloaded from and post-processed
        '''

        if not self.sheet:
            self.sheet = service_account(filename='credentials.json').open("Rally Clock Data").sheet1
        EventLog.upload(self.sheet)
        self._btnchg(obj, 5)

    def on_set(self, obj):
        print("settings")
        self._btnchg(obj, 6)
        print(obj)

    def update_clock(self, dt):
        time = datetime.now()
        self.tm1.text = time.strftime("%H:%M")
        self.tm2.text = time.strftime("%S")

class SetPage(SettingsWithNoMenu):
    pass

class StageSel(Screen):
    '''Class for Stage, Rally Day selection Screen'''

    day = ObjectProperty(None)
    show_stg_sel = BooleanProperty(True) # Whether to show the dropdown for Stage No. Selection or not
    stg_sel = ObjectProperty(None) # Layout/Widget for Stage No. Selection dropdown
    stg_sel_drop = ObjectProperty(None) # Dropdown Widget for Stage No. Selection dropdown
    stg_sel_text = ObjectProperty(None)  # Text for Stage No. Selection dropdown
    box = ObjectProperty(None) # Layout/Widget Containing all the children widgets for this screen

    def __init__(self, **kw):
        super().__init__(**kw)

        self.stg_sel_drop.text = settings['SETTINGS']['stg_no']
        self.stage.text = settings['SETTINGS']['stage']
        self.day.text = settings['SETTINGS']['day']

    def on_stage(self, value):
        '''
        Show different text or hide the stage no/regroup no selection dropdown widget altogether according
        to the selection of current stage. Also show the Stage, Day no, Stage no. on the Home Screen.
        '''

        s = value.split(" ") # This variable is used to show the text on the home screen according to the stage and day no.
        s = s[0][0] + s[1][0]

        list1 = ("Rally Start of the day" , "Rally Finish of the day")
        list2 = ("Start of Special Stage", "Arrival in Special Stage", "Finish of Special Stage","Time Control IN")
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
                if value != 'Time Control IN':
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

        settings['SETTINGS']['stage'] = value
        with open(settings_file,'w') as f:
            settings.write(f)

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
            settings['SETTINGS']['day'] = day_no
            app.loc_but.text = string[:10] + day_no + string[11:]

        # if current stage has changed
        elif curr_stg:
            app.loc_but.text = string[:12] + curr_stg + string[14:]

        # if stage no./regroup no has changed (not present when at stage "Rally Start" or "Rally Finish")
        elif stg_no:
            settings['SETTINGS']['stg_no'] = stg_no
            string = string[:-2] + f'{int(stg_no):02}'
            app.loc_but.text = string

        if not curr_stg:
            with open(settings_file,'w') as f:
                settings.write(f)

        # if the stage no/regroup no selection widget wasnt present but the button text still has stage no., this will remove it.
        # on the other hand, if the stage no/regroup no selection widget is present but the button text doesnt have stage no., this will add it
        if not self.stg_sel in self.box.children and app.loc_but.text[-1].isnumeric():
            app.loc_but.text = app.loc_but.text[:-3]
        elif self.stg_sel in self.box.children and not app.loc_but.text[-1].isnumeric():
            app.loc_but.text = app.loc_but.text + f"-{int(self.stg_sel_drop.text):02}"

    def on_no(self, value):
        self.but_text_ch(stg_no=value)

class Page3(Screen):
    '''Class for the Page3 Screen'''

    rv = ObjectProperty(None)
    def __init__(self, **kw):
        '''Initial input of the records to the RecycleView from the log file'''

        super().__init__(**kw)
        for i in EventLog.select():
            self.rv.data.insert(0,{'tm':i.time, 'carno':str(i.carno)})

    def on_capture(self, time):
        '''Adds the new row to the RecycleView(at the top) and to the logfile database(at the end)'''

        # The button text for the Stage Selection button also acts as an
        # identifier for the stage in which the time was captured so
        # it is added to the database for further verification during the results
        loc = App.get_running_app().loc_but.text
        loc = loc.split('\n')
        loc = loc[1]

        row = EventLog.insert(carno=0,location=loc,date=time.date(), time=time.time())
        row.execute()
        self.rv.data.insert(0, {'tm': time.time(),'carno': '0'})
        self.manager.get_screen("Log").reload()

class ViewLog(Screen):
    rv = ObjectProperty(None)
    def __init__(self, **kw):
        super().__init__(**kw)

        # Adds all the events present in the logfile
        log = EventLog.select()
        for i in log:
            self.rv.data.insert(0,{'tm':i.time, 'carno':str(i.carno), 'date':str(i.date), 'row':i})
        self.prev_log = log if log.count() else None

    def reload(self, row = None):
        '''Adds the row into the Log Screen after a data capture is done of any event type (starting/finish)'''

        new_log = EventLog.select()

        if self.prev_log:# if there was data in the logfile
            for i in new_log:
                if i not in self.prev_log:
                    self.rv.data.insert(0,{'tm':i.time, 'carno':str(i.carno), 'date':str(i.date), 'row':i})
        else:# if there were no data in the logfile and new data was just added
            for i in new_log:
                self.rv.data.insert(0,{'tm':i.time, 'carno':str(i.carno), 'date':str(i.date), 'row':i})

        # this is added for change in any kind of data in a pre-existing record
        if row:
            for i in self.rv.data:
                if row == i['row']:
                    index = self.rv.data.index(i)
                    self.rv.data[index]= {'tm': row.time, 'date': str(row.date), 'carno': str(row.carno), 'row': i['row']}
        self.prev_log = new_log