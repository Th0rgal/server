import os
import json
from pathlib import Path


def get_subfolder(name):
    folder = os.path.join(os.path.dirname(os.path.realpath(__file__)), name)
    Path(folder).mkdir(parents=True, exist_ok=True)
    return folder


def _load(subfolder, file_name):
    file = os.path.join(get_subfolder(subfolder), file_name)
    with open(file) as json_file:
        return json.load(json_file)


def _save(subfolder, file, content):
    with open(os.path.join(get_subfolder(subfolder), file), "w") as outfile:
        json.dump(content, outfile)


def _delete(subfolder, file):
    Path(os.path.join(os.path.dirname(get_subfolder(subfolder), file))).unlink()


def load_ticket(ticket_name):
    return _load("tickets", ticket_name)


def load_all_tickets():
    tickets = {}
    for filename in os.listdir(get_subfolder("tickets")):
        tickets[filename] = load_ticket(filename)
    return tickets


def save_ticket(ticket):
    _save("tickets", ticket.id, ticket.export)
