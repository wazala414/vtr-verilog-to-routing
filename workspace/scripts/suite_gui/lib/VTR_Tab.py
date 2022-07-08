#!/usr/bin/python3
# import all components
# from the tkinter library
from tkinter import *
import os
import subprocess as sp
import tkinter
from PIL import ImageTk, Image
import webbrowser

import lib.Routing_Tab
import lib.Programming_Tab
import lib.general_ui
import ZeroAMP_Suite
  
# import filedialog module
from tkinter import filedialog

from tkinter import ttk


#--------------------------
#
#       VTR Tab
#
#--------------------------

# TODO: Make sub tab for single file and batch process

def VTR_tab_init (VTR_tab):

    # Column Setting
    VTR_tab.grid_columnconfigure(0, minsize=50)
    VTR_tab.grid_columnconfigure(2, minsize=40)
    VTR_tab.grid_columnconfigure(4, minsize=40)
    VTR_tab.grid_rowconfigure(1, minsize=40)
    VTR_tab.grid_rowconfigure(3, minsize=40)
    VTR_tab.grid_rowconfigure(5, minsize=40)
    VTR_tab.grid_rowconfigure(7, minsize=50)
    VTR_tab.grid_rowconfigure(8, minsize=20)

    # VTR Architecture Setup
    ttk.Label(VTR_tab, text="Architecture").grid(row=0, column=1)
    arch_button = Button(VTR_tab,
                            text = "Browse",
                            command = lambda: browseArchitecture(arch_file,arch_entry))
    arch_entry = ttk.Entry(VTR_tab, width="10")
    arch_entry.grid(row=0, column=3)
    arch_button.grid(column = 5, row = 0)

    # VTR Circuit Setup
    ttk.Label(VTR_tab, text="Circuit").grid(row=1, column=1)
    circuit_button = Button(VTR_tab,
                            text = "Browse",
                            command = lambda: browseCircuit(circuit_file,circuit_entry))
    circuit_entry = ttk.Entry(VTR_tab, width="10")
    circuit_entry.grid(row=1, column=3)
    circuit_button.grid(column = 5, row = 1)

    # VTR Output Directory
    ttk.Label(VTR_tab, text="Output Directory").grid(row=2, column=1)
    out_dir_button = Button(VTR_tab,
                            text = "Browse",
                            command = lambda: browseOutDir(out_dir,out_dir_entry))
    out_dir_entry = ttk.Entry(VTR_tab, width="10")
    out_dir_entry.grid(row=2, column=3)
    out_dir_button.grid(column = 5, row = 2)

    # VTR Width
    ttk.Label(VTR_tab, text="Routing Width").grid(row=3, column=1)
    width_entry = ttk.Entry(VTR_tab, width="10")
    width_entry.grid(row=3, column=3)

    # VTR Tickboxes
    analysis_tick = IntVar()
    analysis_entry = Checkbutton(VTR_tab, text='Analysis',variable=analysis_tick, onvalue=1, offvalue=0)
    analysis_entry.grid(row=4, column=1)

    # VTR Arguments Setup
    ttk.Label(VTR_tab, text="Arguments").grid(row=5, column=1)
    args_entry = ttk.Entry(VTR_tab, width="10")
    args_entry.grid(row=5, column=3)

    # Run VTR
    def VTR_run():

        # Field Polling
        circuit_file = circuit_entry.get()
        arch_file = arch_entry.get()
        out_dir = out_dir_entry.get()
        routing_width = width_entry.get()
        args_pass = args_entry.get()

        status = sp.call("cd " 
        + VTR_path 
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

    def VTR_display():
        
        # Field Polling
        circuit_file = circuit_entry.get()
        arch_file = arch_entry.get()
        out_dir = out_dir_entry.get()
        routing_width = width_entry.get()
        #analysis_tick = analysis_entry.get()
        args_pass = args_entry.get()

        if analysis_tick.get():
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

    #$VTR_ROOT/vpr/vpr     $arch     $circuit --circuit_file $circuit.pre-vpr.blif    --route_chan_width $width  --disp on --analysis

    VTR_run_button = Button(VTR_tab,
                            text = "Run",
                            command = lambda: VTR_run())
    VTR_run_button.grid(columns=6, row=7, sticky="SE")
    VTR_display_button = Button(VTR_tab,
                            text = "Display",
                            command = lambda: VTR_display())
    VTR_display_button.grid(columns=6, row=8, sticky="SE")




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