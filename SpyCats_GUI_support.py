#! /usr/bin/env python
#  -*- coding: utf-8 -*-
#
# Support module generated by PAGE version 7.5
#  in conjunction with Tcl version 8.6
#    Nov 18, 2022 12:03:57 AM AEST  platform: Windows NT

import sys
import tkinter as tk
import tkinter.ttk as ttk
from tkinter.constants import *

import SpyCats_GUI

def main(*args):
    '''Main entry point for the application.'''
    global root
    root = tk.Tk()
    root.protocol( 'WM_DELETE_WINDOW' , root.destroy)
    # Creates a toplevel widget.
    global _top1, _w1
    _top1 = root
    _w1 = SpyCats_GUI.Toplevel1(_top1)
    root.mainloop()

if __name__ == '__main__':
    SpyCats_GUI.start_up()




