from Tkinter import *
#from Tix import *
from tkFileDialog import askopenfilename
from tkFont import Font
import Tix

#from TimerScreen import TimerScreen
TYPE_OF_CAUCUS = "Type of caucus"
TITLE_OF_CAUCUS = "Title of caucus"
TOTAL_TIME = "Total time"
SPEAKER_TIME = "Speaker time"
MASTER_LIST = "Master list"
SPEAKER_LIST = "Speaker list"
DEBATE_BUTTON = "Debate"
MINUTES = "Minutes"
SECONDS = "Seconds"
EXCLUDED_SPEAKER_LIST = "Unchosen speakers"
class SetupScreen():
    
    
    class TimeCount():
        def __init__(self, minutes=None, seconds=None):
            self.minutes = StringVar(value='0')
            self.seconds = StringVar(value='0')
            
            if minutes:
                self.minutes.set(minutes)
            if seconds:
                self.seconds.set(seconds)
            
        def get_total_time(self):
            return str(int(self.minutes.get())*60 + int(self.seconds.get()))
    def __init__(self, master, TimerScreenClass, **kwargs):
        self.frame = Frame(master, background='#66a3d2')
        swin = self.frame
#        swin = Tix.ScrolledWindow(master, scrollbar=Tix.Y)
        swin.pack()

        self.type_of_caucus = StringVar()
        self.title_of_caucus = StringVar()
        self.total_time = SetupScreen.TimeCount()
        self.speaker_time = SetupScreen.TimeCount()
        self.master_list = StringVar()
        self.speaker_list = StringVar()
        
        top_label = Label(swin, background='#66a3d2', text=TYPE_OF_CAUCUS)
        top_label.grid(row=0,column=0, sticky='W')
        Entry(swin, textvariable=self.type_of_caucus).grid(row=0, column=1, columnspan=2)
        
        Label(swin, background='#66a3d2', text=TITLE_OF_CAUCUS).grid(row=1, column=0, sticky='W')
        Entry(swin, textvariable=self.title_of_caucus).grid(row=1,column=1, columnspan=2)
        
        Label(swin, background='#66a3d2', text=MINUTES).grid(row=2, column=1)
        Label(swin, background='#66a3d2', text=SECONDS).grid(row=2, column=2)
        
        Label(swin, background='#66a3d2', text=TOTAL_TIME).grid(row=3, column=0, sticky='W')
        Entry(swin, textvariable=self.total_time.minutes).grid(row=3, column=1, padx=(0,10))
        Entry(swin, textvariable=self.total_time.seconds).grid(row=3, column=2)
       
        Label(swin, background='#66a3d2', text=SPEAKER_TIME).grid(row=4, column=0, sticky='W')
        Entry(swin, textvariable=self.speaker_time.minutes).grid(row=4, column=1,padx=(0,10))
        Entry(swin, textvariable=self.speaker_time.seconds).grid(row=4, column=2)
                
        Label(swin, background='#66a3d2', text=MASTER_LIST).grid(row=5, column=0, sticky='W')
        Label(swin, background='#66a3d2', text=SPEAKER_LIST).grid(row=6, columnspan=3)
        
        left_listbox = Listbox(swin, selectmode=MULTIPLE)
        left_listbox.grid(row=7, column=0, rowspan=2)
        
        self.left_listbox = left_listbox
        
        self.right_listbox = Listbox(swin, selectmode=MULTIPLE)
        self.right_listbox.grid(row=7, column=2, rowspan=2)
  
        def select_file():
            filename = askopenfilename()
            if filename:
                with open(filename) as fp:
                    self.master_list = fp.read().strip().split('\n')
                    left_listbox.delete(0, END)
                    for name in self.master_list:
                        left_listbox.insert(END, name)
        def transfer_listbox_items(source, destination):
            while source.curselection():
                destination.insert(END, source.get(source.curselection()[0]))
                source.delete(source.curselection()[0])
        def right_button_click():
            transfer_listbox_items(left_listbox, self.right_listbox)
        def left_button_click():
            transfer_listbox_items(self.right_listbox, left_listbox)
            
        Button(swin, text="Select master list file", command=select_file).grid(row=5, column=1)
        
        Button(swin, text="Left", command=left_button_click).grid(row=7, column=1)
        Button(swin, text="Right", command=right_button_click).grid(row=8, column=1)
        
        def debate_callback():
            data = self.get_data()
            self.destroy()
            t = TimerScreenClass(master, **data)
            def close_window():
                t.write_out_timetracker()
                master.destroy()
                
            master.protocol("WM_DELETE_WINDOW", close_window)
            
        self.debate_button = Button(swin, text=DEBATE_BUTTON, command=debate_callback)
        self.debate_button.grid(row=9, columnspan=3)
        
        def prepopulate_fields():
            if not kwargs:
                return
            self.title_of_caucus.set(kwargs[TITLE_OF_CAUCUS])
            self.type_of_caucus.set(kwargs[TYPE_OF_CAUCUS])
            
            #time -- TODO
            self.total_time.minutes.set(kwargs[TOTAL_TIME].minutes.get())
            self.total_time.seconds.set(kwargs[TOTAL_TIME].seconds.get())
            
            self.speaker_time.minutes.set(kwargs[SPEAKER_TIME].minutes.get())
            self.speaker_time.seconds.set(kwargs[SPEAKER_TIME].seconds.get())
            
            speaker_set = set(kwargs[SPEAKER_LIST])
            master_set = set(kwargs[MASTER_LIST])
            
            for speaker in speaker_set:
                self.right_listbox.insert(END, speaker)
            for speaker in master_set - speaker_set:
                self.left_listbox.insert(END, speaker)
            
            
            
        prepopulate_fields()
        
        text_font = Font(family='Helvetica', size=16)
        for child in swin.children.values():
            child.config(font=text_font)
            child.grid(pady=10)

    def destroy(self):
        self.frame.destroy()
             
    def get_data(self):
        def make_list(sequence):
            return [sequence] if type(sequence) != type(()) else list(sequence)
            
        speaker_tuple = self.right_listbox.get(first=0, last=self.right_listbox.size()-1)
        
        return {
                TYPE_OF_CAUCUS: self.type_of_caucus.get(), 
                TITLE_OF_CAUCUS: self.title_of_caucus.get(),
                TOTAL_TIME: self.total_time,
                SPEAKER_TIME: self.speaker_time,
                SPEAKER_LIST: make_list(self.right_listbox.get(first=0, last=self.right_listbox.size()-1)),
                MASTER_LIST: make_list(self.right_listbox.get(first=0, last=self.right_listbox.size()-1)) + 
                                       make_list(self.left_listbox.get(first=0, last=self.left_listbox.size()-1))
                }