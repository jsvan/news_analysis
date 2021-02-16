import random
import numpy as np
from scipy.sparse import dok_matrix
from datetime import datetime
import os
from jsvnews.src.tools.sparse_matrix import jsv_dictmat


def path2datetime(datepaththing):
    """
    This takes our full matrix paths data/matrices/abcnews.go.com/2020-09-06.pkl and returns a datetime of (2020, 9, 6)
    :param datepaththing: matrix pkl path
    :return: datetime object
    """
    #Take the last segment of path, date is '2020-08-25.pkl'
    date = datepaththing.split(os.path.sep)[-1]
    year, month, day = date.split('-')
    year, month, day = int(year), int(month), int(day[:-4])
    return datetime(year, month, day)


def get_week_mask(list_matrix_fps, targetdate):
    """
    Takes list of date pkl filenames as input, returns a list of if those dates are within 1 week of the target.
    :param list_matrix_fps: ['2020-08-12.pkl', '2020-09-25.pkl', etc.]
    :param targetdate: '2020-08-25.pkl'
    :return: [0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0 etc.]
    """
    def withinweek(today, other):
        # today should be bigger than other by up to 7 days
        return 0 <= (today - other).days < 7


    # TODO Make this so instead of day in middle of week, it's day at end of week.
    toret = [withinweek(targetdate, fp) for fp in list_matrix_fps]
    return toret


def byday(dic, strongopinions, traintest):
    """

    :param dic: the dictionary of publisher: date: matrix
    :param strongopinions: exclude items with fewer than n mentions
    :param traintest: Proportion of data to be in "test set"
    :return:
    """
    inflateddata = {}
    if traintest:
        test = {}
    for pub in dic.keys():
        for date in dic[pub].keys():
            adddict = test if traintest and random.random() < traintest else inflateddata
            todaysmatrix = dic[pub][date]
            todaysmatrix = todaysmatrix.collapse_into_day_vector()
            add2dict(adddict,
                     [pub, date],
                     todaysmatrix)
    if traintest:
        return inflateddata, test
    return inflateddata


def byweek(dic, strongopinions, traintest):
    inflateddata = {}
    if traintest:
        test = {}
    for pub in dic.keys():
        for today in dic[pub].keys():
            adddict = test if traintest and random.random() < traintest else inflateddata
            todaysmatrix = jsv_dictmat()
            otherdays = list(dic[pub].keys())
            mask = get_week_mask(otherdays, today)
            daysinmask = sum(mask)
            if daysinmask == 0:
                print(today)
                for ji in range(len(mask)):
                    print(otherdays[ji], mask[ji])
                input()
            for i, othday in enumerate(dic[pub].values()):
                if mask[i]:
                    todaysmatrix.update(othday)
            # THIS AVERAGES OUT THE MENTION COUNTS BY THE NUMBER OF DAYS,
            # SO THAT WE DON'T MISINTERPRET BLANK DAYS AS NON-SENTIMENT DAYS
            todaysmatrix = todaysmatrix.collapse_into_day_vector() / daysinmask
            add2dict(adddict,
                     [pub, today],
                     todaysmatrix)
    if traintest:
        return inflateddata, test
    return inflateddata


def bypublisher(dic, strongopinions, traintest):
    inflateddata = {}
    if traintest:
        test = {}
    for pub in dic.keys():
        adddict = test if traintest and random.random() < traintest else inflateddata
        pubmatrix = jsv_dictmat()
        for today in dic[pub].keys():
            pubmatrix.update(dic[pub][today])
        #DELETING compress_dok_matrix
        #DELETING to_avg_scipy
        pubmatrix = pubmatrix.collapse_into_day_vector()
        add2dict(adddict,
                 [pub],
                 pubmatrix)
    if traintest:
        return inflateddata, test
    return inflateddata


def add2dict(dic, keys, val, replace=True):
    """
    :param dic: {publisher: {day: (1,2,3), etc.}, etc.}
    :param keys: type list
    :param val: jsv_dictmat or (real, real, real)
    :param replace: dictioanry val item replaces or trinary added
    :return:
    """
    thiskey = keys[0]
    nextkeys = keys[1:]
    if thiskey not in dic:
        dic[thiskey] = dict() if nextkeys else val
        return
    if nextkeys:
        add2dict(dic[thiskey], nextkeys, val)
    elif not replace:
        # no more keys, need to add value, but value already in dict
        if isinstance(val, jsv_dictmat):
            dic[thiskey].update(val)
        elif isinstance(val, tuple):
            dic[thiskey] = jsv_dictmat.add_triple(None, dic[thiskey], val) #1st argument is filler for 'self', doesn't matter
        else:
            raise Exception(f"Error, expected tuple or jsv_dictmat, received {type(val)}")




def read(traintest=0, earlystop=.1, by="week", strongopinions=0):
    if by != 'day' and by != 'week' and by != 'publisher':
        raise NameError(f"{by} not understood. Must be 'day', 'week' or 'publisher'.")
    print('reading data')
    names, data = {}, {}
    matrix_folders = os.path.join('data', 'matrices')
    all_companies_folders = os.listdir(matrix_folders)
    """
                Collect file paths:
                    If by article: Make a list of all matrices to load 
                    else: Make a list of companies (lists) of all the matrices.
    """
    for mf in all_companies_folders:
        company_folder = os.path.join(matrix_folders, mf)
        this_companys_folder = os.listdir(company_folder)
        for i, m in enumerate(this_companys_folder):
            if earlystop and (i/len(this_companys_folder)) > earlystop:
                break
            add2dict(data, [mf, path2datetime(m)], jsv_dictmat(os.path.join(company_folder, m)))

    if by is 'day':
        return byday(data, strongopinions, traintest)
    if by is 'week':
        return byweek(data, strongopinions, traintest)
    if by is 'publisher':
        return bypublisher(data, strongopinions, traintest)


def compress_dok_matrix(matrix):
    """
    Brings all articles to counts 0-N, and sets the dense matrix's dimensions to be this reduced value.
    :param matrix:
    :return:
    """
    newd = {}
    prevk = -1
    nextk = -1
    for i, (k, v) in enumerate(matrix.items()):
        articlek, topic = k
        if articlek != prevk:
            prevk = articlek
            nextk += 1
        newd[nextk, topic] = v
    if not newd:
        return dok_matrix((0,0))
    newdokmat = dok_matrix((max(newd.keys())[0] + 1, matrix.get_shape()[1]))
    newdokmat.dtype = np.dtype('float32')
    for k, v in newd.items():
        newdokmat[k] = v
    return newdokmat

def read_entities():
    """
    Reads the file which is of form:
        SEEN_WORD what this word maps to
    In NE2idx I make a list of indeces bc there can be multiple names that map to the same name.
    :return: (idx2NE, NE2idx), two dicts
    """
    with open("words2resolved.txt", encoding='utf-8') as F:
        idx2NE = {i: ' '.join(x.split(' ')[1:]).lower() for i, x in enumerate(F.read().split('\n')[:-1])}

    with open("words2resolved.txt", encoding='utf-8') as F:
        NE2idx = {}
        for i, x in enumerate(F.read().split('\n')[:-1]):
            word = ' '.join(x.split(' ')[1:]).lower()
            if word not in NE2idx:
                NE2idx[word] = []
            NE2idx[word].append(i)
    return idx2NE, NE2idx


def combine_same_words_into_triples(data, strongopinions, NE2idx=None):
    """

    :param data:
    :return: dictionary of dictionaries where items with idxs corresponding to the same word have been combined.
    """
    if not NE2idx:
        _, NE2idx = read_entities()
    comboform = dict()
    for word, idxs in NE2idx.items():
        for i in idxs:
            comboform[i] = idxs[0]
    newdata = dict()
    for pub in data.keys():
        for day in data[pub].keys():
            for (_, idx) in data[pub][day].keys():
                v = data[pub][day][0, idx]
                if sum(v) > strongopinions:
                    add2dict(newdata, [pub, day, idx], v, replace=False)
    return newdata


def read_as_csv(by='day', earlystop=0, strongopinions=0, asString=True):
    def stringify(items, asString):
        if asString:
            return '\t'.join([str(x) for x in items])
        return items
    idx2NE, NE2idx = read_entities()
    data = read(earlystop=earlystop, by=by)
    unique_triples_dd = combine_same_words_into_triples(data, strongopinions, NE2idx)
    csv = [stringify(["group", "publisher", "date", "topicid", "topic", "neg", "neu", "pos"], asString)]
    i = 0
    for pub in unique_triples_dd.keys():
        for day in unique_triples_dd[pub].keys():
            i += 1
            for idx in unique_triples_dd[pub][day].keys():
                v = unique_triples_dd[pub][day][idx]
                csv.append(stringify([i, pub, day, idx, idx2NE[idx], v[0], v[1], v[2]], asString))
    if asString:
        return '\n'.join(csv)
    return csv