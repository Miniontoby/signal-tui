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
import threading
import shared
import os
import numpy
from qrcodegen import QrCode

#Signal-tui modules
import signal_cli_wrapper

from curses.textpad import Textbox, rectangle



screen = None

first_item_on_page = 0

item_highlighted = 0

settings_buffer = []

def open_settings_screen(sn):
    global screen, first_item_on_page, item_highlighted

    screen = sn

    first_item_on_page = 0

    item_highlighted = 0

    import_settings()

    draw_settings(item_highlighted)

    screen.refresh()

def import_settings():
    global settings_buffer

    settings_buffer = ["register device", "link device", "read receipts", "unidentified delivery indicators", "typing indicator", "link previews", "g", "h", "i", "j", "k", "l", "m", "n", "o"]

def erase(top_x, top_y, bottom_x, bottom_y):
    for x in range(top_x, bottom_x):
        for y in range(top_y, bottom_y):
            screen.addstr(y, x, " ")

    screen.refresh()

def draw_settings(item_highlighted):
    erase(1, 3, curses.COLS - 1, curses.LINES - 1)

    y_increment = int((curses.LINES)/10) - 1

    top_y = 5
    bottom_y = int((curses.LINES)/8)
    left_x = int(curses.COLS/4)
    right_x = int(3*curses.COLS/4)

    for setting in settings_buffer[first_item_on_page:]:

        # if selected
        if settings_buffer.index(setting) == item_highlighted:
            screen.addstr(top_y + 1, left_x + 2, setting, curses.A_STANDOUT)
        # if unselected
        else:
            screen.addstr(top_y + 1, left_x + 2, setting, curses.A_NORMAL)

        rectangle(screen, top_y, left_x, bottom_y, right_x)

        top_y += y_increment
        bottom_y += y_increment

        if first_item_on_page != 0:
            screen.addstr(3, int(curses.COLS/2) - 5, "more above")

        if bottom_y > curses.LINES - 3:
            screen.addstr(curses.LINES - 2, int(curses.COLS/2) - 5, "more below")
            break

def down():
    global item_highlighted, first_item_on_page

    if (item_highlighted % 11) == 10:
        item_highlighted += 1
        first_item_on_page += 11
        draw_settings(item_highlighted)
    elif item_highlighted != settings_buffer.index(settings_buffer[-1]):
        item_highlighted += 1
        draw_settings(item_highlighted)

def up():
    global item_highlighted, first_item_on_page

    if (item_highlighted % 11) >= 1:
        item_highlighted -= 1
        draw_settings(item_highlighted)
    elif item_highlighted != 0:
        item_highlighted -= 1
        first_item_on_page -= 11
        draw_settings(item_highlighted)

def edit_setting():
    erase(1, 3, curses.COLS - 1, curses.LINES - 1)
    screen.addstr(int(curses.LINES/6) + 1, int(curses.COLS/2 - (len(settings_buffer[item_highlighted]))/2), settings_buffer[item_highlighted])
    rectangle(screen,
              int(curses.LINES/6),
              int(curses.COLS/6),
              int(5 * (curses.LINES/6)),
              int(5 * (curses.COLS/6)))
    if settings_buffer[item_highlighted] == "register device": register_device()
    elif settings_buffer[item_highlighted] == "link device": link_device()
    elif settings_buffer[item_highlighted] == "read receipts": read_receipts()
    elif settings_buffer[item_highlighted] == "unidentified delivery indicators": unidentified_delivery_indicators()
    elif settings_buffer[item_highlighted] == "typing indicator": typing_indicator()
    elif settings_buffer[item_highlighted] == "link previews": link_previews()

def register_device():
    screen.addstr(int(curses.LINES/6) + 4, int(curses.COLS/6) + 4, "enter your phone number like this: +11234567891")
    screen.refresh()
    number_to_register = add_text_box(1,
                                    int((curses.COLS - 4)/4) - 9,
                                    int(curses.LINES/6) + 6,
                                    int(curses.COLS/6) + 5)

    if number_to_register == "":
        screen.addstr(int(curses.LINES/6) + 8, int(curses.COLS/6) + 4, "Empty input, Canceling...")
        screen.refresh()
        time.sleep(3)
        return open_settings_screen(screen)

    if not(number_to_register.startswith("+")): number_to_register = '+' + number_to_register

    nnumber_to_register = number_to_register
    try: nnumber_to_register = int(number_to_register[1::])
    except ValueError:
        screen.addstr(int(curses.LINES/6) + 8, int(curses.COLS/6) + 4, "not an int")
        screen.refresh()
        time.sleep(3)
        edit_setting()

    if type(nnumber_to_register) is int:
        if len(number_to_register) > 11: # +11234567890
            old = open(shared.INSTALL_DIRECTORY + "/accounts/" + shared.username, "r").read().split("\n")
            open(shared.INSTALL_DIRECTORY + "/accounts/" + shared.username, "w").write(old[0] + "\n" + number_to_register)
            t = threading.Thread(target=signal_cli_wrapper.register_device, args=(number_to_register,))
            t.start()
            shared.phone_number = number_to_register
        else:
            screen.addstr(int(curses.LINES/6) + 8, int(curses.COLS/6) + 4, "not 10 digits")
            screen.refresh()
            time.sleep(3)
            edit_setting()

    screen.addstr(int(curses.LINES/6) + 8, int(curses.COLS/6) + 4, "request sent")
    screen.addstr(int(curses.LINES/6) + 10, int(curses.COLS/6) + 4, "enter verification code")
    screen.refresh()

    code_to_verify = add_text_box(1,
                                    int((curses.COLS - 4)/4) - 9,
                                    int(curses.LINES/6) + 12,
                                    int(curses.COLS/6) + 5)

    if code_to_verify == "":
        screen.addstr(int(curses.LINES/6) + 8, int(curses.COLS/6) + 4, "Empty input, Canceling...")
        screen.refresh()
        time.sleep(3)
        return open_settings_screen(screen)

    t = threading.Thread(target=signal_cli_wrapper.verify_code, args=(code_to_verify,))
    t.start()
    screen.addstr(int(curses.LINES/6) + 14, int(curses.COLS/6) + 4, "your number is verified")
    screen.refresh()
    time.sleep(3)
    open_settings_screen(screen)

def draw_qr_pattern(screen, pattern):
    size = len(pattern)
    ws_y, ws_x = screen.getmaxyx()
    screen.attron(curses.color_pair(2))

    def draw_module(module_x, module_y): screen.addstr(module_y + int((ws_y - size)/2), 2*module_x + int((ws_x - 2*size)/2), "  ")

    try:
        for module_y in range(size):
            for module_x in range(size):
                if pattern[module_y][module_x]:
                    screen.attron(curses.A_REVERSE)
                    draw_module(module_x, module_y)
                    screen.attroff(curses.A_REVERSE)
                else:
                    draw_module(module_x, module_y)

        # Draw borders
        module_x = -1
        for module_y in range(-1, size): draw_module(module_x, module_y)
        module_x = size
        for module_y in range(-1, size): draw_module(module_x, module_y)
        module_y = -1
        for module_x in range(-1, size): draw_module(module_x, module_y)
        module_y = size
        for module_x in range(-1, size): draw_module(module_x, module_y)
    except:
        pass

    screen.attroff(curses.color_pair(2))

def link_device():
    # dbus-send --session --dest=org.asamk.Signal --type=method_call --print-reply /org/asamk/Signal org.asamk.Signal.link string:"My secondary client" | tr '\n' '\0' | sed 's/.*string //g' | sed 's/\"//g' | qrencode -s10 -tANSI256
    screen.addstr(int(curses.LINES/6) + 4, int(curses.COLS/6) + 4, "scan this qr-code to link this device with your phone")
    screen.refresh()

    original_accounts = signal_cli_wrapper.list_accounts()

    url = signal_cli_wrapper.link_device()
    # Returns a URI of the form "sgnl://linkdevice?uuid=…​". This can be piped to a QR encoder to create a display that can be captured by a Signal smartphone client.

    code = QrCode.encode_text(url,QrCode.Ecc.LOW)
    pattern = numpy.array(code._modules).astype('int32')

    orig = curses.pair_content(2)
    curses.init_pair(2, 0, 7)

    # show qrcode
    draw_qr_pattern(screen, pattern)

    # and wait for enter
    add_text_box(1, 1, int(curses.LINES) - 3, int(curses.COLS/6) + 5)

    # disable color
    curses.init_pair(2, orig[0], orig[1])

    # redraw top menu
    shared.draw_top_menu(screen)

    new_accounts = signal_cli_wrapper.list_accounts()

    for number in new_accounts:
        if not(number in original_accounts):
            old = open(shared.INSTALL_DIRECTORY + "/accounts/" + shared.username, "r").read().split("\n")
            open(shared.INSTALL_DIRECTORY + "/accounts/" + shared.username, "w").write(old[0] + "\n" + number)
            shared.phone_number = number
            break

    screen.refresh()
    time.sleep(3)
    open_settings_screen(screen)


def enable_disable_template_for(thing, callback):
    screen.addstr(int(curses.LINES/6) + 4, int(curses.COLS/6) + 4, "enable " + thing + "?: yes or no")
    screen.refresh()
    enable_or_disable = add_text_box(1,
                                    int((curses.COLS - 4)/4) - 9,
                                    int(curses.LINES/6) + 6,
                                    int(curses.COLS/6 + 5)).strip()
    if enable_or_disable == 'yes':
        response = callback(True)
        screen.addstr(int(curses.LINES/6) + 8, int(curses.COLS/6) + 4, thing + " is enabled" if response is True else response)
    elif enable_or_disable == 'no':
        response = callback(False)
        screen.addstr(int(curses.LINES/6) + 8, int(curses.COLS/6) + 4, thing + " is disabled" if response is True else response)
    else:
        return edit_setting()
    screen.refresh()
    time.sleep(3)
    draw_settings(item_highlighted)

def read_receipts():
    def callback(value):
        try: return signal_cli_wrapper.set_configuration(read_receipts=value)
        except Exception as e: return e.message.replace("GDBus.Error:org.asamk.Signal.Error.Failure: ", "")
    enable_disable_template_for("read receipts", callback)

def unidentified_delivery_indicators():
    def callback(value):
        try: return signal_cli_wrapper.set_configuration(unidentified_delivery_indicators=value)
        except Exception as e: return e.message.replace("GDBus.Error:org.asamk.Signal.Error.Failure: ", "")
    enable_disable_template_for("unidentified delivery indicators", callback)

def typing_indicator():
    def callback(value):
        try: return signal_cli_wrapper.set_configuration(typing_indicators=value)
        except Exception as e: return e.message.replace("GDBus.Error:org.asamk.Signal.Error.Failure: ", "")
    enable_disable_template_for("typing indicators", callback)

def link_previews():
    def callback(value):
        try: return signal_cli_wrapper.set_configuration(link_previews=value)
        except Exception as e: return e.message.replace("GDBus.Error:org.asamk.Signal.Error.Failure: ", "")
    enable_disable_template_for("link previews", callback)


def add_text_box(height, width, top_y, left_x):
    rectangle(screen,
              top_y - 1,
              left_x - 1,
              top_y + height,
              left_x + width)
    screen.refresh()
    curses.curs_set(True)
    # height, width, top_y, top_x
    editwin = curses.newwin(height, width, top_y, left_x)
    editwin.bkgdset(curses.A_STANDOUT)
    box = Textbox(editwin)
    box.stripspaces = True
    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()

    #this renders the blinking cursor invisible again
    curses.curs_set(False)

    return message


def get_phone_settings():
    properties = signal_cli_wrapper.get_configuration()
    return properties

