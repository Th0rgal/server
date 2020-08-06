from bit import Key, PrivateKeyTestnet
from errors import Unauthorized, TicketNotFound
from storage import data
from enum import Enum
import time
import argon2
import logging

logger = logging.getLogger(__name__)


def clean(tickets_manager, config):
    # we must not change the size of dictionnary in  so let's use a queue
    to_delete = []
    for ticket_id in tickets_manager.tickets:
        ticket = tickets_manager.tickets[ticket_id]
        delay = time.time() - ticket.last_update

        if ticket.status == TicketStatus.CONFIGURATION:
            if delay > config.configuration_delay:
                to_delete.append(ticket_id)

        elif ticket.status == TicketStatus.RECEPTION:
            if delay > config.reception_delay:
                ticket.cancel()
                to_delete.append(ticket_id)

        elif ticket.status == TicketStatus.RECEIVED:
            if delay > config.received_delay:
                ticket.finalize()

        elif ticket.status == TicketStatus.SENDING:
            # todo: check if bitcoins have been sent
            ticket.set_status(TicketStatus.SENT)
            # else if the transaction didn't get confirmed within the
            # configured delay
            if delay > config.sending_delay:
                ticket.set_status(TicketStatus.RECEIVED)

        elif ticket.status == TicketStatus.SENT:
            if delay > config.sent_delay:
                ticket.cancel()
                to_delete.append(ticket_id)

        elif ticket.status == TicketStatus.DISPUTE:
            if delay > config.dispute_delay:
                ticket.cancel()
                to_delete.append(ticket_id)

    for ticket_id in to_delete:
        logger.warning(f"deleting ticket {ticket_id}")
        tickets_manager.delete_ticket(ticket_id)


class TicketStatus(Enum):
    CONFIGURATION = 0
    RECEPTION = 1
    RECEIVED = 2
    SENDING = 3
    SENT = 4
    DISPUTE = 5


class TicketsManager:
    def __init__(self, config):
        self.config = config
        BitcoinTicket.rate = config.btc_rate
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
            ticket = BitcoinTicket.create(self.config.btc_testnet)
        else:
            return False
        self.tickets[ticket.id] = ticket
        ticket.save()
        return ticket

    def load_ticket(self, json_content):
        coin = json_content["coin"]
        if coin == "btc":
            return BitcoinTicket.load(json_content, self.config.btc_testnet)
        else:
            return False

    def delete_ticket(self, ticket_id):
        if not ticket_id in self.tickets:
            raise TicketNotFound(f"failed to delete ticket {ticket_id}")
        self.tickets.pop(ticket_id).delete()


class Ticket:
    def __init__(
        self,
        amount,
        spender_hash,
        receiver_hash,
        master_is_spender,
        leftover_address,
        receiver_address,
        status,
    ):
        self.amount = amount
        self.spender_hash = spender_hash
        self.receiver_hash = receiver_hash
        self.master_is_spender = master_is_spender
        self.leftover_address = leftover_address
        self.receiver_address = receiver_address
        self.status = status
        self.password_hasher = argon2.PasswordHasher()

    def save(self):
        data.save_ticket(self)

    def delete(self):
        data.delete_ticket(self.id)

    def update(self):
        self.last_update = time.time()
        self.save()

    def set_amount(self, amount, update=True):
        self.amount = amount
        if update:
            self.update()

    def set_leftover_address(self, address, update=True):
        self.leftover_address = address
        if update:
            self.update()

    def set_receiver_address(self, address, update=True):
        self.receiver_address = address
        if update:
            self.update()

    def set_status(self, status, update=True):
        self.status = status
        if update:
            self.update()

    def verify_password(self, password, spender):
        if password is None:
            raise Unauthorized("A password is required")

        if spender:
            if self.spender_hash is None:
                self.spender_hash = self.password_hasher.hash(password)
                if self.receiver_hash is None:
                    self.master_is_spender = True
                return
            password_hash = self.spender_hash

        else:
            if self.receiver_hash is None:
                self.receiver_hash = self.password_hasher.hash(password)
                if self.spender_hash is None:
                    self.master_is_spender = False
                return
            password_hash = self.receiver_hash

        try:
            self.password_hasher.verify(password_hash, password)
            if self.password_hasher.check_needs_rehash(password_hash):
                password_hash = self.password_hasher.hash(password)
            if spender:
                self.spender_hash = password_hash
            else:
                self.receiver_hash = password_hash
            self.update()
        except argon2.exceptions.VerifyMismatchError:
            raise Unauthorized("Wrong password")


class BitcoinTicket(Ticket):

    coin = "btc"

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
            json_content["amount"],
            json_content["spender_hash"],
            json_content["receiver_hash"],
            json_content["master_is_spender"],
            json_content["leftover_address"],
            json_content["receiver_address"],
            TicketStatus(json_content["status"]),
        )
        self.last_update = json_content["last_update"]
        return self

    def __init__(
        self,
        key,
        amount=0,
        spender_hash=None,
        receiver_hash=None,
        master_is_spender=None,
        leftover_address=None,
        receiver_address=None,
        status=TicketStatus.CONFIGURATION,
    ):
        super().__init__(
            amount,
            spender_hash,
            receiver_hash,
            master_is_spender,
            leftover_address,
            receiver_address,
            status,
        )
        self.key = key

    def refresh_balance(self):
        self.balance = self.key.get_balance("btc")
        if self.balance >= self.amount:
            if self.status == TicketStatus.RECEPTION:
                self.set_status(TicketStatus.RECEIVED, False)
        elif self.balance == 0:
            if self.status == TicketStatus.RECEIVED:
                self.set_status(TicketStatus.SENDING, False)
        self.update()

    def cancel():
        # todo: send BTC to leftover_address
        self.key.create_transaction([], leftover=self.leftover_address)
        pass

    def finalize():
        # todo: send BTC
        ticket.set_status(TicketStatus.SENDING)

    @property
    def id(self):
        return self.key.segwit_address

    @property
    def wif(self):
        return self.key.to_wif()

    @property
    def export(self):
        return {
            "coin": self.coin,
            "amount": self.amount,
            "wif": self.wif,
            "spender_hash": self.spender_hash,
            "receiver_hash": self.receiver_hash,
            "master_is_spender": self.master_is_spender,
            "leftover_address": self.leftover_address,
            "receiver_address": self.receiver_address,
            "status": self.status.value,
            "last_update": self.last_update,
        }
