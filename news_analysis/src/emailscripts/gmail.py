import email
import imaplib
import re
import os
import easygui
from itertools import chain
from langdetect import detect
from googletrans import Translator


# The following imports are currently not used in the code
# from time import sleep


def isascii(word):
    return len(word) == len(word.encode())

def fetch():
    # returns list of tuples [(source email, body)]
    allbodies = dict()
    mail = imaplib.IMAP4_SSL('imap.gmail.com')
    pw = easygui.enterbox("enter jsvsentilabel password").strip()
    (retcode, capabilities) = mail.login('jsvsentilabel@gmail.com', pw)
    mail.list()
    mail.select('inbox')
    (retcode, messages) = mail.search(None, 'ALL')  # Replace with 'ALL' if wanted, else '(UNSEEN)'
    if retcode == 'OK':
        for num in messages[0].split():
            print('Processing ')
            typ, data = mail.fetch(num, '(RFC822)')
            for response_part in data:
                if isinstance(response_part, tuple):
                    original = email.message_from_bytes(response_part[1])
                    esrc = original['From']
                    if esrc not in allbodies:
                        allbodies[esrc] = []
                    # print (original['Subject'])
                    raw_email = data[0][1]
                    raw_email_string = raw_email.decode('utf-8')
                    email_message = email.message_from_string(raw_email_string)
                    for part in email_message.walk():
                        if (part.get_content_type() == "text/plain"):  # ignore attachments/html
                            body = part.get_payload(decode=True)
                            body = str(body, 'utf-8')
                            allbodies[esrc].append(body)
                        else:
                            continue
    return allbodies


def emails2file(in_dir, info_dir):
    """
    get all unchecked emails, parse them by sentiment tag, and write them
    to file in in_dir.
    Also, keep track of how many items each sender contributes, and write
    this information to info_dir.
    """
    mymails = fetch()
    parsed = {}
    contribution_counts = {} # keep track of how many items (context tags) each person contributes

    # creat regex to match survey questions and sentiment tags
    surveytags = {"GOV_DIST" : "num",
            "CULTURE" : "num",
            "COUNTRY" : "str",
            "POL_LEAN" : "num",
            }
    sentitags = ["CONTEXT", "POS", "NEG", "NEU"]
    regexp = ""
    for tag in surveytags:
        if surveytags[tag] == "num":
            regexp += tag + r": \d|" + tag + r": undefined|"
        elif surveytags[tag] == "str":
            regexp += tag + r": .+?(?=\r\n)|" + tag + r": undefined|"
    
    for tag1 in sentitags:
        addstring = ""
        for tag2 in sentitags:
            addstring += r"\[" + tag2 + r"\]:|"
        regexp += r"\[" + tag1 + r"\]: .+?(?=" + addstring + r".$)|"
    regexp = regexp[:-1]
    
    # final regexp will look like this:
    # regexp2 = r"GOV_DIST: \d|GOV_DIST: undefined|CULTURE: \d|CULTURE: undefined|COUNTRY: .+?(?=\r\n)|COUNTRY: undefined|POL_LEAN: \d|POL_LEAN: undefined|\[NEG\]: .+?(?=\[NEG\]:|\[POS\]:|\[NEU\]:|\[CONTEXT\]:|.$)|\[POS\]: .+?(?=\[NEG\]:|\[POS\]:|\[NEU\]:|\[CONTEXT\]:|.$)|\[NEU\]: .+?(?=\[NEG\]:|\[POS\]:|\[NEU\]:|\[CONTEXT\]:|.$)|\[CONTEXT\]: .+?(?=\[NEG\]:|\[POS\]:|\[NEU\]:|\[CONTEXT\]:|.$)"

    # go through each email and parse it
    for sender in mymails:
        parsed[sender] = []
        for email in mymails[sender]:
            # If there is no survey info, assume the email is invalid and ignore it
            if not re.search(r"POL_LEAN: \d|POL_LEAN: undefined", email, flags=re.S):
                continue
            # separate email into a list of strings using regex.
            # then remove trailing whitespace and all newlines
            else:
                parsed[sender].append(re.findall(regexp, email, flags=re.S))
                parsed[sender][-1] = [s.replace("\r\n", " ").strip() for s in parsed[sender][-1]]
        # right now parsed[sender] is a list of lists, so collapse it
        parsed[sender] = list(chain.from_iterable(parsed[sender]))
        if parsed[sender] == []:
            parsed.pop(sender)

    for sdr in parsed:
        sender = "".join([ c if c.isalnum() else "_" for c in sdr ])
        if sender not in contribution_counts:
            contribution_counts[sender] = 0
        current_path = os.path.join(in_dir, sender)
        f = open(current_path, "a", encoding="utf-8")
        for item in parsed[sdr]:
            if item.startswith("[CONTEXT]"):
                f.write("\n")
                contribution_counts[sender] += 1
            f.write("\n" + item)
        f.close()

    # write contribution counts to info_dir (overwrite)
    info_path = os.path.join(info_dir, "info.txt")
    with open(info_path, "w") as f:
        for s in contribution_counts:
            f.write(s + ":" + str(contribution_counts[s]) + "\n")
            print(f"Printed {s}'s contribution count to info file")


def process_tags(in_dir, out_dir):
    """
    Get rid of the highlighted sentiment targets in context sentences
    Replace the targets with <COVERED>
    """

    # reg exp to be used to separate tags from content
    regexp = re.compile(r"^(\[[A-Z]+\]): (.*)$")

    # open each parsedemail to be read
    for fn in os.listdir(in_dir):
        filename = "".join([ c if c.isalnum() else "_" for c in fn ])
        parsed = open(os.path.join(in_dir, filename), "r", encoding="utf-8")
        # create new path to write to
        new_path = os.path.join(out_dir, filename+"_processed")
        print(f"new_path = {new_path}")
        context = ""
        foreign_langs = []
        for chunk in parsed.read().split("\n\n")[1:]:
            for line in chunk.split("\n"):
                try:
                    matches = regexp.match(line)
                    tag = matches.group(1)
                    highlighted_text = matches.group(2)
                except AttributeError:
                    continue

                # Either no tag or no text, so ignore it
                if not tag.strip() or not highlighted_text.strip():
                    continue
                
                # Not a context tag, so just replace word and continue
                if tag != "[CONTEXT]" and context.strip():
                    context = context.replace(highlighted_text, tag, 1)
                    continue

                # write context to file and put next sentence in memory
                elif context.strip():
                    my_write(new_path, lang, foreign_langs, context)
                context = highlighted_text
                lang = 'en' if isascii(context) else detect(context)

        # write the final context sentence
        my_write(new_path, lang, foreign_langs, context)
        parsed.close()


def translate(out_dir):
    """
    Translates non-English files using googletrans
    """
    translator = Translator()
    for filename in os.listdir(out_dir):
        source_lang = filename[-2:]

        # "ed" is the end of "processed" and is not a valid language tag.
        # if a file ends with "ed", it is in English.
        if source_lang == "ed":
            continue

        path = os.path.join(out_dir, filename)
        readfile = open(path, "r", encoding="utf-8") 
        writefile = open(path + "_to_en_processed", "a", encoding="utf-8")
        char_count = 0
        to_translate = ""

        for line in readfile.read().split("\n"):
            if char_count > 3000:
                translated = translator.translate(to_translate, src = source_lang)
                writefile.write(translated.text + "\n") 
                char_count = 0
                to_translate = ""
            else:
                char_count += len(line)
                to_translate += line + "\n"

        if char_count > 0:
            translated = translator.translate(to_translate, src=source_lang)
            writefile.write(translated.text)
        
        readfile.close()
        writefile.close()


def my_write(path, lang, foreign_langs, context):
    # write english sentences to writefile
    if lang == "en":
        pass
    # write other langs to separate files
    else:
        path = path + f"_{lang}"
        if lang not in foreign_langs:
            foreign_langs.append(lang)
    print("Writing to {}".format(path), end='\r')
    with open(path, "a", encoding="utf-8") as writefile:
        writefile.write(context + "\n")
    print("Wrote to {}           ".format(path))


def run(in_dir, out_dir, info_dir):
    emails2file(in_dir, info_dir)
    process_tags(in_dir, out_dir)
    translate(out_dir)
