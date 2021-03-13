import os
from dotenv import load_dotenv


class HelperDir:
    def __init__(self, env_dir: str):
        self.is_loaded = None
        self.load_environment(env_dir)

    def load_environment(self, env_dir: str):
        self.is_loaded = load_dotenv(env_dir)

    def get_env_variable(self, arg: str):
        if self.is_loaded:
            print(os.environ)
            return os.getenv(arg)
