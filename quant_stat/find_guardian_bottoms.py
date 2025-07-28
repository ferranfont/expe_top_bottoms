import pandas as pd

def group_consecutive_bottoms(bottoms, guardian=3, max_gap=5):
    """
    Agrupa bottoms cercanos en valor (≤ guardian) y en índice (≤ max_gap, no requiere consecutividad).
    Devuelve un DataFrame con:
        - index, value
        - cluster_id
        - tag
        - is_min
        - min_value
    """
    rows = []
    current_cluster = []
    cluster_id = 0

    for i in range(len(bottoms)):
        curr_index, curr_value = bottoms[i]

        if not current_cluster:
            current_cluster.append((curr_index, curr_value))
            continue

        last_index, last_value = current_cluster[-1]

        if abs(curr_index - last_index) <= max_gap and abs(curr_value - last_value) <= guardian:
            current_cluster.append((curr_index, curr_value))
        else:
            if len(current_cluster) > 1:
                min_idx, min_val = min(current_cluster, key=lambda x: x[1])
                for idx, val in current_cluster:
                    rows.append({
                        'index': idx,
                        'value': val,
                        'cluster_id': cluster_id,
                        'tag': f'cluster_{cluster_id}',
                        'is_min': idx == min_idx,
                        'min_value': min_val
                    })
                cluster_id += 1
            current_cluster = [(curr_index, curr_value)]

    # último grupo
    if len(current_cluster) > 1:
        min_idx, min_val = min(current_cluster, key=lambda x: x[1])
        for idx, val in current_cluster:
            rows.append({
                'index': idx,
                'value': val,
                'cluster_id': cluster_id,
                'tag': f'cluster_{cluster_id}',
                'is_min': idx == min_idx,
                'min_value': min_val
            })

    return pd.DataFrame(rows)
