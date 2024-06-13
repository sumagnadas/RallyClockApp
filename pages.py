from kivy.base import Builder
from kivy.app import App
from kivy.uix.button import Button
from kivy.uix.label import Label
from kivy.uix.screenmanager import Screen
from kivy.uix.settings import SettingsWithNoMenu
from kivy.properties import StringProperty, ObjectProperty, BooleanProperty
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
    time = StringProperty("00:00:00")
    carno = StringProperty("0")
    date = StringProperty("01-01-2004")
    type = StringProperty("Test")
    row = ObjectProperty(None)
    row_carno = StringProperty(None)
    def refresh_view_attrs(self, rv, index, data):
        print(data)
        return super().refresh_view_attrs(rv, index, data)


class NumericInput(TextInput):
    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.multiline=False
        self.input_type='number'
    def insert_text(self, substring: str, from_undo=False):
        s = sub('[^0-9]','',substring)
        return super(NumericInput, self).insert_text(s,from_undo=from_undo)

class RallyRow(RecycleDataViewBehavior, BoxLayout):
    car = ObjectProperty(None)
    time = StringProperty("00:00:00")
    carno = ObjectProperty(None)
    prev_carno = "0"
    row = None
    def refresh_view_attrs(self, rv, index, data):
        ''' Catch and handle the view changes '''
            # As an alternate method of assignment
        data_rv = rv.data
        self.row_index = len(data_rv) - data_rv.index(data)
        self.index = data_rv.index(data)
        if not self.row and hasattr(self, 'index'):
            self.row = EventLog.select().where(EventLog.type=="Finish" and EventLog.id==self.row_index).get()
            self.prev_carno = str(self.row.carno)
        return super(RallyRow, self).refresh_view_attrs(
            rv, index, data)
    def on_enter(self):
        app = App.get_running_app()
        rv = app.rv
        log = app.sm.get_screen("Log")
        if not EventLog.select().where(EventLog.type=="Finish" and EventLog.carno==self.carno).count():
            print(rv.data)
            self.index = rv.data.index({'time': self.time, 'carno':int(self.prev_carno)})
            rv.data[self.index]['carno'] = self.carno
            new_row_index = len(rv.data) - self.index
            if(new_row_index != self.row_index):
                self.row_index = new_row_index
                self.row = self.row = EventLog.select().where(EventLog.type=="Finish" and EventLog.id==self.row_index).get()
            self.row.carno = self.carno
            self.row.save()
            print(self.row_index)
            self.prev_carno = self.carno
            log.reload(row=self.row)
        else:
            self.carno = 0
            print("Already present. please enter another car no.")
class RV(RecycleView):
    def __init__(self, **kwargs):
        super(RV, self).__init__(**kwargs)
        self.data = list()

class TimeLabel(Label):
    time = StringProperty()
    update = BooleanProperty(True)
    def __init__(self, **kwargs):
        self.update = self.update if not 'update' in kwargs.keys() else kwargs['update']
        self.event = Clock.schedule_interval(self.update_clock, 1/60)
        super().__init__(**kwargs)
    def on_update(self, instance, value):
        if self.update:
            Clock.schedule_interval(self.update_clock, 1/60)
        else:
            self.event.cancel()
            self.time = '00:00:00'

    def update_clock(self, dt):
      self.text = str(datetime.now().time())
      self.time = self.text

    def on_time(self, instance, value):
        self.text = self.time

class RoundedButton(Button):
    pass

class Home(Screen):
    loc_but = ObjectProperty(None)
    def _btnchg(self, obj,i):
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
        self.manager.current = "Page3"
        self._btnchg(obj, 2)
    def on_b4(self, obj):
        self.manager.get_screen("Log").reload()
        self.manager.current = "Log"
        self._btnchg(obj, 3)
    def on_b5(self, obj):
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
    day_no = ObjectProperty(None)
    show_stage = BooleanProperty(True)
    extra = ObjectProperty(None)
    extra_drop = ObjectProperty(None)
    extra_text = ObjectProperty(None)
    box = ObjectProperty(None)
    def on_stage(self, value):
        s = value.split(" ")
        s = s[0][0] + s[1][0]
        list1 = ("Rally Start of the day" , "Rally Finish of the day")
        list2 = ("Start of Special Stage", "Arrival in Special Stage", "Finish of Special Stage")
        list3 = ('Service IN', 'Service OUT', 'Regroup IN', 'Regroup OUT')
        if value in list1:
            if self.extra in self.box.children:
                self.show_stage = False
                self.box.remove_widget(self.extra)
        else:
            if self.extra not in self.box.children:
                self.show_stage = True
                self.box.add_widget(self.extra, index=1)
            if value in list2:
                s = value.split(" ")
                s = "S" + s[0][0]
                self.extra_text.text = "Stage No."
                values = [str(i) for i in range(1,31)]
                values.sort(key=int)
                self.extra_drop.values = values
                self.extra_drop.text = values[0]
            elif value in list3:
                self.extra_text.text = "Service/Regroup No."
                values = [str(i) for i in range(1,6)]
                values.sort(key=int)
                self.extra_drop.values = values
                self.extra_drop.text = values[0]
        self.but_text_ch(s2=s)

    def but_text_ch(self, s1="",s2="",s3=""):
        app = App.get_running_app()
        if app.sm.current == "StageSel":
            string = app.loc_but.text
            if s1:
                app.loc_but.text = string[:10] + s1 + string[11:]
            elif s2:
                app.loc_but.text = string[:12] + s2 + string[14:]
            elif s3:
                if string[-1].isnumeric():
                    string = string[:-1] + s3
                    app.loc_but.text = string
                else:
                    string = string + f'-{s3}'
                    app.loc_but.text = string
            if not self.extra in self.box.children and app.loc_but.text[-1].isnumeric():
                app.loc_but.text = app.loc_but.text[:-2]
            elif self.extra in self.box.children and not app.loc_but.text[-1].isnumeric():
                app.loc_but.text = app.loc_but.text + f"-{self.extra_drop.text}"

    def on_no(self, value):
        self.but_text_ch(s3=value)

class Page3(Screen):
    rv = ObjectProperty(None)
    def __init__(self, **kw):
        super().__init__(**kw)
        for i in EventLog.select().where(EventLog.type=="Finish"):
            self.rv.data.insert(0,{'time':str(i.time), 'carno':i.carno})
    def on_capture(self, time):
        print(time)
        row = EventLog.create(carno=0,type="Finish",date=time.date(), time=time.time())
        row.save()
        self.rv.data.insert(0, {'time': str(time.time()),'carno': '0'})

class ViewLog(Screen):
    rv = ObjectProperty(None)
    def __init__(self, **kw):
        super().__init__(**kw)
        for i in EventLog.select():
            self.rv.data.insert(0,{'time':str(i.time), 'carno':str(i.carno), 'date':str(i.date), 'type':i.type, 'row':i})
        self.prev_log = EventLog.select()

    def reload(self, row = None):
        new_log = EventLog.select()
        if self.prev_log:
            for i in new_log:
                if i not in self.prev_log:
                    self.rv.data.insert(0,{'time':str(i.time), 'carno':str(i.carno), 'date':str(i.date), 'type':i.type, 'row':i})
        else:
            for i in new_log:
                self.rv.data.insert(0,{'time':str(i.time), 'carno':str(i.carno), 'date':str(i.date), 'type':i.type, 'row':i})
        if row:
            for i in self.rv.data:
                if row == i['row']:
                    print(row.time)
                    print(i['row'])
                    index = self.rv.data.index(i)
                    print(self.rv.data[index])
                    self.rv.data[index]['time'] = str(row.time)
                    self.rv.data[index]['date'] = str(row.date)
                    self.rv.data[index]['carno'] = str(row.carno)
                    self.rv.data[index]['type'] = row.type
                    print(self.rv.data[index])
        self.prev_log = new_log