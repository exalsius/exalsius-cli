import os
from pathlib import Path

CFG_DIR = Path(os.getenv("XDG_CONFIG_HOME", "~/.config")).expanduser() / "exalsius"
CFG_FILE = CFG_DIR / "config.yaml"
CONFIG_LOCK_FILE = CFG_DIR / "config.lock"

CONFIG_ENV_PREFIX = "EXLS_"
CONFIG_ENV_NESTED_DELIMITER = "__"
