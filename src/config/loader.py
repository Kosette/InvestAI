import yaml
from pathlib import Path
from .config import StrategyConfig


def load_strategy_config(path: str | Path) -> StrategyConfig:
    path = Path(path)

    if not path.exists():
        raise FileNotFoundError(f"Config file not found: {path}")

    with path.open("r", encoding="utf-8") as f:
        data = yaml.safe_load(f)

    return StrategyConfig(**data)
