# categories.py
# Mapping human-readable category names → Google Trends numeric category ID

CATEGORY_MAP = {
    "All": 0,
    "Arts & Entertainment": 3,
    "Arts & Entertainment/TV & Video": 34,
    "Arts & Entertainment/TV & Video/Online Video": 1358,
    # Add more as needed — Google provides a full list you can mirror here.
}

def category_to_id(category_str: str) -> int:
    if category_str not in CATEGORY_MAP:
        raise ValueError(
            f"Unknown category '{category_str}'. "
            f"Add it to CATEGORY_MAP in categories.py."
        )
    return CATEGORY_MAP[category_str]
