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
import subprocess
import re
import shutil
import shared
from pydbus import SystemBus
from gi.repository import GLib

bus = SystemBus()

from curses.textpad import Textbox, rectangle

def get_signal_object(with_number=False,with_configuration=False):
    signal = None
    if with_number is True: with_number = shared.phone_number
    try:
        if with_number is False: signal = bus.get('org.asamk.Signal', object_path='/org/asamk/Signal')
        elif with_configuration: signal = bus.get('org.asamk.Signal', object_path='/org/asamk/Signal/{}/Configuration'.format(with_number.replace("+","_")))
        else: signal = bus.get('org.asamk.Signal', object_path='/org/asamk/Signal/{}'.format(with_number.replace("+","_")))
    except Exception as e:
        print (e)
    return signal


# Registers the user with Whisper Systems. If it works, they will send a
# verification number to the user's phone
def register_device(pnum):
    shared.phone_number = str(pnum)
    #x = subprocess.run(["signal-cli", "-u", shared.phone_number, "register"], capture_output=True, text=True)
    #return x.stdout.strip()
    signal = get_signal_object(False)
    return signal.register(shared.phone_number)

# Send's user's verification number to Whisper Systems
def verify_code(verification_number):
    verification_number = str(verification_number)
    #x = subprocess.run(["signal-cli", "-u", shared.phone_number, "verify", verification_number])
    signal = get_signal_object(False)
    return signal.verify(shared.phone_number, verification_number)

# Links this client with a phone number (at least it returns the url which can be scanned by signal phone client)
def link_device(device_name="Signal TUI"):
    signal = get_signal_object(False)
    return signal.link(device_name).strip()

# Sends a message to another signal user
def send_message(recipient, message):
    curses.curs_set(0)
    r = str(recipient)
    recipient = [str(recipient)]
    #x = subprocess.run(["signal-cli", "-u", shared.phone_number, "send", "-m", message, recipient])
    signal = get_signal_object(True)
    t = signal.sendMessage(message, [], recipient)
    syncMessageReceive(t, shared.phone_number, r, [], message, False)
    return t

# Get messages from file
def get_messages():
    output = []
    if len(shared.contact_buffer) > 0:
        for i in shared.contact_buffer: output.append([i, []])

    regex = r"\[(r|s)\] \[([\d]+)(:[\d]+|)\] <(\+[\d]+)> ([^\n]+)"
    #           1   2        3           4             5
    #          [r] [12389765:312083712] <+11234567890> Hi there
    #          [r] [12389765]           <+11234567890> text test test

    signal = get_signal_object(True)
    logfile = open("logfile.txt", "r")
    for line in logfile:
        match = re.search(regex, line)
        if match:
            id = -1
            for i, u in enumerate(output):
                if u[0][0] == match.group(4):
                    id = i
                    break
            msg = match.group(5).replace("\\n", "\n")
            if id == -1: output.append([[match.group(4), signal.getContactName(match.group(4))],[[match.group(1), msg, match.group(2), match.group(3)]]])
            else: output[id][1].append([match.group(1), msg, match.group(2), match.group(3)])
    logfile.close()
    return output

# Receive messages from others
def messageReceive(timestamp, sender, groupID, message, attachments):
    if len(groupID) == 0: # Skip groups which makes the receiver always me, so save by sender
        f = open("logfile.txt", "a")
        f.write("[r] [{time}] <{sender}> {message}\n".format(time=timestamp, sender=sender, message=message.strip().replace("\n", "\\n")))
        f.close()

        id = -1
        for i, c in enumerate(shared.contact_buffer):
            if c[0] == sender: id = i

        shared.add_message(id, "r", message, timestamp, True)
        curses.beep()

        signal = get_signal_object(True)
        signal.sendViewedReceipt(sender, [timestamp])

# Receive messages sent by your phonenumber, but not by this device
def syncMessageReceive(timestamp, sender, destination, groupID, message, attachments):
    if len(groupID) == 0: # Skip groups, sender is always me, destination is the user
        found = False
        shutil.copyfile("logfile.txt", "logfile2.txt") # Copy to tmp file, since cannot read when write
        with open("logfile2.txt", "w" if attachments is False and type(sender) is int else "a") as new_file:
            new = "[s] [{time}] <{dest}> {message}\n".format(time=timestamp, dest=destination, message=message.strip().replace("\n", "\\n"))
            if attachments is False and type(sender) is int: # when editing message, we send this, but with sender to the old timestamp
                with open("logfile.txt", "r") as old_file:
                    search = "[s] [{time}] <{dest}> ".format(time=sender, dest=destination)
                    new = new.replace(timestamp, "{}:{}".format(sender, timestamp)) # sender is old
                    for line in old_file:
                        check = line.startswith(search) or line.startswith("[s] [" + str(sender) + ":") and str("] <"+destination+"> ") in line # dont know the new original value
                        if check: found = True
                        new_file.write(new if check else line)
            if not(found):
                new_file.write(new)
            new_file.close()

        shutil.move("logfile2.txt", "logfile.txt")

        if not(found) and not(attachments is False): # It is set to False at send_message function, since send_message is used in messages.py which adds the message as well
            id = -1
            for i, c in enumerate(shared.contact_buffer):
                if c[0] == destination: id = i
            shared.add_message(id, "s", message, timestamp)

# Run message listener in background
def signalMessageListener(number=None):
    number = True if number is None else number
    signal = get_signal_object(number)
    signal.onMessageReceived = messageReceive
    signal.onSyncMessageReceived = syncMessageReceive
    loop = GLib.MainLoop()
    try:
        loop.run()
    except:
        pass # Exit loop on error

# Receive users
def get_contacts():
    signal = get_signal_object(True)
    numbers = signal.listNumbers()
    return [[number, signal.getContactName(number)] for number in numbers]

# Update contact info
def update_contact(type, contact, new_value):
    id = shared.contact_buffer.index(contact)
    if id == -1: return False

    signal = get_signal_object(True)
    if type == "number":
        # signal.setContactNumber() # This doesn't exist!
        shared.contact_buffer[id][0] = new_value
        return True
    if type == "name":
        signal.setContactName(contact[0], new_value)
        shared.contact_buffer[id][1] = new_value
        return True
    return False

# Edit a message
def edit_message(recipient, oldmessage, message):
    #curses.curs_set(0)
    r = recipient = str(recipient)
    if True: return False
    t = subprocess.run(["signal-cli", "-u", shared.phone_number, "send", "--edit-timestamp", str(oldmessage[2]), "-m", message, recipient], capture_output=True, text=True)
    t = t.stdout.strip()
    #signal = get_signal_object(True)
    #t = signal.sendEditMessage(message, recipient, oldmessage[2])
    syncMessageReceive(t, int(oldmessage[2]), r, [], message, False) # t, sender=oldtimestamp
    return t

# Send read status of the message (should be done when the message is shown)
def send_read_message(recipient, timestamps):
    signal = get_signal_object(True)
    if not(type(timestamps) is list): timestamps = [timestamps]
    return signal.sendReadReceipt(recipient, timestamps)

# Send typing status (should be used when "i" been pressed in chat box)
def send_typing(recipient, stop=False):
    signal = get_signal_object(True)
    return signal.sendTyping(recipient, stop)

# Get configuration properties
def get_configuration(pnum=True):
    config = get_signal_object(pnum,True)
    return {
        "ReadReceipts": config.ReadReceipts,
        "UnidentifiedDeliveryIndicators": config.UnidentifiedDeliveryIndicators,
        "TypingIndicators": config.TypingIndicators,
        "LinkPreviews": config.LinkPreviews,
    }

def set_configuration(pnum=True, read_receipts=None, unidentified_delivery_indicators=None, typing_indicators=None, link_previews=None):
    config = get_signal_object(pnum,True)
    if not(read_receipts is None): config.ReadReceipts = read_receipts
    if not(unidentified_delivery_indicators is None): config.UnidentifiedDeliveryIndicators = unidentified_delivery_indicators
    if not(typing_indicators is None): config.TypingIndicators = typing_indicators
    if not(link_previews is None): config.LinkPreviews = link_previews
    return True

