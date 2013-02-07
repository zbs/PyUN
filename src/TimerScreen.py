'''
Created on Sep 14, 2012

@author: zach
'''
from Tkinter import *
#from Tix import *
from ttk import *
from tkFont import Font
from SetupScreen import *
from tkFileDialog import askopenfilename
import threading
import os
import re
import time
import collections
import datetime

PAUSE = "Pause"
RESUME = "Resume"
RESET = "Reset"
START = "Start"
NEXT_SPEAKER = "Next speaker"
BACK = "Back"
ADD_SPEAKER = "Add speaker"
CHOOSE_SPEAKER = "Choose speaker"
RECENT_ACTIVITY = "Recent Activity"
TITLE = "Title"
CHOOSE_DOCUMENT = "Choose document"
LINK = "Link"
ADD_ENTRY = "Add entry"
NO_SPEAKER_TIME = 'Nobody'
WRAPLENGTH = 400

timetracker = collections.defaultdict(lambda:0)

def timetracker_filename():
    localtime = time.localtime()
    return 'ModelUN_%s_%s%s.csv'%(str(datetime.date.today()), 
                                  ('0' + str(localtime.tm_hour))[-2:], ('0' + str(localtime.tm_min))[-2:])

class TimerScreen():
    def __init__(self, master, back_callback=None, **kwargs):
        sw = master.winfo_screenwidth()
        sh = master.winfo_screenheight()
        
        self.master = master
        self.back_callback = back_callback
        self.exit_flag = False
        self.kwargs = kwargs
        
        self.timer_thread = None
        self.timer_lock = threading.Lock()
        self.timer_condition = threading.Condition(self.timer_lock)
        self.exit_flag_lock = threading.Lock()
        
        button_panel = Frame(master,  background='#66a3d2',width=sw)
        button_panel.grid(row=0, columnspan=4, pady=sh/8)
        
        left_column = Frame(master,  background='#66a3d2')
        self.left_column = left_column
        left_column.grid(column=0, row=1, padx=(sw/13,0))
        
        middle_column = Frame(master, background='#66a3d2', width=float(sw)/3.)
        middle_column.grid(column=1, row=1, padx=sw/10)
        
        right_column = Frame(master,  background='#66a3d2', width=sw/3.)
        right_column.grid(column=2, row=1, padx=(0,sw/8))
        
        button_font = Font(family="Helvetica", size=13)
        self.toggle_button_text = StringVar(value=PAUSE)
        self.start_button_text = StringVar(value=START)

        self.start_button = Button(button_panel, font=button_font, command=self.start_debate, textvariable=self.start_button_text)
        self.start_button.grid(column=0, row=0, padx=(0,50))
        
        self.toggle_button = Button(button_panel, font=button_font, command=self.toggle_debate, state=DISABLED, textvariable=self.toggle_button_text)
        self.toggle_button.grid(column=1, row=0, padx=(0,50))
        
        self.next_speaker_button = Button(button_panel, font=button_font, command=self.next_speaker, state=DISABLED, text=NEXT_SPEAKER)
        self.next_speaker_button.grid(column=2, row=0, padx=(0,50))
        
        Button(button_panel, font=button_font, command=self.go_back, text=BACK).grid(column=3, row=0, padx=(0,50))
        
        self.total_time = int(kwargs[TOTAL_TIME].get_total_time())
        self.speaker_time = int(kwargs[SPEAKER_TIME].get_total_time())
        
        self.total_time_remaining = self.total_time
        self.speaker_time_remaining = self.speaker_time
        
        self.speaker_list = kwargs[SPEAKER_LIST]
        self.master_list = kwargs[MASTER_LIST]
        
#        initalize left column
        listbox_font = Font(family='Helvetica', size=12)
        self.speaker_listbox = Listbox(left_column, font=listbox_font, width=30, height=10)
        for name in self.speaker_list:
            self.speaker_listbox.insert(END, name)
        self.speaker_listbox.grid(row=0, column=0, columnspan=2, pady=30)
        
        self.speaker_to_add = StringVar(value='')
        if self.master_list:
            self.speaker_to_add.set(self.master_list[0])
            
        speaker_to_add_box = Combobox(left_column, 
                                      width=20,
                                      font=listbox_font,
                                      textvariable=self.speaker_to_add,
                                      values=self.master_list,
                                      state="readonly")
        speaker_to_add_box.grid(row=1, column=0, padx=10)
        self.speaker_to_add_box = speaker_to_add_box
        
        add_speaker_button = Button(left_column, font=listbox_font, text=ADD_SPEAKER)
        add_speaker_button.grid(row=1, column=1)
        self.add_speaker_button = add_speaker_button
        
        def add_speaker():
            self.speaker_listbox.insert(END, self.speaker_to_add.get())
        add_speaker_button.config(command=add_speaker)
        
        if not self.master_list:
            speaker_to_add_box.config(state='disabled')
            add_speaker_button.config(state='disabled')
        
        
#        initialize middle column
        self.speaker = StringVar()
#        self.speaker.set("%s"%self.pop_speaker())
        header_font = Font(family="Helvetica", size=40)
        Label(middle_column,  background='#66a3d2', wraplength=WRAPLENGTH,
              text="%s: %s"%(kwargs[TYPE_OF_CAUCUS], kwargs[TITLE_OF_CAUCUS]), font=header_font).pack()
        Label(middle_column,  background='#66a3d2',textvariable=self.speaker, font=header_font).pack()
        
        self.total_time_string = StringVar()
        self.speaker_time_string = StringVar()
        
        total_time_string = "%s:%s"%(('0' + kwargs[TOTAL_TIME].minutes.get())[-2:], ('0'+kwargs[TOTAL_TIME].seconds.get())[-2:])
        speaker_time_string = "%s:%s"%(('0' + kwargs[SPEAKER_TIME].minutes.get())[-2:], ('0' + kwargs[SPEAKER_TIME].seconds.get())[-2:])
      
        self.total_time_string.set(total_time_string)
        self.speaker_time_string.set(speaker_time_string)
        remaining_font = Font(family="Helvetica", size=30)
        total_font = Font(family="Helvetica", size=20)

        Label(middle_column, background='#66a3d2', textvariable=self.total_time_string, font=remaining_font).pack()
        Label(middle_column,  background='#66a3d2',text=total_time_string, font=total_font).pack()
        Label(middle_column,  background='#66a3d2',text=speaker_time_string, font=total_font).pack()
        Label(middle_column,  background='#66a3d2',textvariable=self.speaker_time_string, font=remaining_font).pack()
    
#    initialize right column
        entry_font = Font(family='Helvetica', size=18)
        
        Label(right_column,  background='#66a3d2',font=entry_font, text=RECENT_ACTIVITY).pack()
        text_fields = Frame(right_column, background='#66a3d2',)
        text_fields.pack()
        recent_entries = Frame(right_column, background='#66a3d2')
        recent_entries.pack()
        
        doc_title = StringVar()
        doc_link = StringVar()
        
        Label(text_fields, text=TITLE, background='#66a3d2', font=entry_font).grid(column=0, row=0)
        Label(text_fields, text=LINK,  background='#66a3d2',font=entry_font).grid(column=0, row=1)
        Entry(text_fields, textvariable=doc_title,font=entry_font).grid(column=1, row=0, pady=(0,10))
        
        choose_document_button =  Button(text_fields, font=entry_font, text=CHOOSE_DOCUMENT)
        choose_document_button.grid(column=1, row=1)

        def get_entry_filename():
            filename = askopenfilename()
            if filename:
                truncated_name = re.match(r'(.*/)*(.+\.\w+)', filename[-15:]).group(2)
                if not truncated_name:
                    raise Exception('Please provide a valid filename.')
                choose_document_button.config(text='...%s'%truncated_name, state=DISABLED)
            doc_link.set(filename)
            
        choose_document_button.config(command=get_entry_filename)
        
        article_font = Font(family='Helvetica', size=15)
        def add_entry():
            if doc_title.get():
                choose_document_button.config(text=CHOOSE_DOCUMENT, state=NORMAL)
                entry_panel = Frame(recent_entries, background='#66a3d2')
                entry_panel.pack()
                Label(entry_panel,  background='#66a3d2',font=article_font, text=doc_title.get()).pack()
           
                if doc_link.get():
                    filename = doc_link.get()
                    def open_file():
                        if os.name == 'nt':
                            os.system('start '+ '"" "%s"'%filename)
                        elif os.name == 'posix':
                            os.system('open ' + '"%s"'%filename)
                    Button(entry_panel, font=article_font, text="Open", command=open_file).pack()
                    Button(entry_panel, font=article_font, text="Delete", command=lambda: entry_panel.destroy()).pack()
                    doc_title.set(value='')
                    doc_link.set(value='')
            
        Button(text_fields, font=entry_font, text=ADD_ENTRY, command=add_entry).grid(columnspan=2, row=2, pady=(5,20))
        
    
    def write_out_timetracker(self):
        timetracker_csv = "Speaker,Total Time Spoken\n"
        for (speaker, time_spoken) in timetracker.iteritems():
            minutes = time_spoken/60
            seconds = ('0' + str(time_spoken % 60))[-2:]
            time_spoken_string = '%s:%s'%(minutes, seconds)
            timetracker_csv += "%s,%s\n"%(speaker, time_spoken_string)
        with open(timetracker_filename(), 'w') as fp:
            fp.write(timetracker_csv)
        
    def disable_left_column(self):
        self.add_speaker_button.config(state=DISABLED)
        self.speaker_to_add_box.config(state=DISABLED)

    def pop_speaker(self):
        if self.speaker_listbox.size():
            speaker = self.speaker_listbox.get(0)
            self.speaker_listbox.delete(0)
            return speaker
        return ''
    
    def reset_debate(self):
        self.pause_debate()
        
        for child in self.master.children.values():
            child.destroy()
        self = TimerScreen(self.master, self.back_callback, **self.kwargs)
    
    def start_debate(self):
        self.start_button_text.set(RESET)
        self.speaker.set(self.pop_speaker())
#        self.disable_left_column()
        self.start_button.config(command=self.reset_debate)
        
        self.next_speaker_button.config(state=NORMAL)
        self.toggle_button.config(state=NORMAL)
        
        self.resume_debate()
        
    def next_speaker(self):
        self.pause_debate()
        self.speaker.set(self.pop_speaker())
#        self.total_time_remaining -= self.speaker_time_remaining
        self.total_time_remaining -= self.speaker_time_remaining
        total_time_minutes = int(self.total_time_remaining / 60)
        total_time_seconds = self.total_time_remaining % 60
        
        self.total_time_string.set("%s:%s"%(('0' + str(total_time_minutes))[-2:], ('0'+str(total_time_seconds))[-2:]))
        
        self.speaker_time_remaining = self.speaker_time
        self.resume_debate()
    
    def on_tick(self):
        self.total_time_remaining -= 1
        self.speaker_time_remaining -= 1
        
        total_time_minutes = int(self.total_time_remaining / 60)
        total_time_seconds = self.total_time_remaining % 60
        
        self.total_time_string.set("%s:%s"%(('0' + str(total_time_minutes))[-2:], ('0'+str(total_time_seconds))[-2:]))
        
        speaker_time_minutes = int(self.speaker_time_remaining/ 60)
        speaker_time_seconds = self.speaker_time_remaining% 60
        
        self.speaker_time_string.set("%s:%s"%(('0' + str(speaker_time_minutes))[-2:], ('0'+str(speaker_time_seconds))[-2:]))
        
        speaker_name = self.speaker.get() if self.speaker.get() else NO_SPEAKER_TIME
        total_spoken_time = timetracker[speaker_name]
        timetracker[speaker_name] = total_spoken_time + 1
            
    def callback(self):
        if self.total_time_remaining <= 0:
            self.final_UI()
        else:
            self.toggle_button.config(state=DISABLED)
                
    def resume_debate(self):
        self.start_countdown_thread(self.speaker_time_remaining, self.on_tick, self.callback)
        self.toggle_button.config(state=NORMAL)
        self.toggle_button_text.set(PAUSE)
    
    def pause_debate(self):
        if self.is_running():
            self.cancel_countdown_thread()
            self.toggle_button_text.set(RESUME)
    
    def toggle_debate(self):
        if self.is_running():
            self.pause_debate()
        else:
            self.resume_debate()
    
    def is_running(self):
        with self.timer_lock:
            return self.timer_thread and self.timer_thread.is_alive()
        
    def final_UI(self):
        pass
    
    def go_back(self):
        self.pause_debate()
        for child in self.master.children.values():
            child.destroy()
        SetupScreen(self.master, TimerScreen, **self.kwargs)    
        self.master.protocol("WM_DELETE_WINDOW", lambda: self.master.destroy())
        
    def start_countdown_thread(self, time_remaining, on_tick, callback):
        with self.timer_lock:
            while self.timer_thread and self.timer_thread.is_alive():
                self.timer_lock.release()
                self.cancel_countdown_thread()
                self.timer_lock.acquire()
            self.timer_thread = threading.Thread(target=self.countdown, 
                                                 args=(self.speaker_time_remaining, self.on_tick, self.callback))
            self.timer_thread.start()
    
    def cancel_countdown_thread(self):
        with self.timer_lock:
            if self.timer_thread.is_alive():
                with self.exit_flag_lock:
                    self.exit_flag = True
                self.timer_thread.join()
            
    
    def countdown(self, time_, on_tick, callback):
        while time_ > 0:
#            cleaner way to do this?
            with self.exit_flag_lock:
                if self.exit_flag:
                    self.exit_flag = False
                    return
            time.sleep(1)
            with self.exit_flag_lock:
                if self.exit_flag:
                    self.exit_flag = False
                    return
            time_ -= 1
            
            on_tick()
        callback()