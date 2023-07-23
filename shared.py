#!/usr/bin/env python3
import curses
from pathlib import Path

# SHARED VARIABLES, but using function which is run ONCE, since this file is imported multiple times and else the values don't 'sync'
def init():
    global current_screen, current_conversation, contact_buffer, message_buffer, add_message, menu_items, username, phone_number
    current_screen = "login"
    current_conversation = 0
    contact_buffer = []
    message_buffer = []
    menu_items = ["Messages", "Contacts", "Guide", "Settings", "Exit"]
    username = ""
    phone_number = ""

# CONSTANTS
MAX_ATTEMPTS = 3
USERNAME_MAX_LENGTH = 20
HOTKEY_ATTR = curses.A_BOLD | curses.A_UNDERLINE
MENU_ATTR = curses.A_NORMAL
INSTALL_DIRECTORY = str(Path(__file__).parent.resolve())

def addBannerTo(screen, s, x):
    screen.addstr(s,   x, "          @@\                               @@\          @@\               @@\ ")
    screen.addstr(s+1, x, "          \__|                              @@ |         @@ |              \__|")
    screen.addstr(s+2, x, " @@@@@@@\ @@\  @@@@@@\  @@@@@@@\   @@@@@@\  @@ |       @@@@@@\   @@\   @@\ @@\ ")
    screen.addstr(s+3, x, "@@  _____|@@ |@@  __@@\ @@  __@@\  \____@@\ @@ |@@@@@@\|_@@  _|  @@ |  @@ |@@ |")
    screen.addstr(s+4, x, "\@@@@@@\  @@ |@@ /  @@ |@@ |  @@ | @@@@@@@ |@@ |\______\ @@ |    @@ |  @@ |@@ |")
    screen.addstr(s+5, x, " \____@@\ @@ |@@ |  @@ |@@ |  @@ |@@  __@@ |@@ |         @@ |@@\ @@ |  @@ |@@ |")
    screen.addstr(s+6, x, "@@@@@@@  |@@ |\@@@@@@@ |@@ |  @@ |\@@@@@@@ |@@ |         \@@@@  |\@@@@@@  |@@ |")
    screen.addstr(s+7, x, "\_______/ \__| \____@@ |\__|  \__| \_______|\__|          \____/  \______/ \__|")
    screen.addstr(s+8, x, "              @@\   @@ |")
    screen.addstr(s+9, x, "              \@@@@@@  |                                         By Eric Karnis")
    screen.addstr(s+10,x, "               \______/ ")
    return s+10


####################
##### Top Menu #####
####################

def draw_top_menu(screen):
    left = 6

    for menu_name in menu_items:
        menu_hotkey = menu_name[0]
        menu_no_hot = menu_name[1:]
        offset = int(curses.COLS/10 - len(menu_name)/2)
        screen.addstr(1, left + offset, menu_hotkey, HOTKEY_ATTR)
        screen.addstr(1, left + offset + 1, menu_no_hot, MENU_ATTR)
        left = left + int(curses.COLS/6)

    # Draw application title
    offset = int(curses.COLS - len("signal-tui"))
    screen.addstr(1, offset - 3, "signal-tui", curses.A_STANDOUT)

    #bottom line of menu area
    screen.hline(2, 2, curses.ACS_HLINE, curses.COLS - 4)

    screen.refresh()



import threading, sys
class StopThread(StopIteration):
    pass

threading.SystemExit = SystemExit, StopThread

class KillableThread(threading.Thread):
    def _bootstrap(self, stop_thread=False):
        def stop():
            nonlocal stop_thread
            print("stopping...")
            stop_thread = True
        self.stop = stop

        def tracer(*_):
            if stop_thread:
                print("stop")
                raise StopThread()
            return tracer
        sys.settrace(tracer)
        super()._bootstrap()

