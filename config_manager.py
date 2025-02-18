import configparser

class ConfigManager:
    # コンストラクタ
    def __init__(self, config_file='config/config.ini'):
        self.config_file = config_file
        self.config = configparser.ConfigParser()
        self.config.read(self.config_file)

    # セクションとキーを指定して値を取得
    def get(self, section, key):
        return self.config[section][key]

    # セクションとキーを指定して値を設定
    def set(self, section, key, value):
        self.config[section][key] = value
        with open(self.config_file, 'w') as configfile:
            self.config.write(configfile)
