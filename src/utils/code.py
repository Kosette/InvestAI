def get_fullcode(code: str) -> str:
    if code.startswith("00") or code.startswith("30"):
        return f"sz{code}"
    elif code.startswith("60"):
        return f"sh{code}"
    else:
        return code