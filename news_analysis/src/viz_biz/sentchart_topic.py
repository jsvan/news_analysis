from src.tools import read_matrices
idx2word, word2idx = read_matrices.read_entities()
from datetime import datetime, timedelta
from matplotlib import pyplot
import numpy as np
from src.viz_biz.plot_design import mark
DS={}

class sentbydate:
    """
    Organize the data to fit into an array of size ELAPSED_DAYS, with empty days represented with a 0 entry.
    """
    def getXTicks(self):
        """
        Provide a name tick for every day in the elapsed time of the dataset.
        If the month or year is a new month or year, it will write the new month or year with the day tick
        :return:
        """
        if self.xticks:
            return self.xticks, self.toshow
        o = self.origin
        self.xticks.append(f"{self.n2month[o.month]} {o.day} {o.year}")
        self.toshow = [0]
        for i in range(1, self.elapseddays):
            theday = self.origin + timedelta(days=i)
            if (theday.day - 1 ) % 7 != 0:
                continue
            self.toshow.append(i)
            thetick = []
            if theday.day == 1:
                thetick.append(str(self.n2month[theday.month]))
            thetick.append(str(theday.day))
            if theday.month == 1 and theday.day == 1:
                thetick.append(str(theday.year))
            self.xticks.append(' '.join(thetick))
        return self.xticks, self.toshow


    def __init__(self, dic):
        """
        Create a data array with length of the total elapsed days in our dataset.
        :param dic: data dictionary of time publisher:date:sentiments
        """
        self.n2month = {1:'Jan', 2:'Feb', 3:'Mar', 4:'Apr', 5:'May', 6:'Jun',
                        7:'Jul', 8:'Aug', 9:'Sep', 10:'Oct', 11:'Nov', 12:'Dec'}
        self.xticks = []
        self.origin = datetime.today()
        recentest = datetime(1994,3,16)
        for pub in dic.keys():
            for dateobj in dic[pub].keys():
                if dateobj < self.origin:
                    self.origin = dateobj
                elif dateobj > recentest:
                    recentest = dateobj
        self.elapseddays = (recentest-self.origin).days + 1

    def prepare_data(self, data):
        """
        offsets the data to fit with the correct date ticks.
        :param data: dictionary of datetime: sentiment score float
        :return: array of size "elapseddays", 1 entry per day. Empty days represented as 0
        """
        #toret = [0] * self.elapseddays
        x, y = [], []
        print(self.elapseddays, "elapsed days")
        sorteddata = list(data.items())
        sorteddata.sort()
        for date, val in sorteddata:
            offset = (date-self.origin).days
            if x and offset - x[-1] > 1:
                x.append(np.nan)
                y.append(np.nan)
            x.append(offset)
            y.append(val)
        return x, y

    def prepare_data_continue_na(self, data):
        """
        offsets the data to fit with the correct date ticks.
        :param data: dictionary of datetime: sentiment score float
        :return: array of size "elapseddays", 1 entry per day. Empty days represented as 0
        """
        #toret = [0] * self.elapseddays
        toret = []
        its = dict()
        print(self.elapseddays, "elapsed days")
        for date, val in data.items():
            offset = (date-self.origin).days
            #print('offset', offset)
            its[offset] = val

        val = 0
        for i in range(self.elapseddays):
            if i in its:
                val = its[i]
            toret.append(val)

        return toret


def related_terms(plotword):
    """
    :param plotword: search word, like "Trump"
    :return: List of all indices of related terms.
    """
    plotword = plotword.lower()
    related = [] #word2idx[plotword]
    for word in word2idx.keys():
        if plotword in word.lower():
            related += word2idx[word]
    return related


def to_avg(v):
    return -1*v[0] + v[2]# /  max(sum(v), 10)


def filter_for_related(dic, related):
    """
    Reduces entries from the dataset to only those entries dealing with topics x, y or z.
    :param dic: the dataset dic type publisher:date:sentimentscores
    :param related: list of indexes to filter by
    :return: new dic type publisher:date:sentimentscores

    dic example:
    data['abcnews.go.com'][datetime.datetime(2020, 8, 11, 0, 0)].get((0,15))
    #>>> [10, 5, 8]
    """
    toret = dict()
    #read_matrices_as_dict.add2dict(toret, [keys], val)
    for publisher in dic.keys():
        for date in dic[publisher].keys():
            matrix = dic[publisher][date]
            runningsum = [0,0,0]
            for idx in related:
                for i in range(len(runningsum)):
                    try:
                        runningsum[i] += matrix[(0, idx)][i]
                    except KeyError:
                        continue
            if sum(runningsum) > 0:
                read_matrices.add2dict(toret, [publisher, date], to_avg(runningsum))
    return toret

def create_title(related_idxs):
    tit = ', '.join(list({idx2word[x] for x in related_idxs}))
    toret = []
    i = 0
    while i < len(tit):
        newi = min(i+250, len(tit))
        toret.append(tit[i:newi])
        i = newi
    return '\n'.join(toret)


def get_data(by, earlystop, strongopinions):
    global DS
    if DS:
        return DS
    else:
        # Dataset will be {publisher:{date:dok_matrix}}
        # dok_matrix will be [0x65k] ish
        DS = read_matrices.read(by=by, earlystop=earlystop, traintest=0, strongopinions=strongopinions)
        print(len(DS), 'publishers')
        for p in DS.keys():
            print(f"{p} has {len(DS[p])} entries")
    return DS

def plot(plotter, related_idxs):
    #pyplot.ylim(-1, 1)
    pyplot.axhline(0, color='black')
    pyplot.scatter(0, 0, color='white', s=55)
    myXs, xwhere = plotter.getXTicks()
    pyplot.xticks(xwhere, myXs, rotation=45)
    pyplot.title(create_title(related_idxs))
    pyplot.legend()
    pyplot.show()

"""
https://meduza.io/rss/en/all
https://foreignpolicy.com/feed/
http://webfeeds.brookings.edu/brookingsrss/topfeeds/latestfrombrookings?format=xml
http://rssfeeds.usatoday.com/usatoday-NewsTopStories
https://www.businessinsider.com/rss
https://www.nationalreview.com/feed/
http://feeds.foxnews.com/foxnews/latest
http://rss.nytimes.com/services/xml/rss/nyt/Politics.xml
http://rss.nytimes.com/services/xml/rss/nyt/US.xml
http://feeds.washingtonpost.com/rss/politics
https://abcnews.go.com/abcnews/topstories
http://feeds.foxnews.com/foxnews/politics
https://abcnews.go.com/abcnews/politicsheadlines
https://www.rt.com/rss/
http://english.sina.com/rss/scroll.xml
http://news.ifeng.com/rss/
https://www.oann.com/feed
https://www.theatlantic.com/feed/all/
https://www.theamericanconservative.com/articles/feed/
https://www.theepochtimes.com/feed/
"""

conservative= {"www.nationalreview.com", "feeds.foxnews.com", "www.foxnews.com", "www.oann.com", "www.rt.com", "english.sina.com"}
liberal = {"rssfeeds.usatoday.com", "webfeeds.brookings.edu", "www.businessinsider.com", "www.nytimes.com", "www.washingtonpost.com", "abcnews.go.com", "www.theatlantic.com" }
forpol = {"meduza.io", "foreignpolicy.com", "news.ifeng.com","www.theepochtimes.com", "webfeeds.brookings.edu"}
groups = [conservative, liberal, forpol]
M = mark()
def run(plotword, by='week', earlystop=0, strongopinions=0):
    dataset = get_data(by, earlystop, strongopinions)
    related_idxs = related_terms(plotword)
    dataset = filter_for_related(dataset, related_idxs)
    plotter = sentbydate(dataset)
    #for group in groups:
    if True:
        for i, publisher in enumerate(dataset):
            pyplot.scatter(0, 0, color=M.color(i), marker=M.marker(i), s=50, label=publisher)
            #if publisher not in group:
            #    continue
            x, y = plotter.prepare_data(dataset[publisher])
            pyplot.plot(x, y, color=M.color(i))
            pyplot.scatter(x, y, color=M.color(i), marker=M.marker(i), s=5)
        plot(plotter, related_idxs)


    return dataset
    # FOr each publisher
    # Prepare the data into an array of sentiments

    # pyplot.axes().set_xticklabels([dates to label])
    #for publisher in dataset.keys():
