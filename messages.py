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
import math
import shared
from curses.textpad import Textbox, rectangle

#Signal-tui modules
import signal_cli_wrapper

screen = None

page_index = [0]
current_page = 0
messages_area_bottom_y = 0

def open_messages_screen(sn, current_conversation, contact_buffer):
    global screen, messages_area_bottom_y, current_page

    screen = sn
    messages_area_bottom_y = int(curses.LINES*(4/5))
    current_page = 0

    draw_conversations_list(current_conversation, contact_buffer)

    # Top line of text area
    screen.hline(messages_area_bottom_y - 2,
                 int(curses.COLS/4),
                 curses.ACS_HLINE, curses.COLS - 3)
    # right line of conversations panel
    screen.vline(3, int(curses.COLS/4), curses.ACS_VLINE, curses.COLS - 3)
    screen.addstr(messages_area_bottom_y - 2,
                  int(curses.COLS/4) + 1,
                  " I to write ")
    screen.addstr(messages_area_bottom_y - 2,
                  int(curses.COLS/4) + 1 + len(" I to write ") + 4,
                  " U to update ")
    screen.addstr(messages_area_bottom_y - 2,
                  curses.COLS - len(" Ctrl-G to send ") - 1,
                  " Ctrl-G to send ")

    refresh_page_index(current_conversation)
    draw_messages(current_conversation)
    screen.refresh()



def write_message(current_conversation):
    curses.curs_set(True)
    # height, width, top_y, top_x
    editwin = curses.newwin(int(curses.LINES/5),
                            int(curses.COLS*(3/4)) - 2,
                            messages_area_bottom_y,
                            int(curses.COLS/4) + 1)
    editwin.bkgdset(curses.A_STANDOUT)
    box = Textbox(editwin)
    box.stripspaces = True

    recipient = shared.message_buffer[current_conversation][0][0]
    signal_cli_wrapper.send_typing(recipient, False)

    # Let the user edit until Ctrl-G is struck.
    box.edit()

    # Get resulting contents
    message = box.gather()

    signal_cli_wrapper.send_typing(recipient, True) # Stop = True

    if message:
        import_messages()
        # if send_message(recipient, input):
        timestamp = signal_cli_wrapper.send_message(recipient, message)
        add_message(current_conversation, "s", message, timestamp)

    curses.curs_set(False)
    screen.refresh()

def edit_message(current_conversation):
    lastmessage = []
    for i in shared.message_buffer[current_conversation][1][::-1]:
        if i[0] == 's': lastmessage = i

    curses.curs_set(True)
    # height, width, top_y, top_x
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
    recipient = shared.message_buffer[current_conversation][0][0]

    if message:
        import_messages()
        # if send_message(recipient, input):
        timestamp = signal_cli_wrapper.edit_message(recipient, lastmessage, message)
        add_message(current_conversation, "s", message, timestamp)

    curses.curs_set(False)
    screen.refresh()

def add_message(current_conversation, originator, message, timestamp, new=False):
    shared.message_buffer[current_conversation][1].append([originator, message, timestamp, new])

    if shared.current_conversation == current_conversation:
        refresh_page_index(current_conversation)
        draw_messages(current_conversation)

shared.add_message = add_message

def erase(top_x, top_y, bottom_x, bottom_y):
    for x in range(top_x, bottom_x):
        for y in range(top_y, bottom_y):
            screen.addstr(y, x, " ")

    screen.refresh()

def import_messages():
    shared.message_buffer = signal_cli_wrapper.get_messages()
    if len(shared.message_buffer) == 0:
        shared.message_buffer = [
        [[4168870649,"Eric's Phone"],[["s", "Sed vitae magna non eros luctus viverra.", 1000000],["r","Vivamus ullamcorper gravida augue, ut fermentum enim aliquet sit amet.", 1000000],["s","Fusce libero ipsum, feugiat nec libero at, placerat rhoncus dui.", 1000000],["r", "Etiam elit erat, luctus accumsan felis ut, finibus sollicitudin metus.bus."],["r","Vivamus ornare commodo tellus in vestibulum.", 1000000],["s","Interdum et malesuada fames ac ante ipsum primis in faucibus. Praesent et sollicitudin massa.", 1000000],["r","jdflkjdlfkjsdlfjbdslfhjblsdjhfbdlsjhflsadfhlsdjfhlkjshlkfsd?", 1000000],["s"," Lorem ipsum dolor sit amet, consectetur adipiscing elit. Nullam imperdiet, felis a euismod rhoncus, dui nibh lobortis leo, auctor fringilla eros nisl nec eros.", 1000000],["r","Curabitur ut blandit diam, eget rhoncus arcu.", 1000000],["s", "Maecenas feugiat dolor nibh, nec pharetra leo auctor ut. Duis sagittis maximus eros, vitae aliquam elit luctus a. Ut sed orci eget arcu efficitur tempor. Aenean pulvinar fermentum leo et suscipit. Duis semper eros sit amet porta interdum. ", 1000000],["r","jdflkjdlfkjsdlfjbdslfhjblsdjhfbdlsjhflsadfhlsdjfhlkjshlkfsd?", 1000000],["s","hey", 1000000],["r","pls respond", 1000000]]],
        ]
    return shared.message_buffer


def draw_conversations_list(name_highlighted, contact_buffer):
    y = 4
    for contact in contact_buffer:
        if contact_buffer.index(contact) == name_highlighted:
            screen.addstr(y, 2, contact[1], curses.A_STANDOUT)

        else: screen.addstr(y, 2, contact[1], curses.A_NORMAL)

        y += 2
        if y > curses.LINES - 2:
            break

    screen.vline(3, int(curses.COLS/4), curses.ACS_VLINE, curses.COLS - 3)
    screen.refresh()


# This draws the messages of the conversation given as an argument to the message screen
def draw_messages(current_conversation):

    # clear the messages area, ie the space to the left of the contacts panel
    # and above the message writing panel
    erase(int(curses.COLS/4) + 1, 3, curses.COLS - 2, messages_area_bottom_y - 2)

    line_len = int(curses.COLS*(1/2) - 5)

    reversed_message = shared.message_buffer[current_conversation][1][::-1]

    message_bottom_y = messages_area_bottom_y - 3

    if current_page > 0:
        screen.addstr(messages_area_bottom_y - 3, int(5*curses.COLS/8) - 5, "more below")
        message_bottom_y -= 1

    receive_msgs = []
    for message in reversed_message[page_index[current_page]:]:
        if message[0] == 'r' and len(message) == 4 and message[3]:
            receive_msgs.append(int(message[2]))
            # [3] should be new (True is new)
            message[3] = False # Set to seen
    if len(receive_msgs) > 0: signal_cli_wrapper.send_read_message(shared.contact_buffer[current_conversation][0], receive_msgs)

    for message in reversed_message[page_index[current_page]:]:

        # Check if the message was sent or received and put the message on the left
        # or right respectively
        if message[0] == "s":
            left_x = int(curses.COLS*(1/2))
            right_x = curses.COLS - 3
        elif message[0] == "r":
            left_x = int(curses.COLS*(1/4) + 2)
            right_x = int(curses.COLS*(3/4) - 1)
        else:
            quit("Incorrect Sent/Received code in buffer")

        start_line_index = line_num = 0
        my_message = str(message[1])
        while start_line_index < len(my_message):
            end_line_index = start_line_index + line_len
            line = my_message[start_line_index: end_line_index]
            if not("\n" in line) and len(line) == line_len:
                my_message = my_message[:end_line_index] + "\n" + my_message[end_line_index:]
                start_line_index += line_len + 1 # \n == 1
            elif "\n" in line: start_line_index += line.index("\n") + 1
            else: start_line_index += line_len
            line_num += 1

        line_num -= 1 # length = -1, since we start a 0

        # If the message does not fit on the page, stop drawing messages
        # and print "more above" at the top
        if (message_bottom_y - 3 - line_num) < 3:
            global top_message
            top_message = reversed_message.index(message)
            screen.addstr(3, int(5*curses.COLS/8) - 5, "more above")
            break

        for x, line in enumerate(my_message.split("\n")):
            screen.addstr(message_bottom_y - 2 - line_num + x + 1,
                          left_x + 1,
                          line, curses.A_STANDOUT)

        rectangle(screen,
                  message_bottom_y - 2 - line_num,
                  left_x,
                  message_bottom_y,
                  right_x)

        message_bottom_y = message_bottom_y - 3 - line_num

    screen.border(0)
    screen.refresh()

def page_down(current_conversation):
    global current_page
    if current_page != 0:
        current_page -= 1
        draw_messages(current_conversation)

def page_up(current_conversation):
    global current_page
    if current_page != page_index.index(page_index[-1]):
        current_page += 1
        draw_messages(current_conversation)


def refresh_page_index(current_conversation):
    global page_index

    page_index = [0]

    line_len = int(curses.COLS*(1/2) - 5)

    message_bottom_y = messages_area_bottom_y - 3

    try:
        #import_messages()
        reversed_message = shared.message_buffer[current_conversation][1][::-1]
    except IndexError:
        quit("\033[1m" + "Not enough entries in message_buffer for all of the contacts" + "\033[1m")

    for message in reversed_message:

        # Calculate the number of lines in the message
        line_num = int(math.ceil(len(message[1])/line_len))

        if (message_bottom_y - 3 - line_num) < 3:
            # append the index of the bottom message of the new page by adding 1 to
            # the index of the top message of the last page
            page_index.append(reversed_message.index(message))
            message_bottom_y = messages_area_bottom_y - 3

        message_bottom_y = message_bottom_y - 3 - line_num
