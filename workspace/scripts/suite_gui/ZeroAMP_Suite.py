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
import subprocess
from multiprocessing.sharedctypes import Value
import sys

import lib.netlist_parse
import lib.switch_position
import lib.Switchblock_Router.src.cpp.sb_route

# import filedialog module
from tkinter import filedialog

from tkinter import ttk

#--------------------------------------------------------------------------------------------------------------------------------
#
#   Title:  ZeroAMP_Suite.py
#   Date:   July 2022
#   Author: Victor Marot and Sam Payne (Matrix Routing)
#
#   Description:
#   A GUI for the ZeroAMP tool suite based on the Verilog-To-Routing tool suite.
#   Its purpose is to provide a GUI for simulation and programming NEM-based FPGAs as ZeroAMP targets to produce.
#
#--------------------------------------------------------------------------------------------------------------------------------

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

def browseParse(filename,field):
    filename = filedialog.askopenfilename(initialdir = "~/VTR-Tools/workspace/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
    if filename:
        _,file_extension = os.path.splitext(filename)
        if file_extension != ".txt":
            set_text(field,"Error: Requires parse parameter file type") 
        else:
            set_text(field,filename)

def browseQoR(filename,field):
    filename = filedialog.askopenfilename(initialdir = "~/VTR-Tools/workspace/",
                                          title = "Select a File",
                                          filetypes = (("Text files",
                                                        "*.txt*"),
                                                       ("all files",
                                                        "*.*")))
    if filename:
        _,file_extension = os.path.splitext(filename)
        if file_extension != ".txt":
            set_text(field,"Error: Requires QoR file type") 
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
    webbrowser.open("assets/help.html")

def set_text(entry,text):
    entry.delete(0,END)
    entry.insert(0,text)
    return

def cpp_compiler(file, dir):
    curr_dir = os.path.dirname(os.path.abspath(__file__)) + dir
    if not os.path.isfile(os.path.join(curr_dir,file)):
        make_progress = subprocess.Popen("cd " + curr_dir + "; make", shell=True, stdout=subprocess.PIPE, stderr=sys.stdout.fileno())
        make_progress.wait()

# Variable Initialised
arch_file = ""
circuit_file = ""
route_file = ""
out_dir_single_vtr = ""
out_dir_parse = ""
out_dir = ""
database_dir = ""
database_name = ""
programming_in = ""
switch_out_dir = ""
switch_out_name = ""
routing_width = ""
args_pass = ""
task_parse_file = ""
task_batch_file = ""
parse_file = ""
QoR_file = ""
Matrix_in = ""
Matrix_out_dir = ""
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
exit_frame.pack(side=BOTTOM, fill="x")
exit_frame.grid_rowconfigure(0, weight=1)
exit_frame.grid_columnconfigure((0,1), weight=1)

# Exit Button Frame
exit_frame_left = Frame(exit_frame)
exit_frame_left.grid_rowconfigure(0, weight=1)
exit_frame_left.grid_columnconfigure(0, weight=1)
exit_frame_left.grid(row=0,column=0,sticky="w")

# Help Button Frame
exit_frame_right = Frame(exit_frame)
exit_frame_right.grid_rowconfigure(0, weight=1)
exit_frame_right.grid_columnconfigure(0, weight=1)
exit_frame_right.grid(row=0,column=1,sticky="e")

# Exit and Help button initialisation
button_exit = Button(exit_frame_right,
                     text = "Exit",
                     command = exit)
button_exit.grid(row=0,column=0, pady=8,padx=8)
button_help = Button(exit_frame_left,
                     text = "Help",
                     command = helper)
button_help.grid(row=0,column=0, pady=8,padx=8)

# Tabs
tabControl = ttk.Notebook(window)
VTR_tab = ttk.Frame(tabControl)
Routing = ttk.Frame(tabControl)
Programming = ttk.Frame(tabControl)
Matrix = ttk.Frame(tabControl)
UI_Setting = ttk.Frame(tabControl)
tabControl.add(VTR_tab, text='VTR')
tabControl.add(Routing, text='Routing Export')
tabControl.add(Programming, text='Programming')
tabControl.add(Matrix, text='Matrix Routing')

# Uncomment once UI Setting is populated
#tabControl.add(UI_Setting, text='UI Settings')

tabControl.pack(fill="both", expand=1,padx=8, pady=8)
VTR_subtab = ttk.Notebook(VTR_tab)
VTR_single = ttk.Frame(VTR_subtab)
VTR_batch = ttk.Frame(VTR_subtab)
VTR_parse = ttk.Frame(VTR_subtab)
VTR_subtab.add(VTR_single, text='Single')
VTR_subtab.add(VTR_batch, text='Batch')
VTR_subtab.add(VTR_parse, text='Parse')
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
out_dir_single_vtr_button = Button(VTR_single_top_left_frame,
                        text = "Browse",
                        command = lambda: browseOutDir(out_dir_single_vtr,out_dir_single_vtr_entry))
out_dir_single_vtr_entry = ttk.Entry(VTR_single_top_left_frame, width="40")
out_dir_single_vtr_entry.grid(row=5, column=0, pady=4)
out_dir_single_vtr_button.grid(row=5, column=1, pady=4,padx=8)

VTR_single_bottom_left_frame = ttk.Frame(VTR_single_left_frame)
VTR_single_bottom_left_frame.grid(row=1, column=0)
VTR_single_bottom_left_frame.grid_rowconfigure((0,1), weight=1)
VTR_single_bottom_left_frame.grid_columnconfigure((0,1), weight=1)

# VTR Width
ttk.Label(VTR_single_bottom_left_frame, text="Routing Width").grid(row=0, column=0)
VTR_width_entry = ttk.Entry(VTR_single_bottom_left_frame, width="5")
VTR_width_entry.grid(row=0, column=1, columnspan=2, padx=8, pady=8)

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
    out_dir_single_vtr = out_dir_single_vtr_entry.get()
    routing_width = VTR_width_entry.get()
    args_pass = ""
    bash_line = ""

    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    bash_line = ("cd ;" 
    + "cd " 
    + out_dir_single_vtr 
    + "; " 
    + "$VTR_ROOT/vtr_flow/scripts/run_vtr_flow.py     "
    + circuit_file
    + "     "
    + arch_file
    + "     -temp_dir "
    + out_dir_single_vtr)

    if routing_width:
        bash_line += "     --route_chan_width " + routing_width
        print("Routing is specified")
    
    bash_line += " " + args_pass   

    status = sp.call(bash_line, shell=True)
    finish_prompt()

def VTR_display():
    
    # Field Polling
    circuit_file = circuit_entry.get()
    arch_file = arch_entry.get()
    out_dir_single_vtr = out_dir_single_vtr_entry.get()
    routing_width = VTR_width_entry.get()
    #analysis_tick = analysis_entry.get()
    args_pass = ""
    bash_line = ""
    
    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    bash_line = ("cd ;"
        + "cd "  
        + out_dir_single_vtr 
        + "; " 
        + "$VTR_ROOT/vpr/vpr     "
        + arch_file
        + "     "
        + os.path.splitext(os.path.basename(circuit_file))[0]
        + " --circuit_file "
        + os.path.splitext(os.path.basename(circuit_file))[0]
        + ".pre-vpr.blif")

    if routing_width:
        bash_line += "     --route_chan_width " + routing_width
        print("Routing is specified")

    bash_line += "  --disp on"

    if analysis_tick.get():
        bash_line += " --analysis"

    bash_line += " " + args_pass
    status = sp.call(bash_line,shell=True)
    finish_prompt()

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
VTR_batch_left_frame.grid_rowconfigure((0,1), weight=1)
VTR_batch_left_frame.grid_columnconfigure(0, weight=1)

VTR_batch_top_left_frame = ttk.Frame(VTR_batch_left_frame)
VTR_batch_top_left_frame.grid(row=0, column=0)
VTR_batch_top_left_frame.grid_rowconfigure((0,1,2), weight=1)
VTR_batch_top_left_frame.grid_columnconfigure(0, weight=1)
VTR_batch_top_left_frame.grid_columnconfigure(1, weight=1)

# VTR Task List
ttk.Label(VTR_batch_top_left_frame, text="Task List").grid(row=0, column=0)
task_batch_button = Button(VTR_batch_top_left_frame,
                        text = "Browse",
                        command = lambda: browseTask(task_batch_file,task_batch_entry))
task_batch_entry = ttk.Entry(VTR_batch_top_left_frame, width="35")
task_batch_entry.grid(row=1, column=0, pady=4)
task_batch_button.grid(row=1, column=1, pady=4,padx=8)

VTR_batch_bottom_left_frame = ttk.Frame(VTR_batch_left_frame)
VTR_batch_bottom_left_frame.grid(row=1, column=0)
VTR_batch_bottom_left_frame.grid_rowconfigure(0, weight=1)
VTR_batch_bottom_left_frame.grid_columnconfigure(0, weight=1)

# VTR Short Name Tickboxes
short_name_tick = IntVar()
short_name_entry = Checkbutton(VTR_batch_bottom_left_frame, text='Short Name',variable=short_name_tick, onvalue=1, offvalue=0)
short_name_entry.grid(row=0, column=0,padx=8, pady=8)

# Run VTR Batch
def VTR_batch_run():

    # Field Polling
    task_batch_file = task_batch_entry.get()
    short_name = short_name_tick.get()
    args_pass = ""
    bash_line = "cd " + os.path.dirname(task_batch_file) + "; $VTR_ROOT/vtr_flow/scripts/run_vtr_task.py -l " + os.path.basename(task_batch_file)

    if short_name:
        bash_line += " -short_task_names"

    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    bash_line += " " + args_pass
    status = sp.call(bash_line,shell=True)
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

#
#   Parse Execution
#
VTR_parse.grid_rowconfigure((0,1), weight=1)
VTR_parse.grid_columnconfigure(0, weight=1)
VTR_parse.grid_columnconfigure(1, weight=2)

VTR_parse_left_frame = ttk.Frame(VTR_parse)
VTR_parse_left_frame.grid(row=0, column=0)
VTR_parse_left_frame.grid_rowconfigure((0,1), weight=1)
VTR_parse_left_frame.grid_columnconfigure(0, weight=1)

VTR_parse_top_left_frame = ttk.Frame(VTR_parse_left_frame)
VTR_parse_top_left_frame.grid(row=0, column=0)
VTR_parse_top_left_frame.grid_rowconfigure((0,1,2,3,4,5), weight=1)
VTR_parse_top_left_frame.grid_columnconfigure((0,1), weight=1)

# VTR Task List
ttk.Label(VTR_parse_top_left_frame, text="Task List").grid(row=0, column=0)
task_parse_button = Button(VTR_parse_top_left_frame,
                        text = "Browse",
                        command = lambda: browseTask(task_parse_file,task_parse_entry))
task_parse_entry = ttk.Entry(VTR_parse_top_left_frame, width="35")
task_parse_entry.grid(row=1, column=0, pady=4)
task_parse_button.grid(row=1, column=1, pady=4,padx=8)

# VTR Parse Parameter
ttk.Label(VTR_parse_top_left_frame, text="Parse Parameters").grid(row=2, column=0)
parse_button = Button(VTR_parse_top_left_frame,
                        text = "Browse",
                        command = lambda: browseParse(parse_file,parse_entry))
parse_entry = ttk.Entry(VTR_parse_top_left_frame, width="35")
parse_entry.grid(row=3, column=0, pady=4)
parse_button.grid(row=3, column=1, pady=4,padx=8)

# NOT IN USE BECAUSE PARSE PARAM ENOUGH
# VTR QoR Parameter
# ttk.Label(VTR_parse_top_left_frame, text="QoR Parameter").grid(row=4, column=0)
# QoR_button = Button(VTR_parse_top_left_frame,
#                         text = "Browse",
#                         command = lambda: browseQoR(QoR_file,QoR_entry))
# QoR_entry = ttk.Entry(VTR_parse_top_left_frame, width="35")
#QoR_entry.grid(row=5, column=0, pady=4)
#QoR_button.grid(row=5, column=1, pady=4,padx=8)        

# VTR Output Directory
ttk.Label(VTR_parse_top_left_frame, text="Output Directory").grid(row=4, column=0)
out_dir_parse_button = Button(VTR_parse_top_left_frame,
                        text = "Browse",
                        command = lambda: browseOutDir(out_dir_parse,out_dir_parse_entry))
out_dir_parse_entry = ttk.Entry(VTR_parse_top_left_frame, width="35")
out_dir_parse_entry.grid(row=5, column=0, pady=4)
out_dir_parse_button.grid(row=5, column=1, pady=4,padx=8)


VTR_parse_bottom_left_frame = ttk.Frame(VTR_parse_left_frame)
VTR_parse_bottom_left_frame.grid(row=1, column=0)
VTR_parse_bottom_left_frame.grid_rowconfigure(0, weight=1)
VTR_parse_bottom_left_frame.grid_columnconfigure((0,1), weight=1)

# VTR Batch Tickboxes
batch_tick = IntVar()
batch_entry = Checkbutton(VTR_parse_bottom_left_frame, text='Batch',variable=batch_tick, onvalue=1, offvalue=0)
batch_entry.grid(row=0, column=0,padx=8, pady=8)

# Run VTR Batch
def VTR_run_parse():

    # Field Polling
    task_parse_file = task_parse_entry.get()
    batch = batch_tick.get()
    #QoR_file = QoR_entry.get()
    parse_file = parse_entry.get()
    out_dir_parse = out_dir_parse_entry.get()
    args_pass = ""

    if batch:
        # TOFIX: NOT WORKING
        # TODO: First expression might be the correct syntax but seems to not work very well. Will need modification to hyperlink in helper. 
        #bash_line = "cd " + VTR_path + "; $VTR_ROOT/vtr_flow/scripts/run_vtr_task.py -l " + task_file + " -parse"
        bash_line = "cd " + os.path.dirname(task_parse_file) + "; $VTR_ROOT/vtr_flow/scripts/python_libs/vtr/parse_vtr_task.py -l " + os.path.basename(task_parse_file)
    else:
        bash_line = "cd " + VTR_path + "; $VTR_ROOT/vtr_flow/scripts/python_libs/vtr/parse_vtr_flow.py " + out_dir_parse + " " + parse_file
    # Merge argument lines
    for line in args_entry.get('1.0', END).splitlines():
        args_pass = args_pass + " " + line

    bash_line += " " + args_pass
    status = sp.call(bash_line,shell=True)
    finish_prompt()

VTR_parse_right_frame = ttk.Frame(VTR_parse)
VTR_parse_right_frame.grid(row=0, column=1)
VTR_parse_right_frame.grid_rowconfigure((0,1), weight=1)
VTR_parse_right_frame.grid_columnconfigure(0, weight=1)

# VTR Parse Arguments Setup
ttk.Label(VTR_parse_right_frame, text="Arguments").grid(row=0, column=0)
args_entry = Text(VTR_parse_right_frame, width="35", height="8")
args_entry.grid(row=1, column=0, pady=4)

# VTR Task Run and Parse
VTR_parse_bottom_frame = ttk.Frame(VTR_parse)
VTR_parse_bottom_frame.grid(row=1, column=0, columnspan=2)
VTR_parse_bottom_frame.grid_rowconfigure(0, weight=1)
VTR_parse_bottom_frame.grid_columnconfigure(0, weight=1)

VTR_run_button = Button(VTR_parse_bottom_frame,
                        text = "Parse",
                        command = lambda: VTR_run_parse())
VTR_run_button.grid(row=0, column=0, pady=4,padx=8)
VTR_run_button.config(height=3, width=6)

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
#       Switchblock Matrix Routing Tab
#
#--------------------------

Matrix.grid_rowconfigure((0,1), weight=1)
Matrix.grid_columnconfigure(0, weight=1)
Matrix_top_frame = ttk.Frame(Matrix)
Matrix_top_frame.grid(row=0, column=0)
Matrix_top_frame.grid_rowconfigure(0, weight=1)
Matrix_top_frame.grid_columnconfigure((0,1), weight=1)

# Top Left Frame
Matrix_top_left_frame = ttk.Frame(Matrix_top_frame)
Matrix_top_left_frame.grid(row=0, column=0)
Matrix_top_left_frame.grid_rowconfigure((0,1), weight=1)
Matrix_top_left_frame.grid_columnconfigure(0, weight=1)

# Top Right Frame
Matrix_top_right_frame = ttk.Frame(Matrix_top_frame)
Matrix_top_right_frame.grid(row=0, column=1, padx=50)
Matrix_top_right_frame.grid_rowconfigure((0,1,2,3), weight=1)
Matrix_top_right_frame.grid_columnconfigure(0, weight=1)

# Top Left Top Frame
Matrix_top_left_top_frame = ttk.Frame(Matrix_top_left_frame)
Matrix_top_left_top_frame.grid(row=0, column=0)
Matrix_top_left_top_frame.grid_rowconfigure((0,1,2,3,4,5), weight=1)
Matrix_top_left_top_frame.grid_columnconfigure((0,1), weight=1)

# Top Left Bottom Frame
Matrix_top_left_bottom_frame = ttk.Frame(Matrix_top_left_frame)
Matrix_top_left_bottom_frame.grid(row=1, column=0)
Matrix_top_left_bottom_frame.grid_rowconfigure((0,1), weight=1)
Matrix_top_left_bottom_frame.grid_columnconfigure((0,1,2,3), weight=1)

# Routing Demands File
ttk.Label(Matrix_top_left_top_frame, text="Processed Routing").grid(row=0, column=0)
Matrix_in_button = Button(Matrix_top_left_top_frame,
                        text = "Browse",
                        command = lambda: browseCSV(Matrix_in,Matrix_in_entry))
Matrix_in_entry = ttk.Entry(Matrix_top_left_top_frame, width="35")
Matrix_in_entry.grid(row=1, column=0, pady=4)
Matrix_in_button.grid(row=1, column=1,padx=8, pady=4)

# Matrix Routing Output Folder
ttk.Label(Matrix_top_left_top_frame, text="Output Folder").grid(row=2, column=0)
Matrix_out_dir_button = Button(Matrix_top_left_top_frame,
                        text = "Browse",
                        command = lambda: browseOutDir(Matrix_out_dir,Matrix_out_dir_entry))
Matrix_out_dir_entry = ttk.Entry(Matrix_top_left_top_frame, width="35")
Matrix_out_dir_entry.grid(row=3, column=0, pady=4)
Matrix_out_dir_button.grid(row=3, column=1,padx=8, pady=4)

# Matrix Routing Output Name
ttk.Label(Matrix_top_left_top_frame, text="Name").grid(row=4, column=0)
Matrix_out_name_entry = ttk.Entry(Matrix_top_left_top_frame, width="35")
Matrix_out_name_entry.grid(row=5, column=0, pady=4)
Matrix_out_name_entry.insert(END, 'SB_out.csv')

# Switchblock Width Setup
ttk.Label(Matrix_top_left_bottom_frame, text="Width").grid(row=0, column=0)
matrix_width_entry = ttk.Entry(Matrix_top_left_bottom_frame, width="5")
matrix_width_entry.grid(row=0, column=1, pady=4,padx=8)

# Alpha Parameter Setup
ttk.Label(Matrix_top_left_bottom_frame, text="Alpha").grid(row=0, column=2)
alpha_entry = ttk.Entry(Matrix_top_left_bottom_frame, width="5")
alpha_entry.grid(row=0, column=3, pady=4,padx=8)
alpha_entry.insert(END, '0.95')

# Max Router Iteration
ttk.Label(Matrix_top_left_bottom_frame, text="Max Iterations").grid(row=1, column=0)
max_iteration_entry = ttk.Entry(Matrix_top_left_bottom_frame, width="5")
max_iteration_entry.grid(row=1, column=1, pady=4,padx=8)
max_iteration_entry.insert(END, '500')

# Router Target
ttk.Label(Matrix_top_left_bottom_frame, text="Target").grid(row=1, column=2)
routing_target_entry = ttk.Entry(Matrix_top_left_bottom_frame, width="5")
routing_target_entry.grid(row=1, column=3, pady=4,padx=8)
routing_target_entry.insert(END, '0.90')

# Routing Algorithm Choice
ttk.Label(Matrix_top_right_frame, text="Routing Algorithm Selection").grid(row=0, column=0)
routing_algorithm_entry=Listbox(Matrix_top_right_frame, height="4")
routing_algorithm_entry.insert(END, "Random Hadlocks")  
routing_algorithm_entry.insert(END, "Hadlocks")
routing_algorithm_entry.insert(END, "Simulated Annealing")
routing_algorithm_entry.grid(row=1, column=0, pady=8,padx=8)

# Objective Choice
ttk.Label(Matrix_top_right_frame, text="Objective Selection").grid(row=2, column=0)
routing_objective_entry=Listbox(Matrix_top_right_frame, height="3")
routing_objective_entry.insert(END, "Minimize Sum")  
routing_objective_entry.insert(END, "Minimize Longest Path")
routing_objective_entry.grid(row=3, column=0, pady=8,padx=8)

def Matrix_run():
    
    Matrix_in = Matrix_in_entry.get()
    Matrix_out_dir = Matrix_out_dir_entry.get()
    Matrix_out_name = Matrix_out_name_entry.get()
    matrix_width = matrix_width_entry.get()
    alpha = alpha_entry.get()
    max_iteration = max_iteration_entry.get()
    routing_target = routing_target_entry.get()
    routing_algorithm = 0
    routing_objective = 1
    

    if routing_algorithm_entry.get(ACTIVE) == "Random Hadlocks":
        routing_algorithm = 1
    elif routing_algorithm_entry.get(ACTIVE) == "Hadlocks":
        routing_algorithm = 2
    elif routing_algorithm_entry.get(ACTIVE) == "Simulated Annealing":
        routing_algorithm = 3
    else:
        routing_algorithm = 1
        print("No algorithm specified. Defaulting to Random Hadlocks")

    if routing_objective_entry.get(ACTIVE) == "Minimize Sum":
        routing_objective = 1
    elif routing_objective_entry.get(ACTIVE) == "Minimize Longest Path":
        routing_objective = 2
    else:
        routing_objective = 1
        print("No objective specified. Defaulting to Minimize Sum")

    # Compiles the routing c++ code if not compiled
    cpp_compiler("routing", "/lib/Switchblock_Router/src/cpp/")
    # Runs the c++ code
    lib.Switchblock_Router.src.cpp.sb_route.sb_route(matrix_width,alpha,max_iteration,routing_target,Matrix_in,Matrix_out_dir+"/"+Matrix_out_name,routing_algorithm,routing_objective)
    finish_prompt()

Matrix_bottom_frame = ttk.Frame(Matrix)
Matrix_bottom_frame.grid(row=1, column=0, sticky="n")
Matrix_bottom_frame.grid_rowconfigure(0, weight=1)
Matrix_bottom_frame.grid_columnconfigure(0, weight=1)

Matrix_run_button = Button(Matrix_bottom_frame,
                        text = "Run",
                        command = lambda: Matrix_run())
Matrix_run_button.grid(row=0, column=0)
Matrix_run_button.config(height=3, width=6)

#--------------------------
#
#       UI Setting Tab
#
#--------------------------


  
# Let the window wait for any events
window.mainloop()