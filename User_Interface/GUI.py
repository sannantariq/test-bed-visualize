import ttk
import Tkinter as tk
import ScrolledText
import CalenderWidget as CLNDR
import datetime
import time
import json
import User_Client as UC
import webbrowser as web
from tkMessageBox import showwarning

l = ['CPU', 'Memory', 'Bandwidth', 'Ethernet', 'Wifi', 'Bluetooth', 'Power']
filters = ['Desktop/Laptop', 'Smartphone/Tablet', 'Embedded/Other']

SERVER_IP = '86.36.34.202'
SERVER_PORT = 5996

class GUI(tk.Tk):
    def __init__(self, parent, client):
        tk.Tk.__init__(self, parent)
        self.client = client
        self.initialize()

    def update(self):
        data = self.client.listen()
        if data:
            if data[:4] == "URL:":
                url = data[4:]
                self.realtab.realtabshare.set_url(url)
                web.open(url)
            if data[:6] == "STATS:":
                stats = json.loads(data[6:])
                [self.statistic_tab.stats.set_quantity(k, stats[k]) for k in stats.keys()]
            else:
                # self.xy_info.set(data)
                pass
        self.after(1000, self.update)

    def initialize(self):
        self.grid()
        self.client.connect()
        self.note = ttk.Notebook(self)
        self.realtab = Real_Time_Tab(self.note, client = self.client)
        self.statictab = Static_Tab(self.note, client = self.client)
        self.statistic_tab = Statistic_Tab(self)

        self.note.add(self.realtab, text = 'Real Time Plots')
        self.note.add(self.statictab, text = 'Static Plots')
        self.note.add(self.statistic_tab, text = 'Statistics')

        self.note.grid(column = 0, row = 0)
        self.update()

class Device_Filter(ttk.LabelFrame):
    def __init__(self, parent, filter_list):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'Node Selection')
        self.filters = filter_list
        self.val_dict = {}
        self.initialize()

    def initialize(self):
        self.grid()
        self.configure(width = 30)
        s = ttk.Style()
        s.configure('TCheckbutton', anchor = tk.W, width = 30)
        [self.val_dict.update({w : tk.IntVar()}) for w in self.filters]
        self.check_list = [ttk.Checkbutton(self, text = w, variable = self.val_dict[w], style = 'TCheckbutton') for w in self.val_dict.keys()]
        [w.grid(column = 1, row = i) for (i, w) in enumerate(self.check_list, start = 1)]
        ttk.Label(self, text = 'Pick Devices to Plot:', anchor = tk.W, width = 40, background = 'lightgrey').grid(column = 0, row = 0, pady = 5)

    def get_active(self):
        return [w for w in self.val_dict.keys() if self.val_dict[w].get() == 1]

    def disable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.DISABLED)
            except:
                pass

    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.NORMAL)
            except:
                pass
        
        
class Double_Slider(ttk.LabelFrame):
    def __init__(self, parent, low_limit, high_limit):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'Nodes')
        self.low_limit = low_limit
        self.high_limit = high_limit
        self.initialize()

    def check_less(self,val):
        my_val = int(float(val))
        upper_bound = int(float(self.slider2.get()))
        if my_val > upper_bound:
            self.slider.set(upper_bound)
        my_val = int(float(self.slider.get()))
        self.lower.set('From:%4d' % (my_val))

    def check_great(self, val):
        my_val = int(float(val))
        lower_bound = int(float(self.slider.get()))
        if my_val < lower_bound:
            self.slider2.set(lower_bound)
        my_val = int(float(self.slider2.get()))
        self.upper.set('To:   %4d' % (my_val))

    def get_range(self):
        return [int(self.lower.get().split()[1]), int(self.upper.get().split()[1])]

    def disable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.DISABLED)
            except:
                pass
        # [child.configure(state = tk.DISABLED) for child in self.winfo_children()]
        # self.slider.configure(state = tk.DISABLED)

    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.NORMAL)
            except:
                pass

    def initialize(self):
        self.grid()
        self.lower = tk.StringVar()
        self.upper = tk.StringVar()

        self.lower.set('From:%4d' % (self.low_limit))
        self.upper.set('To:   %4d' % (self.high_limit))

        low_label = ttk.Label(self, textvariable = self.lower, width = 10, anchor = tk.W)
        up_label = ttk.Label(self, textvariable = self.upper, width = 10, anchor = tk.W)

        self.slider = ttk.Scale(self, from_ = self.low_limit, to = self.high_limit, value = self.low_limit, orient = tk.HORIZONTAL,  command = self.check_less)
        self.slider2 = ttk.Scale(self, from_ = self.low_limit, to = self.high_limit, value = self.high_limit, orient = tk.HORIZONTAL, command = self.check_great)
        
        self.slider.grid(column = 1, row = 1)
        self.slider2.grid(column = 1, row = 2)
        low_label.grid(column = 2, row = 1, padx = 4)
        up_label.grid(column = 2, row = 2, padx = 4)
        ttk.Label(self, text = 'Node Range:', anchor = tk.W, width = 45, background = 'lightgrey').grid(column = 0, row = 0)


class Metric_Check(ttk.LabelFrame):
    def __init__(self, parent, val_list):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'Metrics')
        self.val_list = val_list
        self.val_dict = {}
        self.initialize()

    def initialize(self):
        self.grid()
        self.configure(width = 30)
        s = ttk.Style()
        s.configure('TCheckbutton', anchor = tk.W, width = 30)
        [self.val_dict.update({w : tk.IntVar()}) for w in self.val_list]
        self.check_list = [ttk.Checkbutton(self, text = w, variable = self.val_dict[w], style = 'TCheckbutton') for w in self.val_dict.keys()]
        [w.grid(column = 1, row = i) for (i, w) in enumerate(self.check_list, start = 1)]
        ttk.Label(self, text = 'Pick Metrics to Plot:', anchor = tk.W, width = 40, background = 'lightgrey').grid(column = 0, row = 0, pady = 5)

    def get_active(self):
        return [w for w in self.val_dict.keys() if self.val_dict[w].get() == 1]

    def disable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.DISABLED)
            except:
                pass

    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.NORMAL)
            except:
                pass

class Value_Scroller(tk.Frame):
    def __init__(self, parent, range):
        tk.Frame.__init__(self, parent)
        self.low = range[0]
        self.high = range[1]
        self.current_val = (-self.low + self.high) / 2

        self.initialize()

    def increase(self):
        # print "UP", self.current_val
        self.current_val = ((self.current_val + 1) % (self.high - self.low))
        self.update_entry_box()

    def decrease(self):
        self.current_val = ((self.current_val - 1) % (self.high - self.low))
        self.update_entry_box()

    def update_entry_box(self):
        self.entry_box.delete(0, tk.END)
        self.entry_box.insert(0, str(self.current_val + self.low))

    def isOkay(self):
        current = self.entry_box.get()
        try:
            current = int(current)
            if current < self.high and current >= self.low:
                self.current_val = current - self.low
                self.update_entry_box()
                return True
            self.update_entry_box()
            return False
        except:
            self.update_entry_box()
            return False

    def get(self):
        return int(self.entry_box.get())

    def initialize(self):
        self.grid()
        okayCommand = self.register(self.isOkay)

        self.entry_box = ttk.Entry(self, width = 2, validate = 'focusout', validatecommand = (okayCommand))
        # self.entry_box = ttk.Entry(self, width = 2)

        self.update_entry_box()
        s = ttk.Style()
        s.configure('TButton', width = 2)
        # s.configure('TEntry', width = 2)
        self.up_button = ttk.Button(self, command = self.increase, text = '+')
        self.down_button = ttk.Button(self, command = self.decrease, text = '-')

        self.up_button.grid(column = 0, row = 0)
        self.down_button.grid(column = 0, row = 2)
        self.entry_box.grid(column = 0, row = 1)

class Date_Entry(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.initialize()

    def get_date(self):
        date_time = self.calendar.selection
        if date_time == None:
            date = datetime.datetime.now().strftime('%Y-%m-%d')
            return date
        date = date_time.strftime('%Y-%m-%d')
        return date

    def initialize(self):
        self.grid()
        self.calendar = CLNDR.Calendar(self)
        self.calendar.grid(column = 0, row = 0)

        # test = ttk.Button(self, command = self.get_date, text = 'Test')
        # test.grid(column = 0, row = 1)


class Time_Entry(tk.Frame):
    def __init__(self, parent, clock = '12'):
        tk.Frame.__init__(self, parent)
        self.clock = clock
        if self.clock == '24':
            self.initialize24()
        else:
            self.initialize12()

    def get_time(self):
        hours = self.Hour_entry.get()
        mins = self.Minute_entry.get()
        secs = self.Second_entry.get()

        if self.clock == '12':
            if self.zone_val == 'PM':
                hours = (hours % 12) + 12
            else:
                hours = hours % 12

        return_val = '%.2d:%.2d:%.2d' % (hours, mins, secs)
        # print return_val
        return return_val

    def isOkay(self):
        val = self.zone.get()
        if val in ['AM', 'A', 'a', 'am']:
            self.zone.set('AM')
            self.zone_val = 'AM'
            return True
        elif val in ['PM', 'P', 'p', 'pm']:
            self.zone.set('PM')
            self.zone_val = 'PM'
            return True
        else:
            self.zone.set(self.zone_val)
            return False

    def initialize12(self):
        self.grid()
        self.Hour_entry = Value_Scroller(self, range = [1, 13])
        self.Minute_entry = Value_Scroller(self, range = [0, 60])
        self.Second_entry = Value_Scroller(self, range = [0, 60])
        self.zone_val = 'AM'

        okayCommand = self.register(self.isOkay)
        self.zone = ttk.Combobox(self, values = ['AM', 'PM'], validatecommand = (okayCommand), validate = 'focusout', width = 4)
        self.zone.set(self.zone_val)

        HMS_label = ttk.Label(self, text = 'H   :   M   :   S', anchor = tk.W)
        xpadding = 2
        self.Hour_entry.grid(column = 0, row = 1, padx = xpadding)
        self.Minute_entry.grid(column = 1, row = 1, padx = xpadding)
        self.Second_entry.grid(column = 2, row = 1, padx = xpadding)
        self.zone.grid(column = 3, row = 1)
        HMS_label.grid(column = 0, row = 0, columnspan = 3)

        # self.print_button = ttk.Button(self, text = 'Print Time', command = self.get_time)
        # self.print_button.grid(column = 3, row = 1)


    def initialize24(self):
        self.grid()
        self.Hour_entry = Value_Scroller(self, range = [1, 13])
        self.Minute_entry = Value_Scroller(self, range = [0, 60])
        self.Second_entry = Value_Scroller(self, range = [0, 60])

        HMS_label = ttk.Label(self, text = 'H : M : S')

        self.Hour_entry.grid(column = 0, row = 0)
        self.Minute_entry.grid(column = 1, row = 0)
        self.Second_entry.grid(column = 2, row = 0)
        HMS_label.grid(column = 0, row = 0, columnspan = 3)

        # self.print_button = ttk.Button(self, text = 'Print Time', command = self.get_time)
        # self.print_button.grid(column = 3, row = 1)


class Date_Time_Widget(tk.Frame):
    def __init__(self, parent, clock = '12'):
        tk.Frame.__init__(self, parent)
        self.clock = clock
        self.initialize()

    def initialize(self):
        self.grid()
        self.time_widget = Time_Entry(self, clock = self.clock)
        self.date_widget = Date_Entry(self)

        ttk.Label(self, text = 'Pick Date and Time', anchor = tk.W).grid(column = 0, row = 0, columnspan = 2)
        self.date_widget.grid(column = 0, row = 1)
        self.time_widget.grid(column = 1, row = 1, padx = 5)

        ttk.Button(self, text = 'OK', width = 5)

        # test = ttk.Button(self, text = 'Test', command = self.get_date_time)
        # test.grid(column = 0, row = 1)

    def get_date_time(self):
        return '%s %s' % (self.date_widget.get_date(), self.time_widget.get_time())


class Date_Time_Win(tk.Toplevel):
    def __init__(self, parent, clock = '12'):
        tk.Toplevel.__init__(self, parent)
        self.clock = clock
        self.parent = parent
        self.protocol('WM_DELETE_WINDOW', self.close)
        self.initialize()

    def close(self):
        self.parent.set_date_time(self.dtwidget.get_date_time())
        self.parent.open_button.configure(state = tk.NORMAL)
        # print self.parent.get_date_time()
        self.destroy()

    def initialize(self):
        self.grid()
        self.dtwidget = Date_Time_Widget(self, clock = self.clock)
        ttk.Button(self, text = 'OK', width = 5, command = self.close).grid(column = 0, row = 1)
        self.dtwidget.grid(column = 0, row = 0)

class DTControl(tk.Frame):
    def __init__(self, parent, clock = '12', entry_label = 'Start Time:'):
        tk.Frame.__init__(self, parent)
        self.clock = clock
        self.date_time = None
        self.entry_label = entry_label
        self.initialize()

    def open_calendar(self):
        self.new_win = Date_Time_Win(self, clock = self.clock)
        self.open_button.configure(state = tk.DISABLED)

    def set_date_time(self, dt):
        self.date_time = dt
        self.timevar.set(self.entry_label + ' ' + self.date_time)

    def get_date_time(self):
        return self.date_time

    def disable(self):
        [child.configure(state = tk.DISABLED) for child in self.winfo_children()]

    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.NORMAL)
            except:
                pass

    def initialize(self):
        self.grid()
        self.timevar = tk.StringVar()
        self.timevar.set(self.entry_label + ' -')
        self.timelabel = ttk.Label(self, textvariable = self.timevar, width = 62, anchor = tk.W, background = 'lightgrey')
        self.open_button = ttk.Button(self, text = 'Pick', width = 10, command = self.open_calendar)
        ypadding = 2
        self.timelabel.grid(column = 0, row = 0, pady = ypadding)
        self.open_button.grid(column = 1, row = 1, pady = ypadding)

class Maxpoint_Scale(ttk.LabelFrame):
    def __init__(self, parent, low_limit, high_limit):
        ttk.LabelFrame.__init__(self, parent)
        self.low_limit = low_limit
        self.high_limit = high_limit
        self.configure(text = 'Maxpoint Label')
        self.initialize()

    def get_maxpoints(self):
        return self.var.get()

    def disable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.DISABLED)
            except:
                pass

    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.NORMAL)
            except:
                pass

    def update_label(self, val):
        val = int(float(val))
        self.var.set('%7d' % (val))

    def initialize(self):
        self.grid()
        self.var = tk.StringVar()
        mid = (self.low_limit + self.high_limit) / 2
        self.var.set('%7d' % mid)
        self.scale = ttk.Scale(self, from_ = self.low_limit, to = self.high_limit, value = mid, command = self.update_label)
        self.scale.grid(column = 1, row = 1)
        ttk.Label(self, textvariable = self.var, width = 10).grid(column = 2, row = 1, padx = 10)
        ttk.Label(self, text = 'Maximum Points to show on Plot:', background = 'lightgrey', width = 44).grid(column = 0, row = 0)


class Add_Shared(ttk.LabelFrame):
    def __init__(self, parent):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'Add Shared Control')
        self.parent = parent
        self.initialize()

    def disable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.DISABLED)
            except:
                pass

    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.NORMAL)
            except:
                pass

    def add_button_pressed(self):
        self.parent.parent.realtabcons.enable()
        self.parent.parent.realtab.disable()
        self.client.send_command(json.dumps(send_cmd))
        # self.disable()

    def remove_button_pressed(self):
        self.parent.parent.realtab.enable()
        self.parent.parent.realtabcons.disable()
        self.client.send_command(json.dumps(send_cmd))
        #self.enable()

    def initialize(self):
        self.grid()
        url_label = ttk.Label(self, text = 'Enter URL here:', width = 20, background = 'lightgrey')
        self.url_entry = ttk.Entry(self, width = 42)
        self.url_add_button = ttk.Button(self, text = 'Add', command = self.add_button_pressed, width = 10)
        self.url_remove_button = ttk.Button(self, text = 'Remove', command = self.remove_button_pressed, width = 10)
        url_label.grid(column = 0, row = 0, padx = 10)
        self.url_entry.grid(column = 1, row = 0, padx = 10)
        self.url_add_button.grid(column = 2, row = 0, padx = 10, pady = 5)
        self.url_remove_button.grid(column = 2, row = 1, padx = 10, pady = 5)


class Real_Time_Tab_options(ttk.LabelFrame):
    def __init__(self, parent, client, clock = '12', metrics = [], node_range = [0, 100]):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'New Plot')
        self.clock = clock
        self.metrics = metrics
        self.node_range = node_range
        self.parent = parent
        self.client = client
        self.initialize()

    def disable(self):
        for child in self.winfo_children():
            try:
                child.disable()
            except:
                child.configure(state = tk.DISABLED)

    def enable(self):
        for child in self.winfo_children():
            try:
                child.enable()
            except:
                child.configure(state = tk.NORMAL)

    def start_button_press(self):
        self.disable()
        # time.sleep(5)
        self.parent.realtabcons.enable()
        self.parent.realtabshare.control_share.disable()
        time = self.date_time.get_date_time()
        metrics = [s.upper() for s in self.metric_box.get_active()]
        maxpoints = int(self.mps.get_maxpoints())
        node_classes = self.node_slide.get_active()
        if (len(metrics) == 0 or len(node_classes) == 0):
            showwarning('Invalid Options', 'Please make sure you have selected at least one metric and atleast one node class', parent = self)
            self.enable()
        else:
            send_cmd = {'cmd' : 'startnew', 'time' : time, 'metrics' : metrics, 'maxpoints' : maxpoints, 'node_classes': node_classes}
            print json.dumps(send_cmd)
            self.client.send_command(json.dumps(send_cmd))

    def initialize(self):
        self.grid()
        self.date_time = DTControl(self, self.clock)
        self.metric_box = Metric_Check(self, val_list = self.metrics)
        # self.node_slide = Double_Slider(self, self.node_range[0], self.node_range[1])
        self.node_slide = Device_Filter(self, filters)
        self.mps = Maxpoint_Scale(self, low_limit = 10, high_limit = 120)
        xpadding = 10
        ypadding = 10
        self.date_time.grid(column = 0, row = 0, padx = xpadding, pady = ypadding)
        self.metric_box.grid(column = 0, row = 1, padx = xpadding, pady = ypadding)
        self.node_slide.grid(column = 0, row = 2, padx = xpadding, pady = ypadding)
        self.mps.grid(column = 0, row = 3, padx = xpadding, pady = ypadding)
        self.start_plot_button = ttk.Button(self, width = 20, text = 'Start Plotting', command = self.start_button_press)
        self.start_plot_button.grid(column = 0, row = 4, pady = ypadding)

class Real_Time_Tab_controls(ttk.LabelFrame):
    def __init__(self, parent, client, clock = '12'):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'Controls')
        self.clock = clock
        self.parent = parent
        self.client = client
        self.initialize()

    def pause(self):
        send_cmd = {'cmd' : 'pause'}
        print send_cmd
        self.client.send_command(json.dumps(send_cmd))

    def resume(self):
        send_cmd = {'cmd' : 'resume'}
        print send_cmd
        self.client.send_command(json.dumps(send_cmd))

    def resume_last(self):
        pass
        self.client.send_command(json.dumps(send_cmd))

    def resume_recent(self):
        send_cmd = {'cmd' : 'gotoend'}
        print send_cmd
        self.client.send_command(json.dumps(send_cmd))

    def seek(self):
        time = self.seek_time_frame.get_date_time()
        send_cmd = {'cmd' : 'goto', 'time' : time}
        print send_cmd
        self.client.send_command(json.dumps(send_cmd))

    def stop_plot(self):
        self.disable()
        self.parent.realtab.enable()
        self.parent.realtabshare.control_share.enable()
        send_cmd = {'cmd' : 'stop'}
        print send_cmd
        self.client.send_command(json.dumps(send_cmd))

    def disable(self):
        for child in self.winfo_children():
            try:
                child.disable()
            except:
                child.configure(state = tk.DISABLED)

    def enable(self):
        for child in self.winfo_children():
            try:
                child.enable()
            except:
                child.configure(state = tk.NORMAL)

    def initialize(self):
        self.grid()
        self.pause_button = ttk.Button(self, text = '||', command = self.pause, width = 10)
        self.resume_button = ttk.Button(self, text = '>', command = self.resume, width = 10)
        self.resume_last_button = ttk.Button(self, text = '>|', command = self.resume_last, width = 10)
        self.resume_recent_button = ttk.Button(self, text = '>>', command = self.resume_recent, width = 10)
        self.seek_button = ttk.Button(self, text = 'Seek', command = self.seek, width = 10)
        self.seek_time_frame = DTControl(self, clock = self.clock, entry_label = 'Go To Time:')
        self.stop_button = ttk.Button(self, text = 'Stop', command = self.stop_plot, width = 10)

        xpadding = 2
        ypadding = 1

        # ttk.Label(self, text = 'Plot Controls').grid(column = 0, row = 0)
        self.seek_time_frame.grid(column = 0, row = 0, pady = 10, columnspan = 4, padx = 10)
        self.seek_button.grid(column = 4, row = 0)
        self.pause_button.grid(column = 0, row = 2, padx = xpadding, pady = ypadding)
        self.resume_button.grid(column = 1, row = 2, padx = xpadding, pady = ypadding)
        self.resume_last_button.grid(column = 2, row = 2, padx = xpadding, pady = ypadding)
        self.resume_recent_button.grid(column = 3, row = 2, padx = xpadding, pady = ypadding)
        self.stop_button.grid(column = 4, row = 2, padx = xpadding, pady = ypadding)

class Real_Time_Tab_share(ttk.LabelFrame):
    def __init__(self, parent, client):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'Share Plot')
        self.parent = parent
        self.client = client
        self.initialize()

    def disable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.DISABLED)
            except:
                pass

    def enable(self):
        for child in self.winfo_children():
            try:
                child.configure(state = tk.NORMAL)
            except:
                pass

    def set_url(self, url):
        self.url.set(url)

    def initialize(self):
        self.url = tk.StringVar()
        self.url_display_entry = ttk.Entry(self, width = 50, textvariable = self.url)
        self.control_share = Add_Shared(self)
        ttk.Label(self, text = 'URL:', width = 30).grid(column = 0, row = 0)

        self.url_display_entry.grid(column = 1, row = 0, columnspan = 2, padx = 5)
        self.control_share.grid(column = 0, row = 1, columnspan = 3, padx = 10, pady = 10)

class Real_Time_Tab(tk.Frame):
    def __init__(self, parent, client):
        tk.Frame.__init__(self, parent)
        self.client = client
        self.initialize()

    def initialize(self):
        self.grid()

        self.realtab = Real_Time_Tab_options(self, clock = '12', metrics = l, client = self.client)
        self.realtabshare = Real_Time_Tab_share(self, client = self.client)
        self.realtabcons = Real_Time_Tab_controls(self, clock = '12', client = self.client)
        self.realtabcons.disable()
        self.realtab.grid(column = 0, row = 0, rowspan = 16, padx = 10)
        self.realtabshare.grid(column = 1, row = 3)
        self.realtabcons.grid(column = 1, row = 0, rowspan = 3, padx = 10)

class Static_Tab_options(ttk.LabelFrame):
    def __init__(self, parent, clock = '12', metrics = [], node_range = [0, 100]):
        ttk.LabelFrame.__init__(self, parent)
        self.configure(text = 'Plot Options')
        self.clock = clock
        self.metrics = metrics
        self.node_range = node_range
        self.parent = parent
        self.initialize()

    def disable(self):
        for child in self.winfo_children():
            try:
                child.disable()
            except:
                child.configure(state = tk.DISABLED)

    def enable(self):
        for child in self.winfo_children():
            try:
                child.enable()
            except:
                child.configure(state = tk.NORMAL)

    def start_button_press(self):
        pass
        # self.disable()
        # # time.sleep(5)
        # self.parent.realtabcons.enable()
        # self.parent.realtabshare.control_share.disable()

        # print 'SthAAAAAaaap!!'

    def download_button_press(self):
        pass

    def initialize(self):
        self.grid()
        self.date_time_start = DTControl(self, self.clock)
        self.date_time_end = DTControl(self, self.clock, entry_label = 'End Time:')
        self.metric_box = Metric_Check(self, val_list = self.metrics)
        self.node_slide = Double_Slider(self, self.node_range[0], self.node_range[1])
        self.mps = Maxpoint_Scale(self, low_limit = 10, high_limit = 120)
        xpadding = 10
        ypadding = 10
        self.date_time_start.grid(column = 0, row = 0, padx = xpadding, pady = ypadding)
        self.date_time_end.grid(column = 1, row = 0, padx = xpadding, pady = ypadding)
        self.metric_box.grid(column = 0, row = 1, padx = xpadding, pady = ypadding)
        self.node_slide.grid(column = 0, row = 2, padx = xpadding, pady = ypadding)
        self.mps.grid(column = 0, row = 3, padx = xpadding, pady = ypadding)
        self.start_plot_button = ttk.Button(self, width = 20, text = 'Display Plot', command = self.start_button_press)
        self.start_plot_button.grid(column = 0, row = 4, pady = ypadding)
        self.download_button = ttk.Button(self, width = 20, text = 'Download Plot', command = self.download_button_press)
        self.download_button.grid(column = 1, row = 4, pady = ypadding)

class Static_Tab(tk.Frame):
    def __init__(self, parent, client):
        tk.Frame.__init__(self, parent)
        self.client = client
        self.initialize()

    def initialize(self):
        self.grid()

        statictabops = Static_Tab_options(self, metrics = l)
        statictabops.grid(column = 0, row = 0)

class Stats(ttk.LabelFrame):
    def __init__(self, parent, quantities):
        ttk.LabelFrame.__init__(self, parent)
        self.quant_list = quantities
        self.configure(text = 'Statistics')
        self.initialize()

    def set_quantity(self, quantity, val):
        prev = self.quantities.get(quantity, None)
        if prev != None:
            prev.set('%.30s : %3d' %(quantity, val))

    def initialize(self):
        self.grid()
        self.quantities = {k : tk.StringVar() for k in self.quant_list}
        [self.quantities[k].set('%.30s : ' % (k)) for k in self.quantities.keys()]
        label_list = [ttk.Label(self, textvariable = self.quantities[k], anchor = tk.W, width = 40) for k in self.quant_list]
        [label.grid(column = 0, row = i) for (i, label) in enumerate(label_list)]


class Statistic_Tab(tk.Frame):
    def __init__(self, parent):
        tk.Frame.__init__(self, parent)
        self.initialize()

    def initialize(self):
        self.grid()
        self.stats = Stats(self, ['Laptop/Desktop Nodes', 'Smartphone/Tablet Nodes', 'Embedded/Other Nodes'])
        self.stats.grid(column = 0, row = 0)
        # self.stats.set_quantity('Laptop/Desktop Nodes', 2)

if __name__ == "__main__":
    server_address = (SERVER_IP, SERVER_PORT)
    app = GUI(None, client = UC.Client(server_address))
    # app = GUI(None, '<client>')
    app.title('Plot Controller')
    app.mainloop()