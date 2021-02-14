import random
import numpy as np
from scipy.sparse import dok_matrix
from datetime import datetime
import os

def get_week_mask(list_matrix_fps, targetdate):
    """
    Takes list of date pkl filenames as input, returns a list of if those dates are within 1 week of the target.
    :param list_matrix_fps: ['2020-08-12.pkl', '2020-09-25.pkl', etc.]
    :param targetdate: '2020-08-25.pkl'
    :return: [0,0,0,0,1,1,1,1,1,1,0,0,0,0,0,0,0 etc.]
    """
    def datetodatetime(date):
        """
        :param date: '2020-08-25.pkl'
        :return: datetime object
        """
        year, month, day = date.split('-')
        year, month, day = int(year), int(month), int(day[:-4])
        return datetime(year, month, day)
    def fp2fname(p):
        return p.split(os.path.sep)[-1]
    targ = datetodatetime(fp2fname(targetdate))
    toret = [abs((targ - datetodatetime(fp2fname(fp))).days) < 4 for fp in list_matrix_fps]
    return toret


def read(shuffle=True, traintest=False, topicscount=True, nameslist=True, totalcolorcount=True, dense=False, pad=False, earlystop=.1, by="article", strongopinions=0, date=False):
    if by != 'article' and by != 'week' and by != 'publisher':
        raise NameError(f"{by} not understood. Must be 'article', 'week' or 'publisher'.")
    print('reading data')
    from src.tools.sparse_matrix import jsv_dictmat
    import os
    names = {}
    colorspre, data = [], []
    maxtopics = 0
    matrix_folders = os.path.join('data', 'matrices')
    matrix_files = []
    color = -1
    all_companies_folders = os.listdir(matrix_folders)
    """
    Collect file paths:
        If by article: Make a list of all matrices to load 
        else: Make a list of companies (lists) of all the matrices.
    """
    for mf in all_companies_folders:
        if by is not 'article':
            matrix_files.append([])
        company_folder = os.path.join(matrix_folders, mf)
        color += 1
        names[color] = mf
        this_companys_folder = os.listdir(company_folder)
        for i, m in enumerate(this_companys_folder):
            if earlystop and (i/len(this_companys_folder)) > earlystop:
                break
            if by is not 'article':
                matrix_files[color].append(os.path.join(company_folder, m))
            else:
                matrix_files.append(os.path.join(company_folder, m))
                colorspre.append(color)
    """
    Produce sparse numpy matrices
    If article, enumerates all articles
    If publisher, enumerates publisher lists of articles
    
    """
    print(f"Should have {len(matrix_files) if by is not 'article' else sum([len(m) for m in matrix_files])} matrices...")
    for ii, matpath in enumerate(matrix_files):
        print(ii, end='\r')
        if by is 'publisher':
            """
            Make one main matrix, and add to it all the other matrices in the publisher list
            Many to 1. Many articles in, one matrix out.
            """
            mat = jsv_dictmat()
            for daymat in matpath:
                nextmat = jsv_dictmat(daymat)
                mat.update(nextmat, appendmode=True)
            mat = mat.collapse_into_day_vector()
            mat = compress_dok_matrix(mat.to_avg_scipy(strongopinions))  # articlewise, should be #articles x #topics
            if not sum(mat.get_shape()):
                continue
            mats = [mat]
        elif by is 'week':
            """
            top loop: 
                    For all in company folder
            this loop:
                    For all days in company folder, collect their week's data. 
            Many to many.
            """
            mats = []
            for daymat in matpath:  # the path to matrix.pkl, limited to earlystop as built above.
                # IE works on all of ABCnews matrices
                mat = jsv_dictmat()
                mask = get_week_mask(matpath, daymat)
                for i in range(len(matpath)):
                    if mask[i]:
                        mat.update(jsv_dictmat(matpath[i]).collapse_into_day_vector())
                #print(mat)
                #mat = mat.collapse_into_week_vector()
                mat = compress_dok_matrix(mat.to_avg_scipy(strongopinions))  # articlewise, should be #articles x #topics
                if not sum(mat.get_shape()):
                    continue
                mats.append(mat)
        else:  # by is 'article'
            """
            1 to 1. One article in, one matrix out
            """
            mat = jsv_dictmat(matpath)
            mat = compress_dok_matrix(mat.collapse_into_day_vector().to_avg_scipy(strongopinions))  # articlewise, should be #articles x #topics
            if not sum(mat.get_shape()):
                continue
            mats = [mat]

        for mat in mats:
            kys = {x[0] for x in mat.keys()}  # getting all articlenums
            vls = [mat[k] for k in kys]
            #print('keys:\n',kys)
            #input('vales:')
            #print(vls)
            #input()
            for v in vls:
                maxtop = v.shape[1]  #  article#, topics
                if maxtop > maxtopics:
                    maxtopics = maxtop
                #print(f"appending {v}, {ii}, {colorspre[ii] if ii < len(colorspre) else '-'}")
                if by is not 'article':
                    data.append([v, ii])
                else:
                    data.append([v, colorspre[ii]])
                #input()
    if pad or dense:
        for d in data:
            d[0] = d[0].todense().A1  # convert 1xtop matrix to array
            if pad:
                pad_len = maxtopics - d[0].shape[0]
                d[0] = np.concatenate((d[0], [0] * pad_len))
    if shuffle:
        random.seed(42)
        random.shuffle(data)
    if traintest:
        splitpoint = round(len(data)*0.8)
    print('done reading matrices into memory (from read_matrices.py)!')
    print(names)

    toret = []
    if traintest:
        toret.append({'train': data[ :splitpoint], 'test': data[splitpoint: ]})
    else:
        toret.append(data)
    if topicscount:
        toret.append(maxtopics)
    if nameslist:
        toret.append(names)
    if totalcolorcount:
        toret.append(color + 1)
    print(f"Presenting {len(toret[0])} matrices")
    return toret


def compress_dok_matrix(matrix):
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
    with open("words2resolved.txt", encoding='utf-8') as F:
        idx2NE = {i: ' '.join(x.split(' ')[1:]) for i, x in enumerate(F.read().split('\n')[:-1])}
    return idx2NE