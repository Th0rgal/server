from bit import Key, PrivateKeyTestnet
from storage import data


class TicketsManager:
    def __init__(self, config):
        self.config = config

    def load(self):
        for ticket_content in data.load_all_tickets():
            self.create_ticket(ticket_content["coin"])

    def create_ticket(self, coin):
        if coin == "btc":
            return BitcoinTicket()
        else:
            return False

    def load_ticket(self, json_content):
        pass


class Ticket:
    def save(self):
        pass


class BitcoinTicket(Ticket):
    def __init__(self):
        self.key = PrivateKeyTestnet()
        self.public_address = self.key.segwit_address
        self.wif = self.key.to_wif()

    @property
    def id(self):
        return self.public_address
