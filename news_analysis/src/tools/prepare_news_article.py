import os
from transformers import BertTokenizer
from googletrans import Translator
translator = Translator()
import langdetect
from news_analysis.src.tools import resolve_NE

tokenizer = BertTokenizer.from_pretrained(os.path.join('lib','ABSA_BERT_MODEL','bert-linear-commonsents-finetune'))   # BertTokenizer.from_pretrained(os.path.join('..', 'ABSA_BERT', 'BERT-E2E-ABSA', "bert-linear-rest15-finetune"))
import re
import string



def get_censor_name(text):
    # just point them out
    return " [[" + text + "]]"



def cleanBody(body):
    body = body.replace('’', '\'').replace('‘', '\'').replace('…', '...')
    body = body.replace('”', '\"').replace('\n',' ')
    body = body.replace('“', '\"').replace(" \'s ", "\'s " )
    body = body.replace('—', '-').replace('–', '-').replace(' ', ' ')
    return body.strip()


MAX_ARTICLE_GROUP = 1000  # Idk but bigger breaks the model ?????

def mask(sentence, df):

    # Model ONLY reads ####Lables part for both data and labels, before #### is for humans
    sentence = cleanBody(sentence)
    if not sentence:
        return ''
    if sentence[-1] not in string.punctuation:
        sentence += '.'
    # find all Named Entities, put them into lab list
    #matches = [m for m in re.finditer('\[\[.+?\]\]', sentence)]
    #NEs = [ x.group().replace(' ', '_') for x in matches]
    #masked = tokenizer.tokenize(sentence.replace("[POS]", "[MASK]").replace("[NEU]", "[MASK]").replace("[NEG]", "[MASK]"))
    if not re.search('\[\[.+?\]\]', sentence):
        return ''
    masked = tokenizer.tokenize(re.sub('\[\[.+?\]\]', '[MASK]', sentence))
    #counter = 0
    labels = []
    try:
        for item in masked:
            labels.append(item+'=O')
    except IndexError:
        print("error with:")
        print(df, sentence)
        return ''
    return sentence + "####" + ' '.join(labels)


def bullshitmask(word):
    return word + "####This=O is=O empty=O .=O"


def fixsentences(thing):
    thing = thing.replace('Ms.', 'Ms').replace('Mr.', 'Mr').replace('Mrs.', 'Mrs').replace('Sen.', 'Senator').replace('Jr.', "Jr").replace('Sr.', 'Sr').replace("U.S.", "United States")
    thing = thing.replace('Jan.', 'January').replace('Feb.', 'February').replace('Mar.', 'March').replace('Apr.', 'April').replace('Aug.', 'Aug').replace("Sept.", 'September').replace("Oct.", "October").replace('Nov.', "November").replace("Dec.", "December")
    for ABC in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ': # get rid of middle initials
        thing = thing.replace(f' {ABC}. ', f' {ABC} ')
    return thing


def convert(art):
    """ input:
        self.scrapedArticle['title'] = title
        self.scrapedArticle['timepublished'] = time
        self.scrapedArticle['url'] = link
        self.scrapedArticle['newspaper'] = link.split('/')[2]
        self.scrapedArticle['article'] = body
    """
    allitems = []
    try:
        body = cleanBody(art['title'] + '. ' + art['article'])
        if langdetect.detect(body) != 'en':
            body = translator.translate(body).text
        body = fixsentences(body)
        body = body.split('. ')
        allitems.append(bullshitmask(f'JSVSRC:  {art["newspaper"]}  {art["url"]}  {art["timepublished"]}'))

        for sentence in body:
            sentence = sentence.strip()
            bodytext, bodymap = resolve_NE.process_article(sentence)
            censored_body = []
            endprevious = 0
            for e, (start, end, text) in enumerate(bodymap):
                if not text:
                    continue
                censored_body.append(
                    ' '.join(bodytext[endprevious:start]) + get_censor_name(text))  # Spaced as "X X X X"
                endprevious = end
            if censored_body:
                censored_body.append(' '.join(bodytext[endprevious:]))
                sentence = ' '.join(censored_body)
                readymasked = mask(sentence, art["url"])

                if readymasked:
                    allitems.append(readymasked)

    except UnicodeEncodeError:
        print("Error with ", art['body'])
    return allitems



  #  We love the pink pony.####we=O love=O the=O pink=T-POS pony=T-POS .=O
  #  We love the [MASK].####we=0 love=0 the=0 [MASK]=T-POS .=0