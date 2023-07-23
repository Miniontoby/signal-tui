'''
          @@\                               @@\          @@\               @@\
          \__|                              @@ |         @@ |              \__|
 @@@@@@@\ @@\  @@@@@@\  @@@@@@@\   @@@@@@\  @@ |       @@@@@@\   @@\   @@\ @@\
@@  _____|@@ |@@  __@@\ @@  __@@\  \____@@\ @@ |@@@@@@\|_@@  _|  @@ |  @@ |@@ |
\@@@@@@\  @@ |@@ /  @@ |@@ |  @@ | @@@@@@@ |@@ |\______\ @@ |    @@ |  @@ |@@ |
 \____@@\ @@ |@@ |  @@ |@@ |  @@ |@@  __@@ |@@ |         @@ |@@\ @@ |  @@ |@@ |
@@@@@@@  |@@ |\@@@@@@@ |@@ |  @@ |\@@@@@@@ |@@ |         \@@@@  |\@@@@@@  |@@ |
\_______/ \__| \____@@ |\__|  \__| \_______|\__|          \____/  \______/ \__|
              @@\   @@ |
              \@@@@@@  |
               \______/

By Eric Karnis
This will be under gpl someday
'''
# !/usr/bin/env python3
import curses
import time
import pathlib
import shared
from shared import MAX_ATTEMPTS

screen = None

from curses.textpad import rectangle

def open_splash_screen(scr):

    #skip login
    #return True
    #delete to reenable login

    global screen

    screen = scr

    screen.clear()

    x = int(curses.COLS / 2 - 40)

    shared.addBannerTo(screen, 10, x)

    screen.addstr(23, int(curses.COLS / 2 - len("1 to login")/2), "1 to login")
    screen.addstr(25, int(curses.COLS / 2 - len("2 to add new user")/2), "2 to add new user")
    screen.addstr(27, int(curses.COLS / 2 - len("E to exit")/2), "E to exit")

    curses.curs_set(False)

    key_struck = ""

    while key_struck != "banana":
        key_struck = screen.getch()

        if key_struck == ord("1"):
            return True

        elif key_struck == ord("2"):
            return False

        elif key_struck == ord("e"):
            return None
