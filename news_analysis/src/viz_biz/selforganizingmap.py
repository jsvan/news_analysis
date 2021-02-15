from minisom import MiniSom
from news_analysis.src.tools.read_matrices import read as RM
import numpy as np
# import pandas as pd
import matplotlib.pyplot as plt
# from matplotlib.patches import Patch
# from sklearn import datasets
from sklearn.preprocessing import scale

import matplotlib.colors

def categorical_cmap(nc, nsc, cmap="tab10", continuous=False):
    if nc > plt.get_cmap(cmap).N:
        raise ValueError("Too many categories for colormap.")
    if continuous:
        ccolors = plt.get_cmap(cmap)(np.linspace(0,1,nc))
    else:
        ccolors = plt.get_cmap(cmap)(np.arange(nc, dtype=int))
    cols = np.zeros((nc*nsc, 3))
    for i, c in enumerate(ccolors):
        chsv = matplotlib.colors.rgb_to_hsv(c[:3])
        arhsv = np.tile(chsv,nsc).reshape(nsc,3)
        arhsv[:,1] = np.linspace(chsv[1],0.25,nsc)
        arhsv[:,2] = np.linspace(chsv[2],1,nsc)
        rgb = matplotlib.colors.hsv_to_rgb(arhsv)
        cols[i*nsc:(i+1)*nsc,:] = rgb
    cmap = matplotlib.colors.ListedColormap(cols)
    return cmap
"""
c1 = categorical_cmap(4, 3, cmap="tab10")
plt.scatter(np.arange(4*3),np.ones(4*3)+1, c=np.arange(4*3), s=180, cmap=c1)

c2 = categorical_cmap(2, 5, cmap="tab10")
plt.scatter(np.arange(10),np.ones(10), c=np.arange(10), s=180, cmap=c2)

c3 = categorical_cmap(10, 3, cmap="tab10")
plt.scatter(np.arange(20),np.ones(20)-1, c=np.arange(20), s=180, cmap=c3)    

plt.margins(y=0.3)
plt.xticks([])
plt.yticks([0,1,2],["(5, 4)", "(2, 5)", "(4, 3)"])
plt.show()
"""



def run(dimensions=(30,30), iterations=1000):
    data_targets, topicscount, nameslist, totalcolors = RM(pad=True, dense=True, earlystop=True)
    data_targets = data_targets[:50]
    data = [x[0] for x in data_targets]
    data = scale(data)
    print('LEN', len(data))
    #for i in data[:10]:
    #    print(i)
    #    for ii, x in enumerate(i):
    #        if x != 0:
    #            print(ii, x)
    som = MiniSom(dimensions[0], dimensions[1], topicscount, sigma=4, learning_rate=0.5)  # , neighborhood_function='triangle')
    #som.pca_weights_init(data)
    som.train(data, iterations, random_order=True, verbose=True)  # trains the SOM with 100 iterations
    print("Done training")
    print("plotting fig")
    plt.figure(figsize=(8, 8))
    wmap = {}
    im = 0
    c3 = categorical_cmap(10, 3, cmap="tab10")
    for i, (x, t) in enumerate(data_targets):  # scatterplot
        print(i, len(data_targets), end='\r')
        w = som.winner(x)
        wmap[w] = im
        plt.text(w[0]+.5,  w[1]+.5,  str(t),
                  color=c3(t), fontdict={'weight': 'bold',  'size': 11})
        im = im + 1
    plt.axis([0, som.get_weights().shape[0], 0,  som.get_weights().shape[1]])
    plt.title(f"{nameslist}")
    plt.savefig('som_digts.png')
    plt.show()