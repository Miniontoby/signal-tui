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
import traceback
import os
import string
import math
import time

from curses.textpad import Textbox, rectangle
from os import system

top_message_on_page_index = 0
message_buffer = []
messages_area_bottom_y = 0
screen = None

def open_messages_panel(sn, m_area_bottom_y):
    global screen, messages_area_bottom_y
    screen = sn
    messages_area_bottom_y = m_area_bottom_y
    # Top line of text area
    screen.hline(messages_area_bottom_y - 2,
                 int(curses.COLS/4),
                 curses.ACS_HLINE, curses.COLS - 3)
    # right line of conversations panel
    screen.vline(3, int(curses.COLS/4), curses.ACS_VLINE, curses.COLS - 3)
    screen.addstr(messages_area_bottom_y - 2,
                  int(curses.COLS/4) + 1,
                  " I to enter edit mode ")
    screen.addstr(messages_area_bottom_y - 2,
                  curses.COLS - 17,
                  " Ctrl-G to send ")
    draw_messages()
    screen.refresh()


def write_message():
    curses.curs_set(True)
    # length, width, y, x
    editwin = curses.newwin(int(curses.LINES/5),
                            int(curses.COLS*(3/4)) - 2,
                            messages_area_bottom_y,
                            int(curses.COLS/4) + 1)
    editwin.bkgdset(curses.A_STANDOUT)
    box = Textbox(editwin)
    box.stripspaces = True
    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()

    if message:
        # if send_message(recipient, input):
        add_message("s", message)

    curses.curs_set(False)
    screen.refresh()


def add_message(originator, message):
    # TODO: write the message to a database here
    message_buffer.append([originator, message])
    draw_messages()

def erase(top_x,top_y, bottom_x, bottom_y):
    for x in range(top_x, bottom_x):
            for y in range(top_y, bottom_y):
                    screen.addstr(y, x, " ")

def import_messages():
    # TODO add a database
    global message_buffer
    message_buffer = [["s", "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50."],["r","what's up?"],["s","hey"],["r", "1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13, 14, 15, 16, 17, 18, 19, 20, 21, 22, 23, 24, 25, 26, 27, 28, 29, 30, 31, 32, 33, 34, 35, 36, 37, 38, 39,40, 41, 42, 43, 44, 45, 46, 47, 48, 49, 50."],["s","hey"],["r","what's up?"],["s","u nerd"],["r","jdflkjdlfkjsdlfjbdslfhjblsdjhfbdlsjhflsadfhlsdjfhlkjshlkfsd?"],["s","hey"],["r","pls respond"]]

def draw_messages():

    # clear the messages area
    erase(int(curses.COLS/4) + 1, 3, curses.COLS - 2, messages_area_bottom_y - 2)

    message_line_len = int(curses.COLS*(1/2) - 5)

    message_bottom_y = messages_area_bottom_y - 3

    for message in reversed(message_buffer):

        # Check if the message was sent or received and put the message on the left 
        # or right respectively
        if message[0] == "s":
            message_box_left_x = int(curses.COLS*(1/2))
            message_box_right_x = curses.COLS - 3
        else:
            message_box_left_x = int(curses.COLS*(1/4) + 2)
            message_box_right_x = int(curses.COLS*(3/4) - 1)

        # Write the message line by line
        message_line_num = int(math.ceil(len(message[1])/message_line_len))

        # If the message does not fit on the page, stop drawing messages
        # and print more above at the top
        if (message_bottom_y - 3 - message_line_num) < 3:
            top_message_on_page_index = message_buffer.index(message) - 1
            screen.addstr(5, int(5*curses.COLS/8) - 5, "more above")
            break

        for x in range(0, message_line_num):
            start_line_index = x * message_line_len
            end_line_index = (x + 1) * message_line_len - 1
            line = message[1][start_line_index: end_line_index]
            try:
                screen.addstr(message_bottom_y - 2 - message_line_num + x + 1,
                              message_box_left_x + 1,
                              line, curses.A_STANDOUT)
            except curses.error:
                pass

        rectangle(screen,
                  message_bottom_y - 2 - message_line_num,
                  message_box_left_x,
                  message_bottom_y,
                  message_box_right_x)

        message_bottom_y = message_bottom_y - 3 - message_line_num



        screen.border(0)
        screen.refresh()