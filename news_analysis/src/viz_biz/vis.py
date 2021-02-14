import os
import pandas as pd
from sparse_matrix import *
import sklearn
import seaborn as sb
import numpy as np
import matplotlib.pyplot as plt


def get_files():
    all_pkls = {}
    sources = os.listdir('matrices')

    for s in sources:
        source_path = os.path.join('matrices', s)
        pkls = (f for f in os.listdir(source_path) if f.endswith('.' + 'pkl'))
        for p in pkls:
            file_path = os.path.join(source_path, p)
            if (not source_path in all_pkls):
                all_pkls[source_path] = []

            all_pkls[source_path].append(file_path)

    return all_pkls


def flatten_sent(flat, loaded_mtx):
    for k, v in loaded_mtx.items():
        if (k[1] in flat):
            arr = flat[k[1]]
            arr[0] = arr[0] + v[0]
            arr[1] = arr[1] + v[1]
            arr[2] = arr[2] + v[2]
        else:
            flat[k[1]] = [v[0], v[1], v[2]]

    return flat


if __name__ == "__main__":
    all_files = get_files()
    print(all_files)

    all_flats = []
    for source in all_files:
        flat = {}
        for file in all_files[source]:
            loaded_mtx = jsv_dictmat(file)
            flat = flatten_sent(flat, loaded_mtx)
            # idx2NE = {}
            # with open("words2resolved.txt", encoding='utf-8') as F:
            #     idx2NE = {i:' '.join(x.split(' ')[1:]) for i, x in enumerate(F.read().split('\n')[:-1])}

        all_flats.append(flat)

    df_dict = []
    for k in all_flats:
        tmp_dict = {}
        print(k)
        # tmp_dict["topic"] = k

        # v = all_flats[k]
        # norm_sum = v[0] + v[1] + v[2]
        # # tmp_dict["neg"] = v[0]
        # # tmp_dict["neu"] = v[1]
        # # tmp_dict["pos"] = v[2]
        # tmp_dict["sum"] = (v[2] - v[0]) / norm_sum
        # df_dict.append(tmp_dict)

    # print(df_dict)
    # df = pd.DataFrame(df_dict)
    # df = df.pivot("article", "topic", "sum")
    # ax = sb.heatmap(df)
    # plt.show()