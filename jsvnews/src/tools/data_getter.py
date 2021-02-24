from jsvnews.src.tools import read_matrices
idx2word, word2idx = read_matrices.read_entities()
from datetime import datetime, timedelta
from matplotlib import pyplot
import numpy as np


class SentByDate:
    """
    Nested dictionaries of sentiments per day per publisher
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
            if (theday.day - 1) % 7 != 0:
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
        self.n2month = {1: 'Jan', 2: 'Feb', 3: 'Mar', 4: 'Apr', 5: 'May', 6: 'Jun',
                        7: 'Jul', 8: 'Aug', 9: 'Sep', 10: 'Oct', 11: 'Nov', 12: 'Dec'}
        self.xticks = []
        self.origin = datetime.today()
        recentest = datetime(1994, 3, 16)
        for pub in dic.keys():
            for dateobj in dic[pub].keys():
                if dateobj < self.origin:
                    self.origin = dateobj
                elif dateobj > recentest:
                    recentest = dateobj
        self.elapseddays = (recentest - self.origin).days + 1

    def prepare_data(self, data):
        """
        offsets the data to fit with the correct date ticks.
        :param data: dictionary of datetime: sentiment score float
        :return: array of size "elapseddays", 1 entry per day. Empty days represented as 0
        """
        # toret = [0] * self.elapseddays
        x, y = [], []
        print(self.elapseddays, "elapsed days")
        sorteddata = list(data.items())
        sorteddata.sort()
        for date, val in sorteddata:
            offset = (date - self.origin).days
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
        # toret = [0] * self.elapseddays
        toret = []
        its = dict()
        print(self.elapseddays, "elapsed days")
        for date, val in data.items():
            offset = (date - self.origin).days
            # print('offset', offset)
            its[offset] = val

        val = 0
        for i in range(self.elapseddays):
            if i in its:
                val = its[i]
            toret.append(val)

        return toret


class DataGetter:
    def __init__(self):
        # Full dataset for all topics, uncombined
        self.DS={}

    def _related_terms(self, plotword):
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


    def _to_avg(self, v):
        return -1*v[0] + v[2]# /  max(sum(v), 10)

    def _filter_for_related(self, dic, related, avg=True):
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
                    sentunit = self._to_avg(runningsum) if avg else runningsum
                    read_matrices.add2dict(toret, [publisher, date], sentunit)
        return toret

    def create_title(self, related_idxs):
        tit = ', '.join(list({idx2word[x] for x in related_idxs}))
        toret = []
        i = 0
        while i < len(tit):
            newi = min(i+250, len(tit))
            toret.append(tit[i:newi])
            i = newi
        return '\n'.join(toret)

    def plot(self, plotter, related_idxs):
        # pyplot.ylim(-1, 1)
        pyplot.axhline(0, color='black')
        pyplot.scatter(0, 0, color='white', s=55)
        myXs, xwhere = plotter.getXTicks()
        pyplot.xticks(xwhere, myXs, rotation=45)
        pyplot.title(self.create_title(related_idxs))
        pyplot.legend()
        pyplot.show()

    def _get_data(self, by, earlystop, strongopinions, reset=False):
        if self.DS and not reset:
            return self.DS
        else:
            # Dataset will be {publisher:{date:dok_matrix}}
            # dok_matrix will be [0x65k] ish
            self.DS = read_matrices.read(by=by, earlystop=earlystop, traintest=0, strongopinions=strongopinions)
            print(len(self.DS), 'publishers')
            for p in self.DS.keys():
                print(f"{p} has {len(self.DS[p])} entries")
        return self.DS

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

    def query_topic(self, plotword, by='week', earlystop=0, strongopinions=0, avg=True, reset=False):
        #This filters the dataset for topics you want and combines all related topics together into one.
        dataset = self._get_data(by, earlystop, strongopinions, reset)
        related_idxs = self._related_terms(plotword)
        dataset = self._filter_for_related(dataset, related_idxs, avg)
        return dataset, related_idxs
        #return SentByDate(dataset)

    def query_topic_SentByDate_type(self, query_topic_output):
        """
        This returns a filtered dataset (query topic), internally buffered so a sentiment array space is given for every day, whether filled or not.
        This is good for plotting sentiment over time graphs where every day deserves a value.
        :param query_topic_output: get a filtered dataset from query topic before converting to SentByDate
        :return: new dic type publisher:date:sentimentscores

        dic example:
        data['abcnews.go.com'][datetime.datetime(2020, 8, 11, 0, 0)].get((0,15))
        # >>> [10, 5, 8]
        """
        return SentByDate(query_topic_output)
