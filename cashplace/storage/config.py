import os
import toml
import shutil
import logging

logger = logging.getLogger(__name__)


class Config:

    # hardcoded
    __title__ = "cash.place"
    __author__ = "Th0rgal"
    __license__ = "DBAD"
    __version__ = "0.0.0"

    def get_path(self, name):
        return os.path.join(os.path.dirname(os.path.realpath(__file__)), name)

    def extract_config(self, file_name, template_name):
        config_file = self.get_path(file_name)
        self.is_new = not os.path.isfile(config_file)
        if self.is_new:
            logger.info(f"config {file_name} doesn't exist, copying template!")
            shutil.copyfile(self.get_path(template_name), config_file)
        return config_file


class TomlConfig(Config):
    def __init__(self, file_name, template_name):
        config_file = self.extract_config(file_name, template_name)
        self.load_config(config_file)

    def load_config(self, config_file):
        config = toml.load(config_file)

        server = config["server"]
        self.port = server["port"]

        bitcoin = config["bitcoin"]
        self.btc_testnet = bitcoin["test_net"]
        self.btc_rate = bitcoin["rate"]
        self.btc_master_address = bitcoin["master_address"]
        self.btc_confirmations = bitcoin["required_confirmations"]
        self.btc_static_minimal = bitcoin["static_minimal_amount"]
        self.btc_relative_minimal = bitcoin["relative_minimal_amount"]

        tickets = config["tickets"]
        self.global_delay = tickets["global_delay"]
        tickets_clean = tickets["clean"]
        self.auto_clean = tickets_clean["auto_clean"]
        self.task_delay = tickets_clean["task_delay"]
        self.configuration_delay = tickets_clean["configuration"] * 3600
        self.reception_delay = tickets_clean["reception"] * 3600
        self.received_delay = tickets_clean["received"] * 3600
        self.sending_delay = tickets_clean["sending"] * 3600
        self.sent_delay = tickets_clean["sent"] * 3600
        self.dispute_delay = tickets_clean["dispute"] * 3600
