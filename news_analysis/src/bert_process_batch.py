import os
import shutil

def run(BERT_DIR, HOME_DIR, BATCH_DIR, BERT_IN_DIR, BERT_OUT_FILE):
    ins = [x for x in os.listdir(BATCH_DIR) if x.endswith('.txt')]
    for f in ins:
        print(f)
        # Move batch into bert-s dir.
        fp = os.path.join(BATCH_DIR, f)
        shutil.copy(fp, os.path.join(BERT_IN_DIR, 'test.txt'))
        try:
            os.remove(os.path.join(BERT_IN_DIR, 'cached_test_bert-base-uncased_128_newsprepared'))
        except FileNotFoundError as E:
            print(E, E.__doc__)
        # Run BERT
        os.chdir(BERT_DIR)
        os.system("sh work.sh")
        os.chdir(HOME_DIR)
        # Move results, input file back to batch_dir
        os.remove(os.path.join(BERT_IN_DIR, 'test.txt'))
        shutil.move(BERT_OUT_FILE, f'{fp}-labels')
