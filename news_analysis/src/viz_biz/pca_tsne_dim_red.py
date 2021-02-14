import numpy as np
import time
from matplotlib import pyplot as plt
from sklearn.decomposition import TruncatedSVD
from sklearn.manifold import TSNE
from src.tools import read_matrices
from src.viz_biz.plot_design import mark
import random
idx2word = {}

def fill_new_vector(topics, vals, length):
    assert len(topics) == len(vals)
    vect = np.zeros(length)
    for i in range(len(vals)):
        vect[topics[i]] = vals[i]
    return vect


def prep_vect(topic, val, length, nickname):
    vect = np.zeros(length)
    if isinstance(type(topic), list):
        for i in range(len(topic)):
            vect[i] = val[i]
    else:
        vect[topic] = val
    return (vect, (nickname, idx2word[topic]))


def annotate_points(data, transformed, ratio, startat):
    global idx2word
    if not idx2word:
        idx2word = read_matrices.read_entities()
    selected = []
    neulow, neuhigh = -0.21, 0.21
    dT = np.array(data).transpose()  # dT is topics x entries
    # now to find the array with the most and least sentiments
    for i in range(len(data)):
        if random.random() < ratio:
            selected.append(prep_vect())
        pass

def make_labeled_points(data, howmany, onlyimportant):

    global idx2word
    if not idx2word:
        idx2word = read_matrices.read_entities()
    topX = -1 * howmany
    created = []

    tot = sum([np.abs(x) for x in data])
    maintopics = np.argpartition(tot, topX)[topX:]
    # now to find the array with the most and least sentiments
    numtopics = len(data[0])

    # Resize data vectors to only include important topics
    if onlyimportant:
        numtopics = len(maintopics)
        importantdata = []
        for d, c in data:
            importantdata.append((fill_new_vector(maintopics, [d[x] for x in maintopics], numtopics)), c)
        data = importantdata

    #Make 1 hot injection vectors
    for i, topic in enumerate(maintopics):
        created.append(prep_vect(topic, -1, numtopics, f'{i}-'))
        created.append(prep_vect(topic, 1, numtopics, f'{i}+'))
        created.append(prep_vect(topic, -.1, numtopics, f'{i}-.'))
        created.append(prep_vect(topic, .1, numtopics, f'{i}+.'))

    return created, data


#  TODO USE  TruncatedSVD to 50 dim. then T-SNE from Scikitlearn


class dim_red:
    def __init__(self):
        self.tsne = TSNE(n_components=2)
        self.svd = TruncatedSVD(n_components=50, n_iter=7, random_state=42)


    def fit_transform(self, matrices, timer):
        print("fitting Truncated SVD on data")
        print(f"{timer.time()}:  fit_transforming...")
        matrices = self.svd.fit_transform(matrices)
        print(f"{timer.time()}:  finished fit_transform")
        print("beginning T-SNE fit")
        matrices = self.tsne.fit_transform(matrices)
        print(f"{timer.time()}:  finished tsne fit transforming")
        return matrices

    def transform(self, matrices, timer):
        print("Transforming Truncated SVD on data")
        print(f"{timer.time()}:  transforming...")
        matrices = self.svd.transform(matrices)
        print(f"{timer.time()}:  finished transform")
        print("beginning T-SNE transform")
        matrices = self.tsne.transform(matrices)
        print(f"{timer.time()}:  finished tsne fit transforming")
        return matrices





class TIME:
    def __init__(self):
        self.start()

    def time(self):
        s = str(round(time.time()-self.t, 0)) + ' sec'
        return s

    def start(self):
        self.t=time.time()

def h():
    return help()

def help():
    print("bypublisher=False, labelcount=13, earlystop=.1, strongopinions=0")


def run(by='article', labelcount=13, earlystop=.1, strongopinions=0, onlyimportant=False):

    if (by is not 'article') and (by is not 'week') and (by is not 'publisher'):
        print(by, type(by))
        raise NameError(f"{by} not understood. Must be 'article', 'week' or 'publisher'.")
    #cm = plt.cm.tab20
    cm = mark()
    T = TIME()
    dataset, maxtopics, names, num_colors = read_matrices.read(by=by, earlystop=earlystop, traintest=False, pad=True, dense=True, strongopinions=strongopinions)
    print(T.time(), "Finished dataset")
    print(len(dataset), 'items')
    colors = [x[1] for x in dataset]
    data = [x[0] for x in dataset]
    datadiv = len(data)
    labelleddata = [] # make_labeled_points(data, labelcount, onlyimportant=onlyimportant)
    data += [x[0] for x in labelleddata]

    dimred = dim_red()
    transformed = dimred.fit_transform(data, T)
    Xs = [x[0] for x in transformed]
    Ys = [x[1] for x in transformed]

    # Prepare the labels at 0,0 so they're invisible:
    for i in names.keys():
        plt.scatter(0 ,0,s=20, color=cm.color(i), marker=cm.marker(i), label=names[i])
    plt.scatter(0,0,s=20, color="white")

    if by is not 'publisher':
        for i in range(len(colors)):
            plt.scatter(Xs[:datadiv][i], Ys[:datadiv][i], s=20, color=cm.color(colors[i]), marker=cm.marker(colors[i]) )

    for i, (x, y) in enumerate(transformed[datadiv:]):
        plt.scatter(x, y, s=10, color='darkgray')
        plt.annotate(labelleddata[i][1][0], (x, y))
        nickname = labelleddata[i][1][0]
        if nickname.endswith('-'):
            print(nickname[:-1]+'+-', ': ', labelleddata[i][1][1])

    # The only difference is to overlay this on TOP of the annotations && BIGGER dots
    if by is 'publisher':
        for i in range(len(colors)):
            plt.scatter(Xs[:datadiv][i], Ys[:datadiv][i], s=50, color=cm.color(colors[i]), marker=cm.marker(colors[i]) )

    print(T.time())
    print("NAMES", names)
    plt.legend()
    # plt.axes().set_facecolor("black")
    plt.show()
    print('ret data with len,', len(data))
    return data, labelleddata

