from .config import *
from .loader import load_strategy_config, load_notification_config


STRATEGY_CONFIG = load_strategy_config(STRATEGY_CONFIG_PATH)
NOTIFICATION_CONFIG = load_notification_config(CONFIG_PATH)