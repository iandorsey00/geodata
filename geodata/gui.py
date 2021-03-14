import engine

import tkinter as tk
import tkinter.messagebox as tk_messagebox

from tkinter import ttk

import time

class GeodataGUI:
    def __init__(self):
        self.dp_offset = 0

        self.root = tk.Tk()
        self.root.title('geodata v0.2a')
        self.root.minsize(500, 20)

        # Main window #########################################################

        ### Upper area
        self.upper_frame = tk.Frame(master=self.root)

        ## Search area

        # Search Entry
        self.search_entry_placeholder = False

        self.search_entry = tk.Entry(master=self.upper_frame, font='Arial 9 italic')
        self.search_entry.insert(0, 'Search for a geography')
        self.search_entry_placeholder = True
        self.search_entry.pack(side=tk.LEFT, fill=tk.BOTH, expand=tk.YES)
        self.search_entry.bind('<Key>', self.search_key)
        self.search_entry.bind('<KeyRelease>', self.search_keyrelease)
        self.search_entry.bind('<FocusIn>', self.search_focusin)
        self.search_entry.icursor(0)

        self.search_button = tk.Button(master=self.upper_frame, text='Search', padx=10, command=self.search)
        self.search_button.pack(side=tk.LEFT)

        self.go_button = tk.Button(master=self.upper_frame, text='Go', bg='green', fg='white', padx=10, command=self.go)
        self.go_button.pack(side=tk.LEFT)
        self.root.bind('<Return>', self.go)

        # Pack upper_frame
        self.upper_frame.pack(fill=tk.BOTH, expand=tk.YES, pady=10)
        self.search_entry.focus_set()

        ### Middle area
        self.middle_frame = tk.Frame(master=self.root)

        self.middle_frame_separator = ttk.Separator(master=self.middle_frame, orient=tk.HORIZONTAL)
        self.middle_frame_separator.pack(fill=tk.X, expand=tk.YES)

        self.values_frame = tk.Frame(master=self.middle_frame, pady=10)

        self.values_display_label = tk.Label(master=self.values_frame, text='Display', anchor='w')
        self.values_display_label.pack(side=tk.LEFT, padx=(0, 5))

        self.values_combobox = ttk.Combobox(master=self.values_frame, state='readonly')
        self.values_combobox['values'] = ['highest values',
                                          'lowest values']
        self.values_combobox.set('highest values')
        self.values_combobox.pack(side=tk.LEFT)

        self.values_for_label = tk.Label(master=self.values_frame, text='for', padx=5)
        self.values_for_label.pack(side=tk.LEFT)

        self.values_comp_combobox = ttk.Combobox(master=self.values_frame, state='readonly')
        self.values_comp_combobox['values'] = ['land_area',
                                               'population',
                                               'population_density',
                                               'white_alone',
                                               'white_alone_not_hispanic_or_latino',
                                               'black_alone',
                                               'asian_alone',
                                               'other_race',
                                               'hispanic_or_latino',
                                               'population_25_years_and_older',
                                               'bachelors_degree_or_higher',
                                               'graduate_degree_or_higher',
                                               'per_capita_income',
                                               'median_household_income',
                                               'median_year_structure_built',
                                               'median_rooms',
                                               'median_value',
                                               'median_rent']
        self.values_comp_combobox.set('population')
        self.values_comp_combobox.pack(side=tk.LEFT)

        self.values_go_button = tk.Button(master=self.values_frame, text='Go', bg='green', fg='white', padx=10, command=self.values_go)
        self.values_go_button.pack(side=tk.RIGHT)

        self.values_frame.pack(fill=tk.X, expand=tk.YES)

        self.middle_frame.pack(fill=tk.X, expand=tk.YES)
        
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
            self.search_entry.insert(0, 'Search for a geography')
            self.search_entry_placeholder = True
            self.search_entry.icursor(0)

    def search_focusin(self, event=None):
        '''Triggered by placing focus on the widget'''
        if self.search_entry_placeholder == True:
            self.search_entry.icursor(0)

    def search(self):
        pass

    def go(self, event=None):
        self.display_demographic_profile(self.search_entry.get())

    def display_demographic_profile(self, display_label):
        dp_window = tk.Toplevel(master=self.root)
        dp_window.minsize(500, 150)
        dp_window.columnconfigure(0, weight=1)

        now_loading = tk.Label(master=dp_window, text='Now loading. Please wait.')
        now_loading.grid(row=0, column=0, sticky='nsew')
        self.root.update()

        d = engine.initialize_database()
        dp_list = list(filter(lambda x: x.name == display_label, d['demographicprofiles']))

        if len(dp_list) == 0:
            dp_window.destroy()
            tk_messagebox.showinfo('', 'Sorry, there is no geography with that name.')
        else:
            dp = dp_list[0]

            place = tk.Label(master=dp_window, text=dp.name, padx=10, font=('TkCaptionFont', 20), anchor='w')
            place.grid(row=0, column=0, columnspan=3, sticky='nsew')

            counties_text = ', '.join(dp.counties_display)
            counties = tk.Label(master=dp_window, text=counties_text, padx=10, anchor='w')
            counties.grid(row=1, column=0, columnspan=3, sticky='nsew')

            self.dp_offset = 2

            keys = ['land_area',
                    'population',
                    'population_density',
                    'white_alone',
                    'white_alone_not_hispanic_or_latino',
                    'black_alone',
                    'asian_alone',
                    'other_race',
                    'hispanic_or_latino',
                    'population_25_years_and_older',
                    'bachelors_degree_or_higher',
                    'graduate_degree_or_higher',
                    'per_capita_income',
                    'median_household_income',
                    'median_year_structure_built',
                    'median_rooms',
                    'median_value',
                    'median_rent']

            for row, key in enumerate(keys):
                # Headers
                if key == 'land_area':
                    self.demographic_profile_header(dp_window, 'Geography', row + self.dp_offset)
                elif key == 'population':
                    self.demographic_profile_header(dp_window, 'Population', row + self.dp_offset)
                elif key == 'white_alone':
                    self.demographic_profile_subheader(dp_window, 'Race', row + self.dp_offset)
                elif key == 'hispanic_or_latino':
                    self.demographic_profile_subheader(dp_window, 'Hispanic or Latino (of any race)', row + self.dp_offset)
                elif key == 'population_25_years_and_older':
                    self.demographic_profile_header(dp_window, 'Education', row + self.dp_offset)
                elif key == 'per_capita_income':
                    self.demographic_profile_header(dp_window, 'Income', row + self.dp_offset)
                elif key == 'median_year_structure_built':
                    self.demographic_profile_header(dp_window, 'Housing', row + self.dp_offset)

                if key == 'population_density':
                    row_header = tk.Label(master=dp_window, text=dp.rh[key], padx=10, anchor='w')
                    row_header.grid(row=row + self.dp_offset, column=0, sticky='nsew')
                    component = tk.Label(master=dp_window, padx=10, anchor='e')
                    component.grid(row=row + self.dp_offset, column=1, sticky='nsew')
                    compound = tk.Label(master=dp_window, text=dp.fcd[key], padx=10, anchor='e')
                    compound.grid(row=row + self.dp_offset, column=2, sticky='nsew')
                elif key in ['land_area', 'population', 'per_capita_income', 'median_household_income',
                             'median_year_structure_built', 'median_rooms', 'median_value', 'median_rent']:
                    self.demographic_profile_row_nc(dp_window, dp, key, row + self.dp_offset)
                else:
                    self.demographic_profile_row_std(dp_window, dp, key, row + self.dp_offset)

    def demographic_profile_row_std(self, master, dp, key, row):
        row_header = tk.Label(master=master, text=dp.rh[key], padx=10, anchor='w')
        row_header.grid(row=row, column=0, sticky='nsew')
        component = tk.Label(master=master, text=dp.fc[key], padx=10, anchor='e')
        component.grid(row=row, column=1, sticky='nsew')
        compound = tk.Label(master=master, text=dp.fcd[key], padx=10, anchor='e')
        compound.grid(row=row, column=2, sticky='nsew')

    def demographic_profile_row_nc(self, master, dp, key, row):
        row_header = tk.Label(master=master, text=dp.rh[key], padx=10, anchor='w')
        row_header.grid(row=row, column=0, sticky='nsew')
        component = tk.Label(master=master, padx=10, anchor='e')
        component.grid(row=row, column=1, sticky='nsew')
        compound = tk.Label(master=master, text=dp.fc[key], padx=10, anchor='e')
        compound.grid(row=row, column=2, sticky='nsew')

    def demographic_profile_header(self, master, text, row):
        header = tk.Label(master=master, text=text, padx=10, font=('TkCaptionFont', 15), anchor='w')
        header.grid(row=row, column=0, columnspan=3, sticky='nsew')
        self.dp_offset += 1

    def demographic_profile_subheader(self, master, text, row):
        header = tk.Label(master=master, text=text, padx=10, font=('TkCaptionFont', 12), anchor='w')
        header.grid(row=row, column=0, columnspan=3, sticky='nsew')
        self.dp_offset += 1

    def values_go(self, event=None):
        val_window = tk.Toplevel(master=self.root)
        val_window.minsize(500, 150)
        val_window.columnconfigure(0, weight=1)

        now_loading = tk.Label(master=val_window, text='Now loading. Please wait.')
        now_loading.grid(row=0, column=0, sticky='nsew')
        self.root.update()

        evs = main.get_extreme_values

        if len(dp_list) == 0:
            dp_window.destroy()
            tk_messagebox.showinfo('', 'Sorry, there is no geography with that name.')
        else:


    def activate_mainloop(self):
        self.root.mainloop()

ggui = GeodataGUI()
ggui.activate_mainloop()
