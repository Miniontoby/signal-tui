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
from shared import INSTALL_DIRECTORY, MAX_ATTEMPTS

screen = None

from passlib.hash import pbkdf2_sha256
from curses.textpad import rectangle

def open_login_screen(scr, attempts):

    #skip login
    #return True
    #delete to reenable login

    global screen, current_username, phone_number

    screen = scr

    screen.clear()

    x = int(curses.COLS / 2 - 40)

    shared.addBannerTo(screen, 10, x)

    if attempts != 0 and attempts < MAX_ATTEMPTS:
        screen.addstr(22, int(curses.COLS / 2 - 13), "Wrong Password or Username")
    elif attempts >= MAX_ATTEMPTS:
        screen.addstr(25, int(curses.COLS / 2 - 7), "Too Many Attempts")
        screen.refresh()
        time.sleep(5)
        quit("\033[1m" + "Too Many Attempts" + "\033[1m")

    curses.curs_set(True)

    username = input_username()
    password = input_password()

    if check_username(username):
        content = open(INSTALL_DIRECTORY + "/accounts/" + username).read().split("\n") # Password\nphonenumber
        if check_password(password, content[0]):
            shared.username = username
            shared.phone_number = content[1] or ""
            return True
        else:
            attempts += 1
            return open_login_screen(screen, attempts)
    else:
        attempts += 1
        return open_login_screen(screen, attempts)

def input_username():

    screen.addstr(24, int(curses.COLS / 2 - 7), "Enter Username")
    rectangle(screen, 25, int(curses.COLS / 2 - 31), 27, int(curses.COLS / 2 + 31))
    screen.refresh()

    # Get then clean up username
    username = screen.getstr(26, int(curses.COLS / 2 - 30), 60)
    username = str(username)[2:-1]

    return username

def input_password():

    screen.addstr(24, int(curses.COLS / 2 - 7), "Enter Password")
    rectangle(screen, 25, int(curses.COLS / 2 - 31), 27, int(curses.COLS / 2 + 31))
    screen.refresh()

    # Get then clean up password
    password = screen.getstr(26, int(curses.COLS / 2 - 30), 60)
    password = str(password)[2:-1]

    return password


def check_username(username):
    # signal-tui's directory
    user_database = INSTALL_DIRECTORY + "/accounts/" + username
    p = pathlib.Path(user_database)

    # user exists if database exists
    return p.is_file()

def check_password(password, passwordhash):
    return pbkdf2_sha256.verify(password, passwordhash)
