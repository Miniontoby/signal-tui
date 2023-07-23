#!/usr/bin/env python3
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
import curses
import traceback
import pathlib
import os
import re

#Signal-tui modules
import shared
shared.init()
import splash
import login
import user_creation
import messages
import contacts
import settings
import signal_cli_wrapper

# Define additional constants
EXIT = 0
CONTINUE = 1
INSTALL_DIRECTORY = shared.INSTALL_DIRECTORY

# Give screen module scope
screen = None

# fills a box with the given coordinates with spaces
def erase(top_x, top_y, bottom_x, bottom_y):
    for x in range(top_x, bottom_x):
        for y in range(top_y, bottom_y):
            screen.addstr(y, x, " ")

    screen.refresh()



##############
#### Main ####
##############

def main(stdscr):

    global screen
    screen = stdscr
    screen.box()
    screen.refresh()

    # Check if any users exist by looking for their databases
    # if none exist, open user creation screen
    filenames = next(os.walk(INSTALL_DIRECTORY + "/accounts/"))[2]
    p = re.compile("^[^.]*$") # just check for files without extension
    found = False

    for file in filenames:
        search_object = p.search(str(file))

        if search_object:
           found = True
           break

    # if code returns None then E had been pressed
    code = splash.open_splash_screen(screen)

    # Start the program
    if found and code is True:
        if login.open_login_screen(screen, 0):
            screen.clear()
            shared.draw_top_menu(screen)
            screen.border(0)
            if shared.phone_number == "": # Need to set phonenumber first
                shared.current_screen = "settings"
                settings.open_settings_screen(screen)
            else:
                shared.contact_buffer = contacts.import_contacts(screen)
                shared.message_buffer = messages.import_messages()
                shared.current_screen = "messages"
                messages.open_messages_screen(screen, 0, shared.contact_buffer)
            curses.curs_set(False)

    elif code is None:
        return # exit

    else:
        user_creation.open_user_creation_screen(screen, 0)
        screen.clear()
        shared.draw_top_menu(screen)
        screen.border(0)
        #shared.contact_buffer = contacts.import_contacts(screen)
        #shared.message_buffer = messages.import_messages()
        #shared.current_screen = "messages"
        #messages.open_messages_screen(screen, 0, shared.contact_buffer)
        shared.current_screen = "settings"
        settings.open_settings_screen(screen)
        curses.curs_set(False)

    if not(shared.phone_number == ""):
        # Start signal message listener
        signalthread = shared.KillableThread(target=signal_cli_wrapper.signalMessageListener, name='MessageListener for {}'.format(shared.phone_number))
        signalthread.daemon = True
        signalthread.start()

    # This loop controls the hotkeys. Pressing e will exit the loop and the program
    key_struck = ""
    while key_struck != ord("e"):
        key_struck = screen.getch()

        # These hotkeys should be available from every screen
        if key_struck == ord("m"):
            if not(shared.phone_number == ""):
                erase(1, 3, curses.COLS - 1, curses.LINES - 1)
                shared.current_screen = "messages"
                messages.open_messages_screen(screen, shared.current_conversation, shared.contact_buffer)

        elif key_struck == ord("c"):
            if not(shared.phone_number == ""):
                erase(1, 3, curses.COLS - 1, curses.LINES - 1)
                shared.current_screen = "contacts"
                contacts.open_contacts_screen(screen)

        elif key_struck == ord("s"):
            if not(shared.phone_number == ""):
                erase(1, 3, curses.COLS - 1, curses.LINES - 1)
                shared.current_screen = "settings"
                settings.open_settings_screen(screen)

        # the hotkeys below are screen specific
        if shared.current_screen == "messages":
            if key_struck == ord("i"):
                messages.write_message(shared.current_conversation)

            elif key_struck == ord("u"):
                messages.edit_message(shared.current_conversation)

            elif key_struck == curses.KEY_RIGHT:
                if shared.current_conversation != len(shared.contact_buffer) - 1:
                    shared.current_conversation += 1
                else:
                    shared.current_conversation = 0
                messages.open_messages_screen(screen, shared.current_conversation, shared.contact_buffer)

            elif key_struck == curses.KEY_DOWN:
                messages.page_down(shared.current_conversation)

            elif key_struck == curses.KEY_UP:
                messages.page_up(shared.current_conversation)

            elif key_struck == curses.KEY_LEFT:
                if shared.current_conversation != 0:
                    shared.current_conversation -= 1
                else:
                    shared.current_conversation = len(shared.contact_buffer) - 1
                messages.open_messages_screen(screen, shared.current_conversation, shared.contact_buffer)

        elif shared.current_screen == "contacts":
            if key_struck == ord("i"):
                contacts.edit_contact()

            elif key_struck == ord("a"):
                contacts.add_contact()

            elif key_struck == curses.KEY_LEFT:
                contacts.left()

            elif key_struck == curses.KEY_DOWN:
                contacts.down()

            elif key_struck == curses.KEY_UP:
                contacts.up()

            elif key_struck == curses.KEY_RIGHT:
                contacts.right()

        elif shared.current_screen == "settings":
            if key_struck == curses.KEY_ENTER or key_struck == 10 or key_struck == 13:
                settings.edit_setting()

            elif key_struck == ord("h"): # idk why this is here
                erase(1, 3, curses.COLS - 1, curses.LINES - 1)
                settings.open_settings_screen(screen)

            elif key_struck == curses.KEY_DOWN:
                settings.down()

            elif key_struck == curses.KEY_UP:
                settings.up()


if __name__ == '__main__':
    try:
        # Initialize curses
        stdscr = curses.initscr()
        curses.start_color()
        curses.use_default_colors()
        # Turn off echoing of keys, and enter cbreak mode,
        # where no buffering is performed on keyboard input
        curses.noecho()
        curses.cbreak()

        # In keypad mode, escape sequences for special keys
        # (like the cursor keys) will be interpreted and
        # a special value like curses.KEY_LEFT will be returned
        stdscr.keypad(1)
        # Enter the main loop
        main(stdscr)
        # Set everything back to normal
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        # Terminate curses
        curses.endwin()


    # If something goes wrong, restore terminal and report exception
    except:
        stdscr.keypad(0)
        curses.echo()
        curses.nocbreak()
        curses.endwin()
        # Print the exception
        traceback.print_exc()
