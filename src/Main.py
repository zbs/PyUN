from Tkinter import *
from SetupScreen import *
from TimerScreen import TimerScreen
import collections
"""
    TODO:
        - Delete button next to open button in TimerScreen
        - Make sure new time record functionality works
        - Make docs scrollable
        
        
"""
root = Tk()
root.configure(background='#66a3d2')
root.state('zoomed')

kwargs =  {
                TYPE_OF_CAUCUS: 'TYPE', 
                TITLE_OF_CAUCUS: "SUPERRRRRLONGGGTITLE",
                TOTAL_TIME: SetupScreen.TimeCount(minutes='10'),
                SPEAKER_TIME: SetupScreen.TimeCount(seconds='5'),
                SPEAKER_LIST: ['a', 'b', 'c', 'd'],
                MASTER_LIST: ['a', 'b', 'c', 'd', 'e', 'f', 'g']
            }       

setup_screen = SetupScreen(root, TimerScreen)

#timer_screen = TimerScreen(root, **kwargs)
#def close_window():
#    timer_screen.write_out_timetracker()
#    root.destroy()
#                
#root.protocol("WM_DELETE_WINDOW", close_window)
            
root.mainloop()

if __name__ == '__main__':
    pass