import os
from transformers import BertTokenizer
tokenizer = BertTokenizer.from_pretrained(os.path.join('..', 'ABSA_BERT', 'BERT-E2E-ABSA', "bert-linear-rest15-finetune"))
import random
import re
import string
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
    thing = thing.replace('Ms.', 'Ms').replace('Mr.', 'Mr').replace('Mrs.', 'Mrs').replace('Sen.', 'Senator').replace('Jr.', "Jr").replace('Sr.', 'Sr')
    thing = thing.replace('Jan.', 'January').replace('Feb.', 'February').replace('Mar.', 'March').replace('Apr.', 'April').replace('Aug.', 'Aug').replace("Sept.", 'September').replace("Oct.", "October").replace('Nov.', "November").replace("Dec.", "December")
    for ABC in 'ABCDEFGHIJKLMNOPQRSTUVWXYZ':
        thing = thing.replace(' '+ABC+'. ', ' '+ABC+' ')
    return thing

try:
    with open(".previousgroupend.txt") as F:
        prevgroupend = int(F.read().strip())
except FileNotFoundError:
    prevgroupend = 0


datafilesdir = "newssource"
destfolder = os.path.join("..", "ABSA_BERT", "BERT-E2E-ABSA", "data", "newsprepared")
to_process = [x for x in os.listdir(datafilesdir) if x.endswith('.txt')][prevgroupend : prevgroupend + MAX_ARTICLE_GROUP]
allitems = []
for df in to_process:
    print("Reading ", df)
    with open(os.path.join(datafilesdir, df), encoding="utf-8") as F:
        try:
            # allitems.append(bullshitmask("ONCE UPON A TIME."))
            text = F.read().split('\n')
            allitems.append(bullshitmask('SOURCE: '+text[0]))
            allitems.append(bullshitmask(text[1]))
            for line in text[2: ]:
                for sentence in fixsentences(line).split('. '):
                    if sentence.strip():
                        readymasked = mask(sentence, df)
                        if readymasked:
                            allitems.append(readymasked)
        except UnicodeEncodeError:
            print("Error with ", df)
            continue


if not os.path.isdir(destfolder):
    os.system("mkdir "+destfolder)
print("Wrote to", destfolder)

with open(os.path.join(destfolder, "test.txt"), 'w', encoding='utf-8') as F:
    F.write('\n'.join(allitems))

with open(".previousgroupend.txt", 'w') as F:
    F.write(str(prevgroupend + MAX_ARTICLE_GROUP))

  #  We love the pink pony.####we=O love=O the=O pink=T-POS pony=T-POS .=O
  #  We love the [MASK].####we=0 love=0 the=0 [MASK]=T-POS .=0