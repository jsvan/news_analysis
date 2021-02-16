import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import DataLoader
import random
import torch.optim as optim
import torch.utils.data as td
from torch.autograd import Variable
import time
import pickle
from matplotlib import pyplot as plt
from sklearn.preprocessing import MinMaxScaler




EPOCH = 25
class AutoEncoder(nn.Module):
    def __init__(self, embedding_size, numcolors):
        super(AutoEncoder, self).__init__()
        self.ES = embedding_size
        self.NC = numcolors
        self.H1 = 300
        self.encode = nn.Sequential(
                        nn.Linear(embedding_size, self.H1),
                        nn.ReLU(inplace=True),
                        # nn.Linear(self.H1, self.H3),
                        # nn.ReLU(inplace=True),
                        )
        self.decode = nn.Sequential(
                        # nn.Linear(self.H3, self.H1),
                        # nn.Dropout(),
                        # nn.ReLU(inplace=True),
                        nn.Linear(self.H1, embedding_size),
                        nn.Tanh(),
                        )
        self.predict = nn.Sequential(
                        nn.Linear(self.H1, self.NC),
                        nn.ReLU(),
                        )
    def forward(self, batch):
        m = self.encode(batch)
        return self.decode(m), self.predict(m)




class DataSet(td.Dataset):
    def pad(self, datatensor):
        ret = torch.FloatTensor(np.zeros((1, self.maxtopics)))
        ret[0][0:datatensor.shape[1]] = datatensor
        return ret

    def __init__(self, data, maxtopics):
        self.maxtopics = maxtopics
        self.data = data
        self.DATAIDX = 0
        self.COLIDX = 1

    def __getitem__(self, index):
        dataitem = torch.FloatTensor(self.data[index][self.DATAIDX].todense())
        return self.pad(dataitem) , torch.LongTensor([self.data[index][self.COLIDX]])

    def __len__(self):
        return len(self.data)

class TIME:
    def __init__(self):
        self.start()

    def time(self):
        s = str(round(time.time()-self.t, 0)) + ' sec'
        return s

    def start(self):
        self.t=time.time()



T = TIME()
DEVICE = torch.device('cuda:0' if torch.cuda.is_available() else 'cpu')
datasets, maxtopics, names, num_colors = read_matrices.read(traintest=True)

print(DEVICE)
print('creating model')
MODEL = AutoEncoder(maxtopics, num_colors)
MODEL.to(DEVICE)
loss_auto_enc  = nn.MSELoss().to(DEVICE)
loss_predict = nn.CrossEntropyLoss().to(DEVICE)
optimizer  = optim.Adam(MODEL.parameters(), lr=1e-5)
scheduler = torch.optim.lr_scheduler.ReduceLROnPlateau (optimizer, patience=1, cooldown=1)
trainSet = DataSet(datasets['train'], maxtopics)
testSet = DataSet(datasets['test'],maxtopics)

BATCH_SIZE = 64
trainloader = DataLoader(trainSet, batch_size=BATCH_SIZE, shuffle=True, drop_last=False)
testloader = DataLoader(testSet, batch_size=BATCH_SIZE, shuffle=True, drop_last=False)

eTrainL, eTestL = [],[]
validOut, validX = [],[]
for e in range(EPOCH):
    T.start()
    XeTrainL, XeTestL = 0.0, 0.0
    for ii, (batch, col_lab) in enumerate(trainloader):
        MODEL.zero_grad()
        x = Variable(batch).to(DEVICE).float()
        auto_out, pre_out = MODEL(x)
        loss_enc = loss_auto_enc(auto_out, x)
        #loss_pre = loss_predict(pre_out.squeeze(1), col_lab.to(DEVICE).squeeze(1))
        loss_enc.backward()  # retain_graph=True)
        #loss_pre.backward()
        optimizer.step()
        XeTrainL += loss_enc.item() #+ loss_pre.item()
        print('Train E',str(e),'/', str(EPOCH), 'B',ii,'/',str(trainloader.__len__()), 'T',T.time(), ' train_loss', str(round(XeTrainL/(ii+1),8)), '\r', end='')
    scheduler.step(XeTrainL/(1+ii))
    eTrainL.append(XeTrainL/(1+ii))
    print()
    with torch.no_grad():
        T.start()
        C = 0
        for ii, (batch, col_lab) in enumerate(testloader):
            x = Variable(batch).to(DEVICE).float()
            auto_out, pre_out = MODEL(x)
            loss_enc = loss_auto_enc(auto_out, x)
            #loss_pre = loss_predict(pre_out.squeeze(1), col_lab.to(DEVICE).squeeze(1))
            XeTestL += loss_enc.item()
            print('Test E',str(e),'/', str(EPOCH), 'B',ii,'/',str(testloader.__len__()), 'T',T.time(), ' test_loss', str(round(XeTestL/(ii+1), 8)), '\r', end='')
        eTestL.append(XeTestL/(ii+1))
        print()


plt.plot(eTestL, label='test loss')
plt.plot(eTrainL, label='train loss')
plt.legend()
plt.show()
Xs, Ys = [], []
Cs = []
with torch.no_grad():
    C = 0
    for i, (batch, col_lab) in enumerate(trainloader):
        x = Variable(batch).to(DEVICE).float()
        twoDBatch = MODEL.encode(x)
        for ii, twoD in enumerate(twoDBatch):
            Xs.append(twoD[0][0].item())
            Ys.append(twoD[0][1].item())
            Cs.append(col_lab[ii].item())

plt.scatter(Xs, Ys, s=15, c=Cs)


print("NAMES", names)
plt.show()