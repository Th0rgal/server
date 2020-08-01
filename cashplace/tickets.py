from bit import Key, PrivateKeyTestnet


class Ticket:
    def __init__(self, config):
        self.key = PrivateKeyTestnet() if config.test_net else Key()
        self.address = self.key.segwit_address
        self.private = self.key.to_wif()
