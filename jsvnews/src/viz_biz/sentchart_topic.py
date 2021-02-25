from jsvnews.src.viz_biz.plot_design import mark
from jsvnews.src import data_getter
from matplotlib import pyplot

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
mygetter = data_getter.DataGetter()
def run(plotword, by='week', earlystop=0, strongopinions=0, saveto=''):
    dataset, names = mygetter.query_topic(plotword,by,earlystop,strongopinions)
    plotter = data_getter.SentByDate(dataset)
    #for group in groups:
    if True:
        for i, publisher in enumerate(dataset):
            pyplot.scatter(0, 0, color=M.color(i), marker=M.marker(i), s=50, label=publisher)
            #if publisher not in group:
            #    continue
            x, y = plotter.prepare_data(dataset[publisher])
            pyplot.plot(x, y, color=M.color(i))
            pyplot.scatter(x, y, color=M.color(i), marker=M.marker(i), s=5)

        mygetter.plot(plotter, plotword, saveto)
    return dataset, names
    # FOr each publisher
    # Prepare the data into an array of sentiments

    # pyplot.axes().set_xticklabels([dates to label])
    #for publisher in dataset.keys():
