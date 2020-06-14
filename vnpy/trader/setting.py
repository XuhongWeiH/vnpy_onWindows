"""
Global setting of VN Trader.
"""

from logging import CRITICAL
from typing import Dict, Any

from .utility import load_json

SETTINGS: Dict[str, Any] = {
    "font.family": "Arial",
    "font.size": 12,

    "log.active": True,
    "log.level": CRITICAL,
    "log.console": True,
    "log.file": True,

    "email.server": "smtp.qq.com",
    "email.port": 465,
    "email.username": "",
    "email.password": "",
    "email.sender": "",
    "email.receiver": "",

    "rqdata.username": "",
    "rqdata.password": "",

    "database.driver": "mongodb",
    "database.database": "weixuhong_data_1234",
    "database.host": "localhost",
    "database.port": 27017,
    "database.user": "",
    "database.password": "",
    "database.authentication_source": ""
}

# Load global setting from json file.
SETTING_FILENAME: str = "vt_setting.json"

SETTINGS.update(load_json(SETTING_FILENAME))

def get_settings(prefix: str = "") -> Dict[str, Any]:
    prefix_length = len(prefix)
    return {k[prefix_length:]: v for k, v in SETTINGS.items() if k.startswith(prefix)}
