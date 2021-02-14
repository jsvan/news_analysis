# import sys
import numpy as np
from matplotlib import pyplot
import matplotlib.colors as mcolors
# from sklearn.preprocessing import MinMaxScaler
from sklearn.decomposition import PCA
#  TODO USE  TruncatedSVD to 50 dim. then T-SNE from Scikitlearn
# from sklearn import manifold
from sklearn.manifold import MDS
from sklearn.manifold import TSNE
# from sklearn.metrics import euclidean_distances
import pickle
from sklearn.cluster import KMeans  # , MiniBatchKMeans


## TODO Do this again but look at all the candidates, PCA down to like 8 dimensions, then a clustering algorithm
## TODO Still use Uni resources,

def normalize(matrix, where):
    # Divide every row's values by the number of articles of that publisher present
    # dict(names -> [row row row row])
    namerows = pickle.load(open(where, 'rb'))
    for name, rows in namerows.items():
        denominator = len(rows)
        for row in rows:
            matrix[row] = matrix[row]/denominator
    return matrix



def get_name_colors(where, count):
    namecolors = pickle.load(open(where, 'rb'))
    # dict(names -> [row row row row])
    colorcounter = 0
    # take out white
    colors = list(mcolors.BASE_COLORS.keys())[:-1] + list(mcolors.TABLEAU_COLORS.keys())
    colorlist = ['w']*count
    name2colordict = {'error': 'w'}
    for name, rows in namecolors.items():
        if name not in name2colordict:
            name2colordict[name] = colors[colorcounter]
            colorcounter += 1
        assoccolor = name2colordict[name]
        for r in rows:
            colorlist[r] = assoccolor
    color2namedict = {y:x for x, y in name2colordict.items()}
    # print(colorlist)
    # input()
    # print(namecolors)
    # input()
    return colorlist, color2namedict

# Probably need to flip matrix 90degrees
# Will return [article x topics]
def load_matrix(where):
    return np.load(where).transpose()


def pca(MATRIX):
    #x = MinMaxScaler().fit_transform(MATRIX) # normalizing the features
    pca = PCA(n_components=2)
    #pp.scatter(p[:,0], p[:,1])
    results =  pca.fit_transform(MATRIX)
    return results[:,0], results[:,1]


def multdimscaling(MATRIX):
    #MATRIX = MinMaxScaler().fit_transform(MATRIX)
    embedding = MDS(n_components=2)
    results = embedding.fit_transform(MATRIX)
    return results[:, 0], results[:, 1]


def tsne(MATRIX):
    #MATRIX = MinMaxScaler().fit_transform(MATRIX)
    results = TSNE(n_components=2).fit_transform(MATRIX)
    return results[:, 0], results[:, 1]


def Kmeans(MATRIX, num_publishers):
    km = KMeans(n_clusters=num_publishers, init='k-means++', max_iter=100, n_init=1)
    results = km.fit_transform(MATRIX)
    return results[:, 0], results[:, 1]



def plot(stuff, colorlist, color2namedict, title):
    sortedbycolor = dict()
    # Go through and group the dots by their colors,
    # so that we can plot each one and legend each one :eyeroll:
    for i, color in enumerate(colorlist):
        if color not in sortedbycolor:
            sortedbycolor[color] = [[],[]]
        sortedbycolor[color][0].append(stuff[0][i])
        sortedbycolor[color][1].append(stuff[1][i])

    for color, data in sortedbycolor.items():
        pyplot.scatter(data[0], data[1], s=2, color=color, label=color2namedict[color])
    pyplot.title(title)
    pyplot.legend()
    pyplot.show()


def go(m=None, matrixpath='', webnamespath=''):
    """

    :param m: needs to be  [article x topics]
    :param matrixpath:
    :param webnamespath:
    :return:
    """
    if not m:
        if matrixpath:
            m = load_matrix(matrixpath)
        if webnamespath:
            m = normalize(m, webnamespath)

    NORMALIZATIONNAME = 'normalized on count of articles'
    count = len(m)
    colorlist, color2namedict = get_name_colors(webnamespath, count)
    # Not very good clustering for these ones
    p = pca(m)
    plot(p, colorlist, color2namedict, 'pca '+NORMALIZATIONNAME)
    p = multdimscaling(m)
    plot(p, colorlist, color2namedict, 'multi-dimensional-scaling '+NORMALIZATIONNAME)
    p = tsne(m)
    plot(p, colorlist, color2namedict, 'tsne '+NORMALIZATIONNAME)

    p = Kmeans(m, len(color2namedict.keys()))
    plot(p, colorlist, color2namedict, 'kmeans '+NORMALIZATIONNAME)