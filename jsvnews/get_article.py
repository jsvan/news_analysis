from jsvnews.database.code import mydb




def getall():
    db, c = mydb.DB().on_start()
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

