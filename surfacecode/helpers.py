import numpy as np
import pandas


def parse_csv(path: str, length: int):
    """
    Parse CSV file with results from the IBM platform.
    """

    results = pandas.read_csv(path, delimiter=",")

    keys = []
    counts = []
    for i, result in enumerate(results.values):
        val = int(result[0], 16)
        key = bin(val)
        key = key[2:]
        key = '0' * (length - len(key)) + key
        print(key)
        count = int(result[1])
        keys.append(key)
        counts.append(count)

    shots = dict(keys=keys, counts=counts)

    return shots
