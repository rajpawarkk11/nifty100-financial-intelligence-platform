"""
Normalisation utilities.
"""

import re


def normalize_year(value):

    if value is None:
        return None

    value = str(value).strip()

    match = re.search(r"\d{4}", value)

    if match:
        return int(match.group())

    return None


def normalize_ticker(value):

    if value is None:
        return None

    value = str(value).strip().upper()

    value = value.replace(".NS", "")
    value = value.replace("-EQ", "")
    value = value.replace(" ", "")

    return value