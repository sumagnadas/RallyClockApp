'''
This script contains the different screens/views which
are shown to user as they interact with the app
'''

from kivy.app import App
from kivy.base import Builder
from kivy.clock import Clock
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from kivy.graphics import Color, RoundedRectangle
from models import EventLog
from base import Dialog, settings, offset
from gspread import service_account
from datetime import datetime, timedelta
from ntplib import NTPClient, NTPException

ntp = NTPClient()

Builder.load_file("pages.kv")

class Home(Screen):
    '''Class for the Home page which is shown on opening the app'''
    tm1 = ObjectProperty(None)
    tm2 = ObjectProperty(None)
    loc_but = ObjectProperty(None)
    sheet = None
    prev_offset = ObjectProperty(0)
    upcount = ObjectProperty(0)
    last_up_time = ObjectProperty(None)
    up_info = ObjectProperty(f'Upload()')

    def __init__(self, **kw):
        up_count = settings.getint('SETTINGS','up_count')
        if up_count:
            self.last_up_time = datetime.strptime(settings['SETTINGS']['last_up_time'],'%d/%m/%y %H:%M:%S')
        self.upcount = up_count
        self.chg_text()
        Clock.schedule_interval(self.update_clock, 0.1)
        super().__init__(**kw)

    def _btnchg(self, obj,i):
        '''Changes the color of the RoundedButton when pressed(due to custom layout, there is no appearance change of button when it is pressed by the user)'''

        with obj.canvas:
            App.get_running_app()._color[i] = Color(200/255, 228/255, 244/255,0.5)
            App.get_running_app()._rect[i] = RoundedRectangle(pos=obj.pos, size=obj.size)

    def on_b3(self, obj):
        '''Goes to Page3 Screen'''

        self.manager.current = "Page3"
        self._btnchg(obj, 2)

    def on_b4(self, obj):
        '''Goes to Log Screen'''

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
        Dialog(self, 'Done Uploading').show()
        now = datetime.now()
        self.last_up_time = now
        self.upcount +=1
        self.chg_text()
        settings['SETTINGS']['up_count'] = str(self.upcount)
        settings['SETTINGS']['last_up_time'] = now.strftime("%d/%m/%y %H:%M:%S")
        settings.write()
        self._btnchg(obj, 5)

    def on_set(self, obj):
        self.manager.current = "Settings"
        print("settings")
        self._btnchg(obj, 6)
        print(obj)

    def chg_text(self):
        self.up_info = f'Upload({self.upcount})'
        print("up_count:", self.upcount)
        if self.upcount:
            self.up_info += f"\nLast: {self.last_up_time.strftime('%H:%M:%S')}"
        print(self.upcount)
        print(self.up_info)


    def update_clock(self, dt):
        t1 = datetime.now()
        tm = datetime.now() + timedelta(seconds=offset,microseconds=self.prev_offset)
        t2 = datetime.now()
        self.prev_offset = (t2 - t1).microseconds
        time = tm.time()
        self.tm1.text = time.strftime("%H:%M")
        self.tm2.text = time.strftime("%S")

class SetPage(Screen):
    use_ll = ObjectProperty(None)
    use_rt = ObjectProperty(None)
    def __init__(self, **kw):
        super().__init__(**kw)
        self.use_ll.active = settings.getboolean('SETTINGS','use_ll')
        self.use_rt.active = settings.getboolean('SETTINGS','use_rt')

    def erase_log(self):
        EventLog.delete().execute()
        self.manager.get_screen("Log").rv.data = list()
        self.manager.get_screen("Page3").rv.data = list()

        home = self.manager.get_screen('Home')
        home.up_count = 0
        settings['SETTINGS']['up_count'] = str(0)
        settings.write()
        home.chg_text()

        Dialog(self, 'Done Erasing').show()

    def on_ll_active(self,value):
        settings['SETTINGS']['use_ll'] = str(value)
        settings.write()

    def on_rt_active(self,value):
        settings['SETTINGS']['use_rt'] = str(value)
        settings.write()

    def sync(self):
        try:
            response = ntp.request('pool.ntp.org')
            global offset
            offset = response.offset
            print(offset)
            settings['SETTINGS']['offset'] = str(offset)
            settings.write()
            Dialog(self, '-Done-').open()
        except NTPException:
            Dialog(self, "Done").open()

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
        settings.write()

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
            settings.write()

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
    prev_offset = ObjectProperty(0)
    def __init__(self, **kw):
        '''Initial input of the records to the RecycleView from the log file'''

        super().__init__(**kw)
        for i in EventLog.select():
            self.rv.data.insert(0,{'tm':i.time, 'carno':'' if not i.carno else str(i.carno), 'LL': i.LL, 'is_rtm':i.is_rtm,'rtm':i.rtime})

    def on_capture(self, time):
        '''Adds the new row to the RecycleView(at the top) and to the logfile database(at the end)'''

        # The button text for the Stage Selection button also acts as an
        # identifier for the stage in which the time was captured so
        # it is added to the database for further verification during the results
        loc = App.get_running_app().loc_but.text
        loc = loc.split('\n')
        loc = loc[1]
        t1 = datetime.now()
        tm = time + timedelta(seconds=offset,microseconds=self.prev_offset)
        t2 = datetime.now()
        self.prev_offset = (t2 - t1).microseconds

        row = EventLog.insert(carno='',location=loc,date=time.date(), time=tm.time())
        row.execute()
        self.rv.data.insert(0, {'tm': tm.time(),'carno': '', 'LL':False, 'is_rtm': False,'rtm': None})
        self.manager.get_screen("Log").reload()

        home = self.manager.get_screen('Home')
        home.up_count = 0
        settings['SETTINGS']['up_count'] = str(0)
        settings.write()
        home.chg_text()

class ViewLog(Screen):
    rv = ObjectProperty(None)
    def __init__(self, **kw):
        super().__init__(**kw)

        # Adds all the events present in the logfile
        # (only the row object from the database is added from which the data is sourced)
        log = EventLog.select()
        for i in log:
            self.rv.data.insert(0,{'row':i})
        self.prev_log = log if log.count() else None

    def reload(self, row = None):
        '''Adds the row into the Log Screen after a data capture is done of any event type (starting/finish)'''

        new_log = EventLog.select()

        if self.prev_log:# if there was data in the logfile
            for i in new_log:
                if i not in self.prev_log:
                    self.rv.data.insert(0,{'row':i})
        else:# if there were no data in the logfile and new data was just added
            for i in new_log:
                self.rv.data.insert(0,{'row':i})

        # this is added for change in any kind of data in a pre-existing record
        if row:
            for i in self.rv.data:
                if row == i['row']:
                    index = self.rv.data.index(i)
                    self.rv.data.pop(index)
                    self.rv.data.insert(index,{'row':row})
        self.prev_log = new_log