import __main__ as main

import tkinter as tk

class GeodataGUI:
    def __init__(self):
        self.root = tk.Tk()
        self.root.title('geodata v0.2a')

        # Main window #########################################################

        ### Upper area
        self.upper_frame = tk.Frame(master=self.root)

        ## Search area

        # Search Entry
        self.search_entry_placeholder = False

        self.search_entry = tk.Entry(master=self.upper_frame, font='Arial 9 italic')
        self.search_entry.insert(0, 'Search for a geography')
        self.search_entry_placeholder = True
        self.search_entry.pack(side=tk.LEFT)
        self.search_entry.bind('<Key>', self.search_key)
        self.search_entry.bind('<KeyRelease>', self.search_keyrelease)
        self.search_entry.bind('<FocusIn>', self.search_focusin)
        self.search_entry.icursor(0)

        self.go_button = tk.Button(master=self.upper_frame, text='Go', bg='green', fg='white', padx=10, command=self.go)
        self.go_button.pack(side=tk.LEFT)
        self.upper_frame.bind('<Return>', self.go)

        # Pack upper_frame
        self.upper_frame.pack(fill=tk.X, expand=tk.YES)
        
    def search_key(self, event=None):
        '''Triggered by <Key>, before sending the event to the widget'''
        # If the key pressed isn't a special key, remove placeholder and
        # unitalicize widget text
        if self.search_entry_placeholder == True and event.char != "":
            self.search_entry.delete(0, tk.END)
            self.search_entry.configure(font='Arial 9')
            self.search_entry_placeholder = False

    def search_keyrelease(self, event=None):
        '''Triggered by <KeyRelease>, before sending the event to the widget'''
        # If widget is empty, italicize font, then insert placeholder
        if self.search_entry_placeholder == False and len(self.search_entry.get()) == 0:
            self.search_entry.configure(font='Arial 9 italic')
            self.search_entry.insert(0, 'Enter search')
            self.search_entry_placeholder = True
            self.search_entry.icursor(0)

    def search_focusin(self, event=None):
        '''Triggered by placing focus on the widget'''
        if self.search_entry_placeholder == True:
            self.search_entry.icursor(0)

    def go(self):
        pass
    
    def activate_mainloop(self):
        self.root.mainloop()

ggui = GeodataGUI()
ggui.activate_mainloop()
