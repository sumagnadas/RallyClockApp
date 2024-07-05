'''
This script contains the different screens/views which
are shown to user as they interact with the app
'''

from kivy.app import App
from kivy.base import Builder
from kivy.properties import ObjectProperty, BooleanProperty
from kivy.uix.screenmanager import Screen
from models import EventLog
from base import Dialog, UploadPopup
from gspread import service_account
import globals
from datetime import datetime
from ntplib import NTPClient, NTPException

ntp = NTPClient()
time_servers = ['time.google.com', # Stratum 1
                'time.facebook.com', # Stratum 1
                'time.apple.com', # Stratum 1
                'pool.ntp.org', # Stratum 2
                'time.cloudflare.com']# Stratum 2

Builder.load_file("pages.kv")

class Home(Screen):
    '''Class for the Home page which is shown on opening the app'''

    tm1 = ObjectProperty(None) # Hours, Minutes label of the clock on Home screen
    tm2 = ObjectProperty(None) # Minutes label of the clock on Home screen
    loc_but = ObjectProperty(None) # Stage selection screen button
    sheet = None # Google sheet to which the data is going to be uploaded
    upcount = ObjectProperty(0) # Number of uploads since last change
    last_up_time = ObjectProperty(None) # Recent upload time
    up_info = ObjectProperty(f'Upload(0)') # text on the upload button
    tm = ObjectProperty(datetime(1,1,1,0,0,0)) # Stores the time for the home clock

    def __init__(self, **kw):

        globals.update_objs.append(self)
        up_count = globals.settings.getint('SETTINGS','up_count')
        globals.settings.add_callback(self.chg_text,'SETTINGS','up_count')
        if up_count:
            self.last_up_time = datetime.strptime(globals.settings['SETTINGS']['last_up_time'],'%d/%m/%y %H:%M:%S')
        self.chg_text(val=up_count) # changes the upload button to include relevant info

        super().__init__(**kw)

    def on_log(self, obj):
        '''Goes to Log Screen'''

        self.manager.get_screen("Log").reload()
        self.manager.current = "Log"

    def upload(self):
        UploadPopup(self.on_upload).open()

    def on_upload(self,name):
        '''
        Uploads the data to the Google Sheets where itcan be downloaded from and post-processed
        '''

        if not self.sheet:
            self.sheet = service_account(filename='credentials.json').open("Rally Clock Data").sheet1
        EventLog.upload(self.sheet,name)
        Dialog(self, 'Done Uploading').show()
        now = datetime.now()
        self.last_up_time = now
        globals.settings['SETTINGS']['last_up_time'] = now.strftime("%d/%m/%y %H:%M:%S")
        globals.settings['SETTINGS']['up_count'] = str(self.upcount)
        globals.settings['SETTINGS']['up_name'] = name
        globals.settings.write()
        return 0

    def chg_text(self,s = None,k = None,val = None):
        '''
        Changes the text of the Upload button to include extra data like number of
        upload attempts and last upload time
        '''
        upcount = int(val)
        self.up_info = f'Upload({upcount})'
        if upcount:
            self.up_info += "\n" + self.last_up_time.strftime('%H:%M:%S')

    def on_tm(self, ins, val):
        '''Adds an offset to the local time to sync it to the NTP server'''

        self.tm1.text = self.tm.strftime("%H:%M")
        self.tm2.text = self.tm.strftime("%S")

class SetPage(Screen):
    '''Class for Settings/More Options screen which contains several options for using the app'''

    use_ll = ObjectProperty(None) # State of Use Lifeline slider
    use_rt = ObjectProperty(None) # State of Use Restart time slider
    sync_but = ObjectProperty(None) # Sync Button

    def __init__(self, **kw):
        super().__init__(**kw)

        self.use_ll.active = globals.settings.getboolean('SETTINGS','use_ll')
        self.use_rt.active = globals.settings.getboolean('SETTINGS','use_rt')

        self.on_offset('SETTINGS','offset', globals.offset) # Change the offset if it is present
        globals.settings.add_callback(self.on_offset, 'SETTINGS','offset')

    def erase_log(self):
        EventLog.delete().execute()
        self.manager.get_screen("Page3").rv.data = list() # Clear the Time Capture Screen

        # Reset the upload count and info (not in sync with last uploaded data)
        globals.settings['SETTINGS']['up_count'] = str(0)
        globals.settings.write()

        Dialog(self, 'Done Erasing').show()

    def on_ll_active(self,value):
        globals.settings['SETTINGS']['use_ll'] = str(value)
        globals.settings.write()

    def on_rt_active(self,value):
        globals.settings['SETTINGS']['use_rt'] = str(value)
        globals.settings.write()

    def on_offset(self,sec,key,value):
        self.sync_but.text = f'Sync\nOffset from local time: {float(value):.02f}s'

    def sync(self):
        '''Sync the time to an NTP server'''

        for server in time_servers: # try different servers for time syncing
            try:
                response = ntp.request(server)
                globals.offset = response.offset
                print(server)
                globals.settings['SETTINGS']['offset'] = str(globals.offset)
                globals.settings.write()
                Dialog(self, '-Done-').open()
                return 0 # exit the function if the time was synced
            except NTPException:
                continue
        Dialog(self, "Done").open() # For debugging purposes (only shown if the time couldn't be synced)
        return 1

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

        self.stg_sel_drop.text = globals.settings['SETTINGS']['stg_no']
        self.stage.text = globals.settings['SETTINGS']['stage']
        self.day.text = globals.settings['SETTINGS']['day']

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

        globals.settings['SETTINGS']['stage'] = value
        globals.settings.write()

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
            globals.settings['SETTINGS']['day'] = day_no
            app.loc_but.text = string[:10] + day_no + string[11:]

        # if current stage has changed
        elif curr_stg:
            app.loc_but.text = string[:12] + curr_stg + string[14:]

        # if stage no./regroup no has changed (not present when at stage "Rally Start" or "Rally Finish")
        elif stg_no:
            globals.settings['SETTINGS']['stg_no'] = stg_no
            string = string[:-2] + f'{int(stg_no):02}'
            app.loc_but.text = string

        if not curr_stg:
            globals.settings.write()

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
        tm = globals.synced_time.time()

        row = EventLog.insert(carno='',location=loc,date=time.date(), time=tm)
        row.execute()
        self.rv.data.insert(0, {'tm': tm,'carno': '', 'LL':False, 'is_rtm': False,'rtm': None})
        self.manager.get_screen("Log").reload()

        globals.settings['SETTINGS']['up_count'] = str(0)
        globals.settings.write()

class ViewLog(Screen):
    '''Log screen'''
    rv = ObjectProperty(None)
    def reload(self):
        '''Adds the row into the Log Screen after a data capture is done of any event type (starting/finish)'''

        log = EventLog.select()

        self.rv.data = list()
        for i in log:
            self.rv.data.insert(0,{'carno':i.carno,'rtime':i.rtime,'tm':i.time,'LL':i.LL,'is_rtm':i.is_rtm})