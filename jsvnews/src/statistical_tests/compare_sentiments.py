#for i in outs[1]:
#    print(i)
from matplotlib import pyplot as PP
import sys
import numpy as np
print("You are using Python {}.{}.".format(sys.version_info.major, sys.version_info.minor))
from scipy import stats
np.random.seed(12345678)

def demean(x, m, sd):
    return (x-m)/sd


def get_matrices():
    import jsvnews.src.tools.read_matrices

"""
0.2       [[California]]                                    [1, 0, 0, 0, 0]
0         [[Capitol Hill]]                                  [0, 0, 0, 0, 0]
['0.2       ', '', 'California]]                         ', '1, 0, 0, 0, 0]']
"""
def run(name):
    papers = dict()
    C = 5

    name = 'Biden'.lower()
    #NAME = 'Affordable Care Act'.lower()

    related_names = set()
    related_names.add(name)
    allscores = []
    for item in outs:
        if len(item) < 4:
            continue

        source = item[0][8:]
        if source not in papers:
            papers[source] = dict()
        time = item[1]
        score = item.index('SCORES:') + 1
        for sent in item[score:]:
            parts = sent.split('[')
            if not parts[0]:
                continue
            # Parts: Avg, Name, scores(list)
            # print(parts)
            # print(parts[0].strip())
            javg = float(parts[0].strip())
            NE = parts[2].strip()[:-2].lower()
            scores = [int(x) for x in parts[3][:-1].split(', ')]
            allscores += scores
            if name in NE:
                related_names.add(NE)
            # if NE == 'Republican':
            #    NE = 'Republican Party (United States)'
            if NE not in papers[source]:
                papers[source][NE] = [[],[]]
            papers[source][NE][0].append(javg)
            papers[source][NE][1].append(scores)

    related_names = list(related_names)
    Ms = ['.',',','o','v','^','1','2','3','4','s','p','P','*','h','+','x','X','d','|','_']


    # the histogram of the data
    # add a 'best fit' line
    from scipy.stats import norm
    from statistics import mean, stdev
    # import matplotlib.mlab as mlab
    import random
    pkeys = list(papers.keys())
    random.shuffle(pkeys)
    topic_scores=[]
    for i, src in enumerate(pkeys):
        for rn in related_names:
            if rn not in papers[src]:
                continue
            for fitchunk in papers[src][rn][1]:
                topic_scores += fitchunk
    m = mean(allscores)
    sd = stdev(allscores)
    #print('mean', m)
    #print(allscores[:100])
    allscores = [demean(x, m, sd) for x in allscores]

    #print(allscores[:100])
    for i, src in enumerate(pkeys):
        fig, ax = PP.subplots()
        toplot, tofitline = [], []
        for rn in related_names:
            if rn not in papers[src]:
                continue
            toplot += papers[src][rn][0]
            for fitchunk in papers[src][rn][1]:
                tofitline += fitchunk
        if not toplot:
            continue
        if not tofitline:
            continue

        (mu, sigma) = norm.fit(tofitline)
        if sigma < 0.000001:
            continue
        tofitline = [demean(x, m, sd) for x in tofitline]
        ax.hist(allscores, 20, label='all scores'.format(len(tofitline)), align='mid' , density=False, weights=np.ones(len(allscores)) / len(allscores))
        ax.hist(tofitline, 20, align='left', label='pure trinary mentions ({})'.format(len(tofitline)) , density=False, weights=np.ones(len(tofitline)) / len(tofitline))
        n, bins, patches = ax.hist(toplot, 20, align='right',  label='avg article scores ({})'.format(len(toplot)) ,  density=False, weights=np.ones(len(toplot)) / len(toplot))  # ,density=True, weights=np.ones(len(toplot)) / len(toplot), label=src)

        y = norm.pdf(np.linspace(-1, 1, 21), mu, sigma)  #
        ax.plot(np.linspace(-1, 1, 21), y, marker=Ms[i%len(Ms)], label='gauss over mentions')

        # Get topic sentiment line
        (mu, sigma) = norm.fit(topic_scores)
        y = norm.pdf(np.linspace(-1, 1, 21), mu, sigma)  #
        ax.plot(np.linspace(-1, 1, 21), y, label='gauss over all newspapers on topic, NEUTRAL for topic ({})'.format(len(topic_scores)))

        # Get total sentiment line
        (mu, sigma) = norm.fit(allscores)
        y = norm.pdf(np.linspace(-1, 1, 21), mu, sigma)  #
        ax.plot(np.linspace(-1, 1, 21), y, label='gauss over all scores, NEUTRAL for journalism ({})'.format(len(allscores)))
        # Indented
        ax.plot([0,0],[0,1], label='NEUTRAL', color='black')
        PP.xlim([-1, 1])
        ttres = stats.ttest_ind(tofitline, allscores, equal_var=False)
        ttres_top = stats.ttest_ind(tofitline, topic_scores, equal_var=False)

        PP.title('All things {}  {}\nMedia tstat: {:.8f}   pval: {:.8f}\nTopic tstat: {:.8f}   pval: {:.8f}'.format(name, src, ttres[0], ttres[1], ttres_top[0], ttres_top[1]))   # +"\n".join(      [', '.join(related_names[i * C:(i + 1) * C]) for i in range((len(related_names) + C - 1) // C )]     ))
        ax.legend()
        PP.show()
# PP.show()

