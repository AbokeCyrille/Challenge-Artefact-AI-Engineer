import re


def extract_range_params(question: str):
    """
    Extract numeric ranges like:
    - "entre 30% et 50%"
    - "between 10 and 20"
    - "plus de 40%"
    """
    q = question.lower()
    params = {}

    # entre X et Y
    match = re.search(r"entre\s+(\d+)\s*%?\s+et\s+(\d+)", q)
    if match:
        params["min_pct"] = int(match.group(1))
        params["max_pct"] = int(match.group(2))
        return params

    # between X and Y
    match = re.search(r"between\s+(\d+)\s+and\s+(\d+)", q)
    if match:
        params["min_pct"] = int(match.group(1))
        params["max_pct"] = int(match.group(2))
        return params

    # plus de X
    match = re.search(r"plus\s+de\s+(\d+)", q)
    if match:
        params["min_pct"] = int(match.group(1))
        params["max_pct"] = 100
        return params

    # more than X
    match = re.search(r"more\s+than\s+(\d+)", q)
    if match:
        params["min_pct"] = int(match.group(1))
        params["max_pct"] = 100
        return params

    return params
