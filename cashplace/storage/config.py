import os
import toml
import shutil


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
            print(f"config {file_name} doesn't exist, copying template!")
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
        self.test_net = bitcoin["test_net"]
