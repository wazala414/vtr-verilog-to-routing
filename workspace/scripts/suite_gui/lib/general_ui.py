#!/usr/bin/python3
# import all components
# from the tkinter library
from tkinter import *
import os
import subprocess as sp
import tkinter
from PIL import ImageTk, Image
import webbrowser
  
import lib.VTR_Tab
import lib.Routing_Tab
import lib.Programming_Tab
import ZeroAMP_Suite

# import filedialog module
from tkinter import filedialog

from tkinter import ttk

#------------------------------
#
#      General Functions
#
#------------------------------

def helper():
    print("test")

def set_text(entry,text):
    entry.delete(0,END)
    entry.insert(0,text)
    return