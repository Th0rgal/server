from bit import Key, PrivateKeyTestnet


class TicketsFactory:
    def __init__(self, config):
        self.config = config

    def create_ticket(self, coin):
        if coin == "btc":
            return BitcoinTicket()
        else:
            return False


class Ticket:
    pass


class BitcoinTicket(Ticket):
    def __init__(self):
        self.key = PrivateKeyTestnet()
        self.public_address = self.key.segwit_address
        self.wif = self.key.to_wif()

    @property
    def id(self):
        return self.public_address
