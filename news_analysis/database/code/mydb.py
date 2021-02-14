import sqlite3
import os

print(os.listdir('./'))

NEWSPAPER_CMD = '''INSERT OR IGNORE INTO newspaper_tbl VALUES(NULL, ?);'''
ARTICLE_CMD = '''INSERT OR IGNORE INTO article_tbl VALUES(NULL,?,?,?,?,?);'''
REPLACE_ARTICLE_CMD = '''REPLACE INTO article_tbl VALUES(NULL,?,?,?,?,?);'''

class DB:
    newspaper_TBL = "newspaper_tbl"

    def __init__(self, databasename='articles.db'):
        self.databasename = databasename
        self.db, self.cursor = self.on_start()
        self.newspapers = dict()
        r = self.cursor.execute('''SELECT * FROM newspaper_tbl''')
        for content in r.fetchall():
            id, name = content
            self.newspapers[name] = id

    def on_end(self):
        try:
            self.db.commit()
            try:
                z = self.cursor.execute("SELECT COUNT(*) FROM article_tbl;")
                for i in z.fetchall():
                    print("We have", i[0], "articles!")
            except sqlite3.ProgrammingError:
                pass
            print("Disconnecting")
            self.db.close()
        except sqlite3.OperationalError as E:
            print(E)

    def on_start(self):
        self.db = sqlite3.connect(f'./database/dbs/{self.databasename}')
        self.cursor = self.db.cursor()
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS article_tbl(
            id                        INTEGER PRIMARY KEY,
            title                     STRING,
            timepublished             STRING,
            websitename               STRING,
            websiteurl                STRING UNIQUE,
            text                      STRING,
            FOREIGN KEY(websitename)  REFERENCES newspaper_tbl(id),
            CONSTRAINT whatever UNIQUE (websitename, title)
    );''')
        self.cursor.execute('''
        CREATE TABLE IF NOT EXISTS newspaper_tbl(
            id                      INTEGER PRIMARY KEY,
            name                    STRING UNIQUE
    );''')
        return self.db, self.cursor

    def add_article(self, prey, command=ARTICLE_CMD):
        if not prey['article']:
            return
        print(prey['newspaper'], prey['title'])
        if prey['newspaper'] not in self.newspapers:
            self.cursor.execute(NEWSPAPER_CMD, (prey['newspaper'],))
            r = self.cursor.execute('''SELECT id FROM newspaper_tbl WHERE name IS ?;''', (prey['newspaper'],))
            for i in r.fetchall():
                self.newspapers[prey['newspaper']] = i[0]

        self.cursor.execute(command, (
        prey['title'], prey['timepublished'], self.newspapers[prey['newspaper']], prey['url'], prey['article']))
