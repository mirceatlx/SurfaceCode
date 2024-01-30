import numpy as np
import pandas


def parse_csv(path):
    """
    Parse CSV file with results from the IBM platform.
    """

    results = pandas.read_csv(path, delimiter=",")

    keys = []
    counts = []
    for result in results:
        val = int(result[0], 16)
        key = format(val, '0>42b')
        print(key)
        count = int(result[1])
        keys.append(key)
        counts.append(count)

    shots = dict(keys=keys, counts=counts)

    return shots
