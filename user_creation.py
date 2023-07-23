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
import re
import shared
from shared import INSTALL_DIRECTORY, USERNAME_MAX_LENGTH

screen = None

from passlib.hash import pbkdf2_sha256
from curses.textpad import rectangle

def open_user_creation_screen(scr, error_message):

    global screen

    screen = scr

    screen.clear()

    x = int(curses.COLS / 2 - 40)

    shared.addBannerTo(screen, 10, x)

    if error_message == 0:
        screen.addstr(22, int(curses.COLS / 2 - len("Create new user")/2), "Create new user")
    else:
        screen.addstr(22, int(curses.COLS / 2 - len(error_message)/2), error_message)

    curses.curs_set(True)

    username = input_username()
    password = input_password()

    username_test = check_username(username)
    password_test = check_password(password)

    if username_test == 0:
        if password_test == 0:
            shared.phone_number = ''
            hash = pbkdf2_sha256.hash(password)
            open(INSTALL_DIRECTORY + "/accounts/" + username,"w").write(hash + "\n")
            return True
        else:
            return open_user_creation_screen(screen, password_test)
    else:
        return open_user_creation_screen(screen, username_test)

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
    if p.is_file():
        return "Username taken"

    if len(username) > USERNAME_MAX_LENGTH:
        return "Username too long"

    # else create user database

    shared.username = username

    return 0

def check_password(password):
    if len(password) < 8: return "Password must be 8+ characters"
    if not re.search("[a-z]", password): return "Password must include lowercased characters"
    if not re.search("[A-Z]", password): return "Password must include uppercased characters"
    if not re.search("[0-9]", password): return "Password must include numbers"
    return 0
