import os


class Config:
    """
    Config class with the database creadentials
    """
    def __init__(self):
        self.db = os.environ["DATABASE"]
        self.user = os.environ["USER"]
        self.password = os.environ["PASSWORD"]
        self.host = os.environ["HOST"]
        self.port = os.environ["PORT"]

