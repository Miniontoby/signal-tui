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
import shared
from signal_cli_wrapper import get_contacts, update_contact

from curses.textpad import Textbox, rectangle

screen = None

contact_highlighted = 0

first_contact_on_page = 0

def import_contacts(sn):
    # TODO add a database
    global screen
    screen = sn
    #shared.contact_buffer = [[4168870649,"Eric's Phone"], [1, "Manuela Bartolomeo"], [2, "Ace Falkner"], [3, "Bryan Hayes"], [4, "Luke Doliszny"], [5, "Noah Stranger"], [6, "Eliot Old"],[7,"John Smith"], [8, "Manuel Bart"], [9, "Aces Falk"], [10, "Bry Hay"], [11, "Luk Dol"], [12, "No Strange"], [13, "Felix Beiderman"], [14, "Linus T"], [15, "Richard S"], [16, "Peter Parker"],[17,"Tales Ferreira"], [111, "Manuela Bartolomeo"], [211, "Ace Falkner"], [311, "Bryan Hayes"], [411, "Luke Doliszny"], [511, "Noah Stranger"], [611, "Eliot Old"],[711,"John Smith"], [811, "Manuel Bart"], [911, "Aces Falk"], [101, "Bry Hay"], [111, "Luk Dol"], [112, "No Strange"], [113, "Felix Beiderman"], [114, "Linus T"], [115, "Richard S"], [116, "Peter Parker"]]
    shared.contact_buffer = get_contacts()
    return shared.contact_buffer

def open_contacts_screen(sn):
    global screen, first_contact_on_page

    screen = sn

    first_contact_on_page = 0

    draw_contacts(0)

    screen.refresh()

def erase(top_x, top_y, bottom_x, bottom_y):
    for x in range(top_x, bottom_x):
        for y in range(top_y, bottom_y):
            screen.addstr(y, x, " ")

    screen.refresh()


def draw_contacts(name_highlighted):
    erase(1, 3, curses.COLS - 1, curses.LINES - 1)

    x_increment = int((curses.COLS - 4)/4)
    y_increment = int((curses.LINES - 4)/4)

    top_y = 5
    bottom_y = y_increment
    left_x = 4
    right_x = x_increment


    screen.addstr(3, 3, "A to add")
    screen.addstr(3, curses.COLS - len("I to edit") - 3, "I to edit")

    for contact in shared.contact_buffer[first_contact_on_page:]:

        # if selected
        if shared.contact_buffer.index(contact) == name_highlighted:
            screen.addstr(top_y + 2,
                          left_x + 2,
                          contact[1][:right_x - left_x - 2],
                          curses.A_STANDOUT)
            screen.addstr(top_y + 3, left_x + 2, str(contact[0]), curses.A_STANDOUT)

        # if unselected
        else:
            screen.addstr(top_y + 2, left_x + 2, contact[1][:right_x - left_x - 2], curses.A_NORMAL)
            screen.addstr(top_y + 3, left_x + 2, str(contact[0]), curses.A_NORMAL)

        rectangle(screen, top_y, left_x, bottom_y, right_x)


        left_x += x_increment
        right_x += x_increment

        # if end of row start next row
        if right_x > curses.COLS - 3:
            top_y += y_increment
            bottom_y += y_increment
            left_x = 4
            right_x = x_increment

        if first_contact_on_page != 0:
            screen.addstr(3, int(curses.COLS/2) - 5, "more above")

        #if end of page stop
        if bottom_y > curses.LINES - 3:
            screen.addstr(curses.LINES - 2, int(curses.COLS/2) - 5, "more below")
            break

# TODO: these only works properly for a 4x4 grid of contacts

def left():
    global contact_highlighted, first_contact_on_page

    if (contact_highlighted % 16) != 0:
        contact_highlighted -= 1
        draw_contacts(contact_highlighted)
    elif contact_highlighted != 0:
        contact_highlighted -= 1
        first_contact_on_page -= 16
        draw_contacts(contact_highlighted)

def down():
    global contact_highlighted, first_contact_on_page

    contact_buffer = shared.contact_buffer

    if (contact_highlighted + 3) < contact_buffer.index(contact_buffer[-1]):

        if (((contact_highlighted + 1) % 16) <= 12 and ((contact_highlighted + 1) % 16) != 0) or contact_highlighted == 0:
            contact_highlighted += 4
            draw_contacts(contact_highlighted)
        else:
            contact_highlighted += 4
            first_contact_on_page += 16
            draw_contacts(contact_highlighted)

def up():
    global contact_highlighted, first_contact_on_page

    if (contact_highlighted % 16) >= 4:
        contact_highlighted -= 4
        draw_contacts(contact_highlighted)
    elif contact_highlighted >= 4:
        contact_highlighted -= 4
        first_contact_on_page -= 16
        draw_contacts(contact_highlighted)

def right():
    global contact_highlighted, first_contact_on_page

    contact_buffer = shared.contact_buffer

    if contact_highlighted != contact_buffer.index(contact_buffer[-1]):

        if ((contact_highlighted + 1) % 16) != 0:
            contact_highlighted += 1
            draw_contacts(contact_highlighted)
        else:
            contact_highlighted += 1
            first_contact_on_page += 16
            draw_contacts(contact_highlighted)

def edit_contact():

    xamount = 4
    yamount = 4

    entry = contact_highlighted % (xamount * yamount)

    #hardcoded 4x4 grid
    #TODO: make this more flexible

    for r in range(0, xamount+1): # not inclusive
        if xamount * r <= entry < xamount * (r + 1):
            top_y = 5 + r * int((curses.LINES - yamount)/yamount)
            bottom_y = (r + 1) * int((curses.LINES - yamount)/yamount)

    for r in range(0, yamount):
        if (entry - r) % xamount == 0:
            left_x = 4 + r * int((curses.COLS - xamount)/xamount)
            right_x = (r + 1) * int((curses.COLS - xamount)/xamount)

    erase(left_x + 1, top_y + 1, right_x, bottom_y)

    screen.addstr(3, 3, "Ctrl-G to commit")
    screen.addstr(3, curses.COLS - len("I to edit") - 3, "         ")

    screen.addstr(top_y + 2, left_x + 2, "Name")
    screen.addstr(top_y + 6, left_x + 2, "Number")
    rectangle(screen, top_y + 3, left_x + 2, top_y + 5, right_x - 2)
    rectangle(screen, top_y + 7, left_x + 2, top_y + 9, right_x - 2)

    screen.refresh()

    new_name = add_text_box(1, int((curses.COLS - 4)/4) - 9, top_y + 4, left_x + 3)
    new_number = add_text_box(1, int((curses.COLS - 4)/4) - 9, top_y + 8, left_x + 3)

    addzero = str(new_number).startswith("0")
    try: new_number = int(new_number)
    except ValueError:
        erase(left_x + 1, top_y + 1, right_x, bottom_y)
        screen.addstr(top_y + 2, left_x + 2, "number not an int")
        screen.refresh()
        time.sleep(3)
        draw_contacts(shared.contact_highlighted)

    if type(new_number) is int:
        if len(str(new_number)) == 10 if not(addzero) else 9:
            update_contact("number", shared.contact_buffer[contact_highlighted], new_number)
        else:
            erase(left_x + 1, top_y + 1, right_x, bottom_y)
            screen.addstr(top_y + 2, left_x + 2, "number not 10 digits")
            screen.refresh()
            time.sleep(3)
            draw_contacts(contact_highlighted)
    if new_name:
        update_contact("name", shared.contact_buffer[contact_highlighted], new_name)
    else:
        erase(left_x + 1, top_y + 1, right_x, bottom_y)
        screen.addstr(top_y + 2, left_x + 2, "enter a name")
        screen.refresh()
        time.sleep(3)
        draw_contacts(contact_highlighted)

    draw_contacts(contact_highlighted)

def add_contact():
    erase(1, 3, curses.COLS - 1, curses.LINES - 1)

    rectangle(screen, int(curses.LINES/5), int(curses.COLS/4), int(3 * curses.LINES/4), int(3 * curses.COLS/4))

    screen.addstr(int(curses.LINES/5) + 3, int(curses.COLS/4) + 3, "Name:")
    screen.addstr(int(curses.LINES/5) + 8, int(curses.COLS/4) + 3, "Number:")

    screen.addstr(3, 3, "Ctrl-G to commit")
    screen.addstr(3, curses.COLS - len("I to edit") - 3, "         ")

    rectangle(screen, 
              int(curses.LINES/5) + 2,
              int(curses.COLS/3 + 3), 
              int(curses.LINES/5) + 4,
              int(3 * curses.COLS/4) - 3)
    rectangle(screen, 
              int(curses.LINES/5) + 7,
              int(curses.COLS/3 + 3), 
              int(curses.LINES/5) + 9,
              int(3 * curses.COLS/4) - 3)

    screen.refresh()

    new_name = add_text_box(1, 
                            int((curses.COLS - 4)/4) - 9, 
                            int(curses.LINES/5) + 3, 
                            int(curses.COLS/3 + 4))
    new_number = add_text_box(1, 
                            int((curses.COLS - 4)/4) - 9, 
                            int(curses.LINES/5) + 8, 
                            int(curses.COLS/3 + 4))

    # TODO: write name and number to database
    if new_name:
        addzero = new_number.startswith("0")
        try: new_number = int(new_number)
        except ValueError:
            erase(1, 3, curses.COLS - 1, curses.LINES - 1)
            rectangle(screen, int(curses.LINES/5), int(curses.COLS/4), int(3 * curses.LINES/4), int(3 * curses.COLS/4))        
            screen.addstr(int(curses.LINES/5) + 3, 
                          int(curses.COLS/4) + 3, 
                          "number not an int")
            screen.refresh()
            time.sleep(3)
            add_contact()

        if type(new_number) is int:
            if len(str(new_number)) == 10 if not(addzero) else 9:
                new_contact = [new_number,new_name]
                shared.contact_buffer.append(new_contact)
            else:
                erase(1, 3, curses.COLS - 1, curses.LINES - 1)
                rectangle(screen, int(curses.LINES/5), int(curses.COLS/4), int(3 * curses.LINES/4), int(3 * curses.COLS/4))        
                screen.addstr(int(curses.LINES/5) + 3, 
                              int(curses.COLS/4) + 3, 
                             "number not 10 digits")
                screen.refresh()
                time.sleep(3)
                add_contact()

    else:
        erase(1, 3, curses.COLS - 1, curses.LINES - 1)
        rectangle(screen, int(curses.LINES/5), int(curses.COLS/4), int(3 * curses.LINES/4), int(3 * curses.COLS/4))        
        screen.addstr(int(curses.LINES/5) + 3, 
                      int(curses.COLS/4) + 3, 
                     "enter a name")
        screen.refresh()
        time.sleep(3)
        add_contact()

    draw_contacts(contact_highlighted)

def add_text_box(height, width, top_y, left_x):

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
