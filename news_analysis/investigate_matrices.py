import os
from news_analysis.src.tools.sparse_matrix import jsv_dictmat

with open("words2resolved.txt", encoding='utf-8') as F:
    idx2NE = {i:' '.join(x.split(' ')[1:]) for i, x in enumerate(F.read().split('\n')[:-1])}

print(idx2NE)
print(len(idx2NE))
input()
with open("filepaths.txt") as F:
    fps = [x.split('#')[0].split(' ') for x in F.read().split('\n') if x]
    filepaths = {x[0][:-1]:os.path.join(*x[1:]) for x in fps}

matrices_parent = filepaths["matrix_out"]
sparse = dict()
for publisher_folder in os.listdir(matrices_parent):
    fp = os.path.join(matrices_parent, publisher_folder)
    if publisher_folder not in sparse:
        sparse[publisher_folder] = []
    for daily_matrix in os.listdir(fp):
        print(daily_matrix)
        sm = jsv_dictmat(os.path.join(fp, daily_matrix))
        sparse[publisher_folder].append(sm)



for publisher in sparse.keys():
    for mat in sparse[publisher]:
        # Print the contents of each
        mat.print_readable(idx2NE)
        input()
        print('converting')
        scipy_mat = mat.to_scipy()
        print("finished")
        for i in scipy_mat:
            print(i)
            input()
        # TODO:  Anything
        # ...