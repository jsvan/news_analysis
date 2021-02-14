from src.tools import read_matrices
DAYS_IN_WEEK = 7
HISTORICAL_WINDOW = 6 * DAYS_IN_WEEK  # 6 weeks
"""
Use a sliding window of let's say 6 weeks, see if the sentiments of new week is out of ordinary.

"""
def analyze_publisher_landscape(topic_data):



def analyze_one_publisher(topic_data):
    """
    Performs sliding window analysis over a single publisher to see if they begin discussing topics in a new way
    :param topic_data:
    :return:
    """


def filter_for_topics(topicidxs, data):
    topicdata = dict()
    for publisher in data.keys():
        for day in data[publisher].keys():
            mat = data[publisher][day]
            assert mat.X == 1
            sents = [0,0,0]
            for topic in topicidxs:
                v = mat[0, topic]
                sents = mat.add_triple(sents, v)
            read_matrices.add2dict(topicdata, [publisher, day], sents)
    return topicdata


def analyze_topic(topicidxs, alldata):
    topicdata = filter_for_topics(topicidxs, alldata)



def run():
    data = read_matrices.read(by='day')
    idx2w, w2idx = read_matrices.read_entities()
    for topic, topicidxs in w2idx.items():
        result = analyze_topic(topicidxs, data)
