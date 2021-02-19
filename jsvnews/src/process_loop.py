from jsvnews.src.tools import getNews
from jsvnews.database import mydb
from os import path
from jsvnews.src.tools import prepare_news_article

class WF:
    """
    For future, BERT can only take an input of < 1000 articles, so may need to make multiple input files to remain
    within that limit. I think it should be fine for now without it............... cross your fingers.
    """
    def __init__(self, out_dir):
        self.out_dir = out_dir
        self.file = open(path.join(self.out_dir, '0.txt'), 'w')

    def generate(self):
        counter = 0
        while True:
            self.close()
            counter += 1
            self.file = open(path.join(self.out_dir, f'{counter}.txt'), 'w')
            yield self.file

    def close(self):  # actually unnecessary but oh well
        self.file.close()



def run(out_file, feedlist, fromdatabase=''):
    """

    :param out_file:
    :param feedlist: rssfeeds
    :param fromdatabase: if articles to come from webscrape, leave blank
    :return:
    """
    ARTICLE_LINE_LIMIT = 1500
    cnt = 0
    db = mydb.DB()
    if not fromdatabase:
        print("scraping")
        scrapedArticles = getNews.Scraper().scrape(feedlist)  # generator
    else:
        print(f"Getting from database {fromdatabase}")
        scrapedArticles = getNews.fromdb(fromdatabase)
    # filegen = WF(out_dir).generate()
    # outfile = filegen.__next__()
    towrite = []
    try:
        for i in scrapedArticles:
            try:
                db.add_article(i)
            except KeyboardInterrupt as e:
                print("ENDING")
                db.on_end()
                print(e, e.__doc__)
            except Exception as e:
                print(e, e.__doc__)

            try:
                towrite.extend(prepare_news_article.convert(i))
                if len(towrite) > ARTICLE_LINE_LIMIT:
                    with open(path.join(out_file, f'{cnt}.txt'), 'w', encoding='utf-8') as F:
                        F.write('\n'.join(towrite))
                    cnt += 1
                    towrite.clear()
            except Exception as e:
                #continue
                print(e, e.__doc__)

        print("ENDING")
        db.on_end()
        with open(path.join(out_file, f'{cnt}.txt'), 'w', encoding='utf-8') as F:
            F.write('\n'.join(towrite))
        cnt += 1

    except KeyboardInterrupt as e:
        print("ENDING")
        db.on_end()
        print(e, e.__doc__)





"""
:::::ScrapedArticles Outlay:::::
self.scrapedArticle['title'] = title
self.scrapedArticle['timepublished'] = time
self.scrapedArticle['url'] = link
self.scrapedArticle['newspaper'] = link.split('/')[2]
self.scrapedArticle['article'] = body
"""
# TODO Need to put sentences into massive file max length 10,000 lines long, new articles start with tag
# TODO tag IDK words #### This=O is=O nothing=O .=O
# TODO and we need that buffer for timepublished, url, newspaper==(dest_folder)
# TODO title should be prepended onto article.