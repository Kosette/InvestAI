import re


def validate_stock_code(code: str) -> bool:
    """
    验证股票代码格式

    支持的格式:
    - 6位数字: 000001, 600519, 300750
    - 带前缀: sh000001, sz000001, sh600519, sz300750

    参数:
        code: 股票代码

    返回:
        bool: 是否为有效的股票代码格式
    """
    if not code or not isinstance(code, str):
        return False

    # A股股票代码通常是6位数字，或带sh/sz/bj前缀
    pattern = r"^[0-9]{6}$|^(sh|sz|bj)[0-9]{6}$"
    return bool(re.match(pattern, code.lower()))


def get_fullcode(code: str) -> str:
    if code.startswith("00") or code.startswith("30"):
        return f"sz{code}"
    elif code.startswith("60"):
        return f"sh{code}"
    else:
        return code


def extract_code(fullcode: str) -> str:
    """
    基于正则提取基础股票6位数代码
    """
    pattern = r"^(sh|sz)?(\d{6})$"
    match = re.match(pattern, fullcode)
    if match:
        return match.group(2)
    return fullcode
