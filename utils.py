import socket
from contextlib import closing
import threading, webbrowser, time

# * Set up the port
def find_free_port():
    """ Find a free port on localhost. """
    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(('', 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return s.getsockname()[1]
    
def auto_opentab_delay(port):
    """ Open a new tab in the browser after a delay. """
    def open(): time.sleep(2)
    webbrowser.open_new_tab(f'http://localhost:{port}')
    t = threading.Thread(target=open)
    t.daemon = True; t.start()

def hide_middle_chars(s):
    if len(s) <= 8:
        return s
    else:
        head = s[:4]
        tail = s[-4:]
        hidden = "*" * (len(s) - 8)
        return head + hidden + tail
