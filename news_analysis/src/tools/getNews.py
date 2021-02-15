from readability import Document
import requests
import re
import feedparser


from news_analysis.database.code import mydb




def fromdb(databasename):
    db, c = mydb.DB(databasename).on_start()
    query = "SELECT * FROM newspaper_tbl;"
    newspapers = {x:y for x, y in c.execute(query).fetchall()}
    query = "SELECT * FROM article_tbl;"
    print(query)
    print(""" title
            timepublished
            newspaper
            url
            article""")
    articles = c.execute(query)
    for art in articles:
        # yield art
        yield {'title':art[1], 'timepublished':art[2], 'newspaper':newspapers[art[3]], 'url':art[4], 'article':art[5]}




class Scraper:
    def cleanBody(self, body):
        body = body.replace('</p>', '\n')
        body = re.sub(r'<.*?>','',body)
        body = body.replace('[', '')
        body = body.replace(']', '')
        body = body.replace('’', '\'')
        body = body.replace('”', '\"')
        body = body.replace('“', '\"')
        body = '\n'.join(self.testJunkSentence(s) for s in body.split('\n'))
        body = re.sub(r'\n+', '\n', body)
        body = re.sub(r'  +', ' ', body)
        return body.strip()

    def testJunkSentence(self, s):
        s=s.strip()
        if not s:
            return ''
        if not s:
            return ''
        if s[-1] != '.':
            return ''
        sentence = s.replace(' ', '')
        length = len(sentence)
        caps = sum(1 for x in sentence if x.isupper())
        alpha = sum(1 for x in sentence if x.isalpha() or x.isdigit())
        if caps >= length/2:
            return ''
        if alpha <length/2:
            return ''
        return s

    def __init__(self):
        self.scrapedArticle=dict()
        self.scrapedArticle['title'] = ''
        self.scrapedArticle['timepublished'] = ''
        self.scrapedArticle['url'] = ''
        self.scrapedArticle['newspaper'] = ''
        self.scrapedArticle['article'] = ''

    def scrape(self, rssfeedlist):
        with open(rssfeedlist, 'r') as RSSs:
            for rss in RSSs:
                count = 0
                #print("\nCollecting from", rss)
                for entry in feedparser.parse(rss).entries:
                    try:
                        #if count > 0: # return just 1
                        #    break
                        count +=1
                        #print('\r', count, end='')
                        link = entry.link
                        title = entry.title
                        time = entry.published
                        #print(Document(requests.get(link).text))

                        body = self.cleanBody(Document(requests.get(link).text).summary())
                        self.scrapedArticle['title'] = title
                        self.scrapedArticle['timepublished'] = time
                        self.scrapedArticle['url'] = link
                        self.scrapedArticle['newspaper'] = link.split('/')[2]
                        self.scrapedArticle['article'] = body
                        if body:
                            #print(body[:15])
                            yield self.scrapedArticle
                    except ConnectionError as E:
                        print(E, E.__doc__)
                        continue