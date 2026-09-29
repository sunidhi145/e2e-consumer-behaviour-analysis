import math


def humanize_column(name):
    text = str(name).replace("log_", "").replace("_", " ").strip()
    return text.title()


def format_number(value, digits=2):
    if value is None:
        return "N/A"
    try:
        if isinstance(value, str):
            return value
        if not math.isfinite(float(value)):
            return "N/A"
        value = float(value)
    except (TypeError, ValueError):
        return str(value)
    if abs(value) >= 1000:
        return f"{value:,.0f}"
    if value.is_integer():
        return f"{value:,.0f}"
    return f"{value:,.{digits}f}"


def display_value(value):
    if value is None:
        return "N/A"
    try:
        if math.isnan(float(value)):
            return "N/A"
    except (TypeError, ValueError):
        pass
    return format_number(value) if isinstance(value, (int, float)) else str(value)
