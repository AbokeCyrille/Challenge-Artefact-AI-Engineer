def exact_match(pred, gold):
    return pred == gold

def numeric_match(pred, gold, tolerance=0):
    return abs(pred - gold) <= tolerance
