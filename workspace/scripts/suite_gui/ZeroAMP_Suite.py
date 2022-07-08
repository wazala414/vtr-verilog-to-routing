#!/usr/bin/python3
# import all components
# from the tkinter library
from distutils.log import error
from tkinter import *
import os
import subprocess as sp
import tkinter
from turtle import width
from PIL import ImageTk, Image
import webbrowser

import lib.netlist_parse
import lib.switch_position

# import filedialog module
from tkinter import filedialog

from tkinter import ttk
  
#--------------------------
#
#       Browser Functions
#
#--------------------------

def browseArchitecture(filename,field):
    filename = filedialog.askopenfilename(initialdir = "~/VTR-Tools/workspace/architectures",
                                          title = "Select a File",
                                          filetypes = (("XML files",
                                                        "*.xml*"),
                                                       ("all files",
                                                        "*.*")))
    if filename:
        _,file_extension = os.path.splitext(filename)
        if file_extension != ".xml":
            set_text(field,"Error: Requires XML file type") 
        else:
            set_text(field,filename)

def browseCircuit(filename,field):
    filename = filedialog.askopenfilename(initialdir = "~/VTR-Tools/workspace/circuits",
                                          title = "Select a File",
                                          filetypes = (("Verilog files",
                                                        "*.v*"),
                                                       ("all files",
                                                        "*.*")))
    if filename:
        _,file_extension = os.path.splitext(filename)
        if file_extension != ".v":
            set_text(field,"Error: Requires Verilog file type") 
        else:
            set_text(field,filename)

def browseOutDir(filename,field):
    filename = filedialog.askdirectory(initialdir = "~/VTR-Tools/workspace",
                                          title = "Select a Folder")
    set_text(field,filename)


def browseRoute(filename,field):
    filename = filedialog.askopenfilename(initialdir = "~/VTR-Tools/workspace/",
                                          title = "Select a File",
                                          filetypes = (("Route files",
                                                        "*.route*"),
                                                       ("all files",
                                                        "*.*")))
    if filename:
        _,file_extension = os.path.splitext(filename)
        if file_extension != ".route":
            set_text(field,"Error: Requires Route file type") 
        else:
            set_text(field,filename)

def browseCSV(filename,field):
    filename = filedialog.askopenfilename(initialdir = "~/VTR-Tools/workspace/",
                                          title = "Select a File",
                                          filetypes = (("CSV files",
                                                        "*.csv*"),
                                                       ("all files",
                                                        "*.*")))
    if filename:
        _,file_extension = os.path.splitext(filename)
        if file_extension != ".csv":
            set_text(field,"Error: Requires Route file type") 
        else:
            set_text(field,filename)

def browseTask(filename,field):
    filename = filedialog.askopenfilename(initialdir = "~/VTR-Tools/workspace/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
    if filename:
        _,file_extension = os.path.splitext(filename)
        if file_extension != ".txt":
            set_text(field,"Error: Requires Route file type") 
        else:
            set_text(field,filename)

def file_exist(filename, file_override):
    # Create the root window
    error_window = Tk()
    error_window.title('Error: File Already Exists')
    error_window.geometry("300x150")
    error_window.config()
    ttk.Label(error_window, text=("Warning: " + filename + " already exists.")).pack()
    prompt_frame = Frame(error_window, width=300, height=150)
    prompt_frame.pack(side=BOTTOM)

    closing = False

    def button_action(action):
        file_override = action
        closing = True
        #error_window.destroy()

    button_continue = Button(prompt_frame,
                     text = "Continue",
                     command =error_window.destroy())
    button_continue.pack(side=LEFT)
    button_cancel = Button(prompt_frame,
                     text = "Cancel",
                     command = error_window.destroy())
    button_cancel.pack(side=RIGHT)

    if closing:
        error_window.destroy()
        file_override = False

def finish_prompt():
    # Create the root window
    finish_window = Tk()
    finish_window.title('Finished')
    finish_window.geometry("200x100")
    finish_window.config()
    finish_main_frame = ttk.Frame(finish_window)
    finish_main_frame.pack(fill="both", expand=1)
    finish_main_frame.grid_rowconfigure(0, weight=2)
    finish_main_frame.grid_rowconfigure(1, weight=1)
    finish_main_frame.grid_columnconfigure(0, weight=1)
    message_frame = ttk.Label(finish_main_frame, text=("Process has finished")).grid(row=0, column=0)
    prompt_frame = Frame(finish_main_frame)
    prompt_frame.grid(row=1,column=0)
    button_continue = Button(prompt_frame,
                     text = "Continue",
                     command = finish_window.destroy)
    button_continue.grid()

def helper():
    print("test")


def set_text(entry,text):
    entry.delete(0,END)
    entry.insert(0,text)
    return

# Variable Initialised
arch_file = ""
circuit_file = ""
route_file = ""
out_dir = ""
database_dir = ""
database_name = ""
programming_in = ""
switch_out_dir = ""
switch_out_name = ""
routing_width = ""
args_pass = ""
task_file = ""
parse_file = ""
mod_in = False
mod_out = False
VTR_path = "$VTR_ROOT"
ZeroAMP_url = 'https://www.zeroamp.eu'

# Create the root window
window = Tk()
window.title('ZeroAMP Tool Suite')
window.geometry('800x675')
window.config()

# Logo Function
def ZeroAMP_click():
    webbrowser.open(ZeroAMP_url)

logo_frame = Frame(window)
logo_frame.config(bg="white")
logo_frame.pack(side=TOP)
img = Image.open("assets/ZeroAMP_logo.png")
resized_img= img.resize((361,130))
resized_img = ImageTk.PhotoImage(resized_img)
img_label= Label(image=resized_img)
logo_button= Button(logo_frame, image=resized_img,command=ZeroAMP_click,borderwidth=0,relief="sunken")
logo_button.config(activebackground=logo_button.cget('background'))
logo_button.grid()

# Permanent Buttons
exit_frame = Frame(window)
exit_frame.pack(side=BOTTOM)
button_exit = Button(exit_frame,
                     text = "Exit",
                     command = exit)
button_exit.grid(row=2,column=0)
button_help = Button(exit_frame,
                     text = "Help",
                     command = helper)
button_help.grid(row=2,column=1)

# Tabs
tabControl = ttk.Notebook(window)
VTR_tab = ttk.Frame(tabControl)
Routing = ttk.Frame(tabControl)
Programming = ttk.Frame(tabControl)
UI_Setting = ttk.Frame(tabControl)
tabControl.add(VTR_tab, text='VTR')
tabControl.add(Routing, text='Routing Export')
tabControl.add(Programming, text='Programming')

# Uncomment once UI Setting is populated
#tabControl.add(UI_Setting, text='UI Settings')

tabControl.pack(fill="both", expand=1,padx=8, pady=8)
VTR_subtab = ttk.Notebook(VTR_tab)
VTR_single = ttk.Frame(VTR_subtab)
VTR_batch = ttk.Frame(VTR_subtab)
VTR_subtab.add(VTR_single, text='Single')
VTR_subtab.add(VTR_batch, text='Batch')
VTR_subtab.pack(fill="both", expand=1,padx=8, pady=8)


#--------------------------
#
#       VTR Tab
#
#--------------------------

#
#   Single Execution
#

VTR_single.grid_rowconfigure((0,1,2), weight=1)
VTR_single.grid_columnconfigure(0, weight=1)
VTR_single.grid_columnconfigure(1, weight=2)

VTR_single_left_frame = ttk.Frame(VTR_single)
VTR_single_left_frame.grid(row=0, column=0)
VTR_single_left_frame.grid_rowconfigure((0,1), weight=1)
VTR_single_left_frame.grid_columnconfigure(0, weight=1)

# TODO: Make sub tab for single file and batch process
VTR_single_top_left_frame = ttk.Frame(VTR_single_left_frame)
VTR_single_top_left_frame.grid(row=0, column=0)
VTR_single_top_left_frame.grid_rowconfigure((0,1,2,3,4,5), weight=1)
VTR_single_top_left_frame.grid_columnconfigure((0,1), weight=1)
#VTR_single_top_left_frame.grid_columnconfigure(1, weight=1)

# VTR Architecture Setup
ttk.Label(VTR_single_top_left_frame, text="Architecture").grid(row=0, column=0)
arch_button = Button(VTR_single_top_left_frame,
                        text = "Browse",
                        command = lambda: browseArchitecture(arch_file,arch_entry))
arch_entry = ttk.Entry(VTR_single_top_left_frame, width="40")
arch_entry.grid(row=1, column=0, pady=4)
arch_button.grid(row=1, column=1, pady=4,padx=8)

# VTR Circuit Setup
ttk.Label(VTR_single_top_left_frame, text="Circuit").grid(row=2, column=0)
circuit_button = Button(VTR_single_top_left_frame,
                        text = "Browse",
                        command = lambda: browseCircuit(circuit_file,circuit_entry))
circuit_entry = ttk.Entry(VTR_single_top_left_frame, width="40")
circuit_entry.grid(row=3, column=0, pady=4)
circuit_button.grid(row=3, column=1, pady=4,padx=8)

# VTR Output Directory
ttk.Label(VTR_single_top_left_frame, text="Output Directory").grid(row=4, column=0)
out_dir_button = Button(VTR_single_top_left_frame,
                        text = "Browse",
                        command = lambda: browseOutDir(out_dir,out_dir_entry))
out_dir_entry = ttk.Entry(VTR_single_top_left_frame, width="40")
out_dir_entry.grid(row=5, column=0, pady=4)
out_dir_button.grid(row=5, column=1, pady=4,padx=8)

VTR_single_bottom_left_frame = ttk.Frame(VTR_single_left_frame)
VTR_single_bottom_left_frame.grid(row=1, column=0)
VTR_single_bottom_left_frame.grid_rowconfigure((0,1), weight=1)
VTR_single_bottom_left_frame.grid_columnconfigure((0,1), weight=1)

# VTR Width
ttk.Label(VTR_single_bottom_left_frame, text="Routing Width").grid(row=0, column=0)
width_entry = ttk.Entry(VTR_single_bottom_left_frame, width="5")
width_entry.grid(row=0, column=1, columnspan=2, padx=8, pady=8)

# VTR Tickboxes
analysis_tick = IntVar()
analysis_entry = Checkbutton(VTR_single_bottom_left_frame, text='Analysis',variable=analysis_tick, onvalue=1, offvalue=0)
analysis_entry.grid(row=1, column=0,padx=8, pady=8)


VTR_single_right_frame = ttk.Frame(VTR_single)
VTR_single_right_frame.grid(row=0, column=1)
VTR_single_right_frame.grid_rowconfigure((0,1), weight=1)
VTR_single_right_frame.grid_columnconfigure(0, weight=1)
VTR_single_right_frame.grid_columnconfigure(1, weight=2)

# VTR Arguments Setup
ttk.Label(VTR_single_right_frame, text="Arguments").grid(row=0, column=0)
args_entry = Text(VTR_single_right_frame, width="35", height="8")
args_entry.grid(row=1, column=0)

# Run VTR
def VTR_run():

    # Field Polling
    circuit_file = circuit_entry.get()
    arch_file = arch_entry.get()
    out_dir = out_dir_entry.get()
    routing_width = width_entry.get()
    args_pass = ""

    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    
    status = sp.call("cd ;" 
    + "cd " 
    + out_dir 
    + "; " 
    + "$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py     "
    + circuit_file
    + "     "
    + arch_file
    + "     -temp_dir "
    + out_dir
    + "     --route_chan_width "
    + routing_width
    + " "
    + args_pass,   # add args entry
    shell=True)
    finish_prompt()

def VTR_display():
    
    # Field Polling
    circuit_file = circuit_entry.get()
    arch_file = arch_entry.get()
    out_dir = out_dir_entry.get()
    routing_width = width_entry.get()
    #analysis_tick = analysis_entry.get()
    args_pass = ""
    
    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    if analysis_tick.get():
        status = sp.call("cd ;"
        + "cd "  
        + out_dir 
        + "; " 
        + "$VTR_ROOT/vpr/vpr     "
        + arch_file
        + "     "
        + os.path.splitext(os.path.basename(circuit_file))[0]
        + " --circuit_file "
        + os.path.splitext(os.path.basename(circuit_file))[0]
        + ".pre-vpr.blif    --route_chan_width "
        + routing_width
        + "  --disp on --analysis "
        + args_pass,   # add args entry
        shell=True)
    else:
        status = sp.call("cd " 
        + out_dir 
        + "; " 
        + "$VTR_ROOT/vpr/vpr     "
        + arch_file
        + "     "
        + os.path.splitext(os.path.basename(circuit_file))[0]
        + " --circuit_file "
        + os.path.splitext(os.path.basename(circuit_file))[0]
        + ".pre-vpr.blif    --route_chan_width "
        + routing_width
        + "  --disp on "
        + args_pass,   # add args entry
        shell=True)

VTR_single_bottom_frame = ttk.Frame(VTR_single)
VTR_single_bottom_frame.grid(row=1, column=0, columnspan=2)
VTR_single_bottom_frame.grid_rowconfigure(0, weight=1)
VTR_single_bottom_frame.grid_columnconfigure((0,1), weight=1)

VTR_run_button = Button(VTR_single_bottom_frame,
                        text = "Run",
                        command = lambda: VTR_run())
VTR_run_button.grid(row=0, column=0, pady=4,padx=8)
VTR_run_button.config(height=3, width=6)
VTR_display_button = Button(VTR_single_bottom_frame,
                        text = "Display",
                        command = lambda: VTR_display())
VTR_display_button.grid(row=0, column=1, pady=4,padx=8)
VTR_display_button.config(height=3, width=6)


#
#   Batch Execution
#
#$VTR_ROOT/vtr_flow/scripts/run_vtr_task.py -l $VTR_ROOT/vtr_flow/tasks/regression_tests/vtr_same_side/ultrascale_ispd/task_list_limited.txt

#$VTR_ROOT/vtr_flow/scripts/parse_vtr_task.py -l $VTR_ROOT/vtr_flow/tasks/regression_tests/vtr_same_side/stratixiv_arch.timing/task_list_limited.txt
VTR_batch.grid_rowconfigure((0,1), weight=1)
VTR_batch.grid_columnconfigure(0, weight=1)
VTR_batch.grid_columnconfigure(1, weight=2)

VTR_batch_left_frame = ttk.Frame(VTR_batch)
VTR_batch_left_frame.grid(row=0, column=0)
VTR_batch_left_frame.grid_rowconfigure((0,1,2,3), weight=1)
VTR_batch_left_frame.grid_columnconfigure(0, weight=1)
VTR_batch_left_frame.grid_columnconfigure(1, weight=1)

# VTR Task List
ttk.Label(VTR_batch_left_frame, text="Task List").grid(row=0, column=0)
task_button = Button(VTR_batch_left_frame,
                        text = "Browse",
                        command = lambda: browseTask(task_file,task_entry))
task_entry = ttk.Entry(VTR_batch_left_frame, width="35")
task_entry.grid(row=1, column=0, pady=4)
task_button.grid(row=1, column=1, pady=4,padx=8)

# VTR Parse Parameter
ttk.Label(VTR_batch_left_frame, text="Parse Parameter").grid(row=2, column=0)
parse_button = Button(VTR_batch_left_frame,
                        text = "Browse",
                        command = lambda: browseTask(parse_file,parse_entry))
parse_entry = ttk.Entry(VTR_batch_left_frame, width="35")
parse_entry.grid(row=3, column=0, pady=4)
parse_button.grid(row=3, column=1, pady=4,padx=8)

# Run VTR Batch
def VTR_batch_run():

    # Field Polling
    task_file = task_entry.get()
    out_dir = out_dir_entry.get()
    routing_width = width_entry.get()
    args_pass = ""

    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    status = sp.call("cd " 
    + VTR_path 
    + "; " 
    + "$VTR_ROOT/vtr_flow/scripts/run_vtr_task.py -l "
    + task_file,
    shell=True)
    finish_prompt()

def VTR_batch_parse():

    # Field Polling
    task_file = task_entry.get()
    out_dir = out_dir_entry.get()
    routing_width = width_entry.get()
    args_pass = ""

    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    status = sp.call("cd " 
    + VTR_path 
    + "; " 
    + "$VTR_ROOT/vtr_flow/scripts/run_vtr_task.py -l "
    + task_file,
    shell=True)
    finish_prompt()

VTR_batch_right_frame = ttk.Frame(VTR_batch)
VTR_batch_right_frame.grid(row=0, column=1)
VTR_batch_right_frame.grid_rowconfigure((0,1), weight=1)
VTR_batch_right_frame.grid_columnconfigure(0, weight=1)

# VTR Batch Arguments Setup
ttk.Label(VTR_batch_right_frame, text="Arguments").grid(row=0, column=0)
args_entry = Text(VTR_batch_right_frame, width="35", height="8")
args_entry.grid(row=1, column=0, pady=4)

# VTR Task Run and Parse
VTR_batch_bottom_frame = ttk.Frame(VTR_batch)
VTR_batch_bottom_frame.grid(row=1, column=0, columnspan=2)
VTR_batch_bottom_frame.grid_rowconfigure(0, weight=1)
VTR_batch_bottom_frame.grid_columnconfigure((0,1), weight=1)

VTR_run_button = Button(VTR_batch_bottom_frame,
                        text = "Run",
                        command = lambda: VTR_batch_run())
VTR_run_button.grid(row=0, column=0, pady=4,padx=8)
VTR_run_button.config(height=3, width=6)
VTR_display_button = Button(VTR_batch_bottom_frame,
                        text = "Parse",
                        command = lambda: VTR_batch_parse())
VTR_display_button.grid(row=0, column=1, pady=4,padx=8)
VTR_display_button.config(height=3, width=6)


#--------------------------
#
#       Routing Export Tab
#
#--------------------------

Routing.grid_rowconfigure((0,1), weight=1)
Routing.grid_columnconfigure(0, weight=1)
Routing_top_frame = ttk.Frame(Routing)
Routing_top_frame.grid(row=0, column=0)
Routing_top_frame.grid_rowconfigure((0,1,2,3,4,5,6,7), weight=1)
Routing_top_frame.grid_columnconfigure((0,1,2,3), weight=1)

# Routing Input Setup
ttk.Label(Routing_top_frame, text="Routing Outcome").grid(row=0, column=0, columnspan=2)
routing_in_button = Button(Routing_top_frame,
                        text = "Browse",
                        command = lambda: browseRoute(route_file,routing_in_entry))
routing_in_entry = ttk.Entry(Routing_top_frame, width="35")
routing_in_entry.grid(row=1, column=0, columnspan=2, pady=4)
routing_in_button.grid(row=1, column=2, columnspan=2, pady=4,padx=8, sticky="w")

# Database Output Directory
ttk.Label(Routing_top_frame, text="Database Output Folder").grid(row=2, column=0, columnspan=2)
database_dir_button = Button(Routing_top_frame,
                        text = "Browse",
                        command = lambda: browseOutDir(database_dir,database_dir_entry))
database_dir_entry = ttk.Entry(Routing_top_frame, width="35")
database_dir_entry.grid(row=3, column=0, columnspan=2, pady=4)
database_dir_button.grid(row = 3, column=2, columnspan=2, pady=4,padx=8, sticky="w")

# Database Output File Name Setup
ttk.Label(Routing_top_frame, text="Name").grid(row=4, column=0, columnspan=2)
database_name_entry = ttk.Entry(Routing_top_frame, width="35")
database_name_entry.grid(row=5, column=0, columnspan=4, pady=4, sticky="w")
database_name_entry.insert(END, 'SB_database.csv')

# Regex Filtered Output Setup
ttk.Label(Routing_top_frame, text="Regex Output").grid(row=6, column=0, columnspan=2)
regex_entry = ttk.Entry(Routing_top_frame, width="35")
regex_entry.grid(row=7, column=0, columnspan=3, pady=4, sticky="w")

# Regex Tickbox
regex_tick = IntVar()
regex_tick_entry = Checkbutton(Routing_top_frame, text='Regex Output',variable=regex_tick, onvalue=1, offvalue=0)
regex_tick_entry.grid(row=7, column=2, columnspan=1, pady=4)

Routing_bottom_frame = ttk.Frame(Routing)
Routing_bottom_frame.grid(row=1, column=0, sticky="n")
Routing_bottom_frame.grid_rowconfigure(0, weight=1)
Routing_bottom_frame.grid_columnconfigure(0, weight=1)
#Routing_bottom_frame.grid_columnconfigure(1, weight=1)

def netlist_run():
    
    error_flag = False
    file_override = False
    route_file = routing_in_entry.get()
    regex_file = regex_entry.get()
    database_dir = database_dir_entry.get()
    database_name = database_name_entry.get()

    # Forces .csv finishing names
    if not os.path.splitext(database_name)[1] == ".csv":
        database_name = os.path.splitext(database_name)[0] + ".csv"
    if not os.path.splitext(regex_file)[1] == ".csv":
        regex_file = os.path.splitext(regex_file)[0] + ".csv"

    # Make sure route file exists
    if not os.path.isfile(route_file):
        set_text(routing_in_entry,"Missing Value")
        error_flag = True
    
    

    # Make sure regex doesn't exist and is not empty
    if regex_tick.get():
        if os.path.isfile(database_dir + "/" + regex_file):
            #file_exist(regex_file, file_override)
            file_override = True # Force for testing
            if not file_override:
                error_flag = True
                print("No Override")            

            file_override = False
            
        if not regex_file and not regex_file=="Missing Value":
            set_text(regex_entry,"Missing Value")
            error_flag = True
    else:
        set_text(regex_entry,"")
        regex_file = None
    
    file_override = True # Force for testing

    # Make Database doesn't exist but has a value
    if not os.path.isdir(database_dir):
        set_text(database_dir_entry,"Missing Value")
        error_flag = True
    if os.path.isfile(database_dir + "/" + database_name):
        #file_exist(database_name, file_override)
        file_override = True # Force for testing
        if not file_override:
            error_flag = True
        file_override = False
    
    # Runs netlist parse if no errors are found
    if not error_flag:
        if regex_file:
            lib.netlist_parse.netlist_parse(route_file,database_dir + "/" + regex_file,database_dir + "/" + database_name)
        else:
            lib.netlist_parse.netlist_parse(route_file,regex_file,database_dir + "/" + database_name)        
        finish_prompt()
    error_flag = False
    

Routing_run_button = Button(Routing_bottom_frame,
                        text = "Run",
                        command = lambda: netlist_run())
Routing_run_button.grid(row=0, column=0)
Routing_run_button.config(height=3, width=6)

#--------------------------
#
#       Programming Tab
#
#--------------------------

Programming.grid_rowconfigure((0,1), weight=1)
Programming.grid_columnconfigure(0, weight=1)
Programming_top_frame = ttk.Frame(Programming)
Programming_top_frame.grid(row=0, column=0)
Programming_top_frame.grid_rowconfigure((0,1,2,3,4,5), weight=1)
Programming_top_frame.grid_columnconfigure((0,1), weight=1)

# Routing Input Setup
ttk.Label(Programming_top_frame, text="Processed Routing").grid(row=0, column=0)
programming_in_button = Button(Programming_top_frame,
                        text = "Browse",
                        command = lambda: browseCSV(programming_in,programming_in_entry))
programming_in_entry = ttk.Entry(Programming_top_frame, width="35")
programming_in_entry.grid(row=1, column=0, pady=4)
programming_in_button.grid(row=1, column=1,padx=8, pady=4, sticky="w")

# Switch Position Output Folder
ttk.Label(Programming_top_frame, text="Switch Position Output Folder").grid(row=2, column=0)
switch_out_dir_button = Button(Programming_top_frame,
                        text = "Browse",
                        command = lambda: browseOutDir(switch_out_dir,switch_out_dir_entry))
switch_out_dir_entry = ttk.Entry(Programming_top_frame, width="35")
switch_out_dir_entry.grid(row=3, column=0, pady=4)
switch_out_dir_button.grid(row=3, column=1,padx=8, pady=4, sticky="w")

# Database Output File Name Setup
ttk.Label(Programming_top_frame, text="Name").grid(row=4, column=0)
switch_out_name_entry = ttk.Entry(Programming_top_frame, width="35")
switch_out_name_entry.grid(row=5, column=0, pady=4)
switch_out_name_entry.insert(END, 'SB_position.csv')

# Loading previous parsing Tickbox
load_tick = IntVar()
load_tick_entry = Checkbutton(Programming_top_frame, text='Load From File',variable=load_tick, onvalue=1, offvalue=0)
load_tick_entry.grid(row=5, column=1, pady=4)

def programming_run():
    error_flag = False
    file_override = False
    programming_in = programming_in_entry.get()
    switch_out_dir = switch_out_dir_entry.get()
    switch_out_name = switch_out_name_entry.get()
    
    if load_tick.get():
        lib.switch_position.switch_position(programming_in, switch_out_dir + "/" + switch_out_name,True)
        print("loaded")
    else:
        lib.switch_position.switch_position(programming_in, switch_out_dir + "/" + switch_out_name,False)
        print("not loaded")
    finish_prompt()

Programming_bottom_frame = ttk.Frame(Programming)
Programming_bottom_frame.grid(row=1, column=0, sticky="n")
Programming_bottom_frame.grid_rowconfigure(0, weight=1)
Programming_bottom_frame.grid_columnconfigure(0, weight=1)

Programming_run_button = Button(Programming_bottom_frame,
                        text = "Run",
                        command = lambda: programming_run())
Programming_run_button.grid(row=0, column=0)
Programming_run_button.config(height=3, width=6)

#--------------------------
#
#       UI Setting Tab
#
#--------------------------


  
# Let the window wait for any events
window.mainloop()