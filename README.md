# Signal TUI

A textual user interface for signal using signal-cli


## Dependencies

signal-tui relies on the following things:

- [signal-cli](https://github.com/AsamK/signal-cli), with the dbus service enabled!
- ncurses, which can be installed on ubuntu/debian with apt: `sudo apt install libncurses5-dev libncursesw5-dev`
- passlib, which can be installed with `python3 -m pip install passlib`
- qrcodegen, which can be installed with `python3 -m pip install qrcodegen`


## How to run

signal-tui can be started/used by running the `signal-tui.py` file: `python3 signal-tui.py`

Or make the file executable and run it:
```sh
chmod u+x signal-tui.py
./signal-tui.py
```


## Screenshot

![Signal-Tui Interface](signal-tui.png)


## Limitations

- Not all emoji's work, only those which are in your terminal font
- Attachments cannot be viewed and you won't even know if there is one at a message
- You cannot upload attachments
- Group channels are not supported
- Editing messages doesn't work, since dbus is not allowing it
- Markdown/Text Styling doesn't work
