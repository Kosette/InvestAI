# utils/json_utils.py

import orjson
import numpy as np
from enum import Enum
from typing import Any


def _json_default(obj: Any):
    """
    orjson 默认序列化回调
    用于处理非原生 JSON 类型
    """
    if isinstance(obj, Enum):
        return obj.value

    if isinstance(obj, np.generic):
        return obj.item()

    # 可选：支持 numpy array
    if isinstance(obj, np.ndarray):
        return obj.tolist()

    # 可选：支持 Pydantic v2
    if hasattr(obj, "model_dump"):
        return obj.model_dump()

    raise TypeError(f"Object of type {type(obj).__name__} is not JSON serializable")


def to_pretty_json(data: Any) -> str:
    """
    将 Python 对象安全序列化为可读 JSON 字符串
    """
    return orjson.dumps(data, default=_json_default, option=orjson.OPT_INDENT_2).decode(
        "utf-8"
    )
