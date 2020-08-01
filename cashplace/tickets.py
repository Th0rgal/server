from bit import Key, PrivateKeyTestnet


class Ticket:
    pass


class BitcoinTicket(Ticket):
    pass


class TicketsFactory:
    def __init__(self, config):
        self.config = config

    def create_ticket(self, coin):
        if coin == "btc":
            return Ticket()
        else:
            pass
