def running_total(values):
    """Return cumulative totals: [1,2,3] -> [1,3,6]."""
    totals = []
    acc = 0
    for v in values[1:]:
        acc += v
        totals.append(acc)
    return totals
