import os
import json
from pathlib import Path


def get_subfolder(name):
    folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
    Path(folder).mkdir(parents=True, exist_ok=True)
    return folder


def _load(subfolder, file):
    folder = get_subfolder(subfolder)
    return json.load(os.path.join(os.path.dirname(folder, file)))


def load_ticket(ticket_name):
    return _load("tickets", ticket_name)


def load_all_tickets():
    tickets = {}
    for filename in os.listdir(get_subfolder("tickets")):
        tickets[filename] = load_ticket(filename)
    return tickets
