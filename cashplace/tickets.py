from bit import Key, PrivateKeyTestnet
from errors import Unauthorized
from storage import data
from enum import Enum
import time
import argon2


class TicketStatus(Enum):
    CONFIGURATION = 0
    PAYMENT = 1
    RECEPTION = 2
    RECEIVED = 3
    DISPUTE = 4


class TicketsManager:
    def __init__(self, config):
        self.config = config
        self.tickets = {}

    def load(self):
        tickets = data.load_all_tickets()
        for ticket_name in tickets:
            ticket_content = tickets[ticket_name]
            ticket = self.load_ticket(ticket_content)
            if ticket:
                self.tickets[ticket.id] = ticket

    def save(self):
        for ticket_id in self.tickets():
            self.tickets[ticket_id].save()

    def create_ticket(self, coin):
        if coin == "btc":
            ticket = BitcoinTicket.create(self.config.test_net)
        else:
            return False
        ticket.save()
        return ticket

    def load_ticket(self, json_content):
        coin = json_content["coin"]
        if coin == "btc":
            return BitcoinTicket.load(json_content, self.config.test_net)
        else:
            return False


class Ticket:
    def __init__(self):
        self.password_hasher = argon2.PasswordHasher()

    def save(self):
        data.save_ticket(self)

    def delete(self):
        data.delete_ticket(self.id)

    def update(self):
        self.last_update = time.time()
        self.save()

    def login(self, password, spender):
        if spender:
            if self.spender_hash is not None:
                self.verify_password(password, self.spender_hash, True)
        else:
            if self.receiver_hash is not None:
                self.verify_password(password, self.spender_hash, False)
        return {"connected": True}

    def verify_password(self, password, password_hash, spender):
        try:
            self.password_hasher.verify(password_hash, password)
            if self.password_hasher.check_needs_rehash(password_hash):
                if spender:
                    self.spender_hash = self.password_hasher.hash(password)
                else:
                    self.receiver_hash = self.password_hasher.hash(password)

        except argon2.exceptions.VerifyMismatchError:
            raise Unauthorized("Wrong password")


class BitcoinTicket(Ticket):
    @classmethod
    def create(cls, test):
        self = BitcoinTicket(PrivateKeyTestnet() if test else Key())
        self.last_update = time.time()
        return self

    @classmethod
    def load(cls, json_content, test):
        wif = json_content["wif"]
        self = BitcoinTicket(
            PrivateKeyTestnet(wif) if test else Key(wif),
            json_content["spender_hash"],
            json_content["receiver_hash"],
            TicketStatus(json_content["status"]),
        )
        self.last_update = json_content["last_update"]
        return self

    def __init__(
        self,
        key,
        spender_hash=None,
        receiver_hash=None,
        status=TicketStatus.CONFIGURATION,
    ):
        super().__init__()
        self.key = key
        self.spender_hash = spender_hash
        self.receiver_hash = receiver_hash
        self.status = status

    @property
    def id(self):
        return self.key.segwit_address

    @property
    def wif(self):
        return self.key.to_wif()

    @property
    def export(self):
        return {
            "coin": "btc",
            "wif": self.wif,
            "spender_hash": self.spender_hash,
            "receiver_hash": self.receiver_hash,
            "status": self.status.value,
            "last_update": self.last_update,
        }
