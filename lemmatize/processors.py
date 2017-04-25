from typing import List, Tuple


def accumulation(timestamps: List[int], **kwargs) -> List[Tuple[int, int]]:
    count = 0
    data = []

    ts_i = iter(timestamps)
    ts = next(ts_i)
    prev_ts_i = iter(timestamps)

    width = kwargs.get("width", 60 * 60)

    try:
        while True:
            ts = next(ts_i)
            prev_ts = next(prev_ts_i)

            if ts - prev_ts > width:
                data.append((ts, count))

            count += 1

    except StopIteration:
        data.append((ts, count))

    return data


def sliding(timestamps: List[int], width=3600, **kwargs) -> List[Tuple[int, int]]:
    """
    
    :param timestamps: список исходных timestamp-ов
    :param width: ширина окна сдвига
    :return: 
    """
    data = []

    left = 0
    left_ts = timestamps[0]
    right = 0

    for i, ts in enumerate(timestamps):
        if ts - timestamps[0] < width:
            right = i
        else:
            break

    data.append((left_ts + width / 2, right - left))

    while right + 1 < len(timestamps):
        if timestamps[right + 1] - (left_ts + width) < timestamps[left + 1] - left_ts:
            right += 1
            left_ts = timestamps[right] - width
        else:
            left += 1
            left_ts = timestamps[left]

        data.append((left_ts + width / 2, right - left))

    return data


def diff(ts_val: List[Tuple[int, int]], **kwargs) -> List[Tuple[int, float]]:
    data = []

    prev_i = iter(ts_val)
    cur_i = iter(ts_val)
    next(cur_i)

    try:
        while True:
            ts_p, prev = next(prev_i)
            ts, cur = next(cur_i)

            if ts != ts_p:
                data.append((ts, (cur - prev) / (ts - ts_p)))
    except StopIteration:
        pass

    return data


def diff_ranged(ts_val: List[Tuple[int, float]], **kwargs) -> List[Tuple[int, float]]:
    data = []

    width = kwargs.get('width', 60 * 60)

    prev_v = 0
    prev_ts = ts_val[0][0]

    for ts, v in ts_val:
        if ts - prev_ts > width:
            data.append((
                (ts + prev_ts) / 2,
                (v - prev_v) / (ts - prev_ts)
            ))
            prev_ts = ts
            prev_v = v

    return data


def limit(ts_val: List[Tuple[int, int]], **kwargs) -> List[Tuple[int, float]]:
    data = []

    positive = [i[1] for i in ts_val if i[1] > 0]
    avg_p = sum(positive) / len(positive)

    negative = [i[1] for i in ts_val if i[1] < 0]
    avg_n = sum(negative) / len(negative)

    for ts, v in ts_val:
        if v > 0:
            v = min((v, avg_p))
        else:
            v = max((v, avg_n))

        data.append((ts, v))

    return data

