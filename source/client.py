
#!/usr/bin/env python3

import sys
import socket
import selectors
import traceback
import os

import libclient
import logging_utilities
import protocol_definitions

sel = selectors.DefaultSelector()
os.makedirs("logs", exist_ok=True)
logger = logging_utilities.Logger(os.path.join("logs", "client.log"))

def create_request(action, value):
    if action == "help":
        if value:
            return protocol_definitions.HELP_MESSAGE_PROTOCOL_TYPE_CODE, (value,)
        else:
            return protocol_definitions.BASE_HELP_MESSAGE_PROTOCOL_TYPE_CODE, []

def start_connection(host, port, type_code, request):
    addr = (host, port)
    print("starting connection to", addr)
    sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    sock.setblocking(False)
    sock.connect_ex(addr)
    events = selectors.EVENT_READ | selectors.EVENT_WRITE
    message = libclient.Message(sel, sock, addr, type_code, request)
    sel.register(sock, events, data=message)


if len(sys.argv) not in [4, 5]:
    print("usage:", sys.argv[0], "<host> <port> <action> [<value>]")
    sys.exit(1)

host, port = sys.argv[1], int(sys.argv[2])
action = sys.argv[3]
value = ""
if len(sys.argv) == 5:
    value = sys.argv[4]
type_code, request = create_request(action, value)
start_connection(host, port, type_code, request)

try:
    while True:
        events = sel.select(timeout=1)
        for key, mask in events:
            message = key.data
            try:
                message.process_events(mask)
            except Exception:
                logger.log_message(
                    f"main: error: exception for {message.addr}:\n{traceback.format_exc()}",
                )
                message.close()
        # Check for a socket being monitored to continue.
        if not sel.get_map():
            break
except KeyboardInterrupt:
    print("caught keyboard interrupt, exiting")
finally:
    sel.close()
