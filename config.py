"""
Local/secret variables
"""

import os
from dotenv import load_dotenv
from pathlib import Path

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent

# DB config

DB_HOST = os.getenv('DB_HOST')
DB_NAME = os.getenv('DB_NAME')
DB_USER = os.getenv('DB_USER')
DB_PASSWORD = os.getenv('DB_PASSWORD')
DB_PORT = os.getenv('DB_PORT')

# NETWORK DEVICES CREDENTIALS

CISCO_LOGIN = os.getenv('CISCO_LOGIN')
CISCO_PASSWORD = os.getenv('CISCO_PASSWORD')
UBUNTU_SERVER_LOGIN = os.getenv('UBUNTU_SERVER_LOGIN')
UBUNTU_SERVER_PASSWORD = os.getenv("UBUNTU_SERVER_PASSWORD")

# File paths

LOG_PATH = Path(os.getenv('LOG_PATH', str(BASE_DIR / "./log/log.log")))
INVENTORY_PATH = Path(os.getenv('INVENTORY_PATH', str(BASE_DIR / "./data/inventory.yml")))