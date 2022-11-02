import pandas as pd
# import matplotlib.pyplot as plt
import sys
import pandas as pd
from PyQt5.QtWidgets import QApplication, QTableView
from PyQt5.QtCore import QAbstractTableModel, Qt

df = pd.DataFrame({'a': ['Mary', 'Jim', 'John'],
                   'b': [100, 200, 300],
                   'c': ['a', 'b', 'c']})

class pandasModel(QAbstractTableModel):

    def __init__(self, data):
        QAbstractTableModel.__init__(self)
        self._data = data

    def rowCount(self, parent=None):
        return self._data.shape[0]

    def columnCount(self, parnet=None):
        return self._data.shape[1]

    def data(self, index, role=Qt.DisplayRole):
        if index.isValid():
            if role == Qt.DisplayRole:
                return str(self._data.iloc[index.row(), index.column()])
        return None

    def headerData(self, col, orientation, role):
        if orientation == Qt.Horizontal and role == Qt.DisplayRole:
            return self._data.columns[col]
        return None



def process_data():
    txt = '''
    CAN1:   ID: 0x502  LEN: 4  DATA: 0 0 0 0 0 64 0 128   TS: 58306
    CAN1:   ID: 0x383  LEN: 8  DATA: 5 32 164 127 130 0 0 124   TS: 58393
    CAN1:   ID: 0x153  LEN: 8  DATA: 0 128 16 255 0 255 192 78   TS: 59254
    CAN1:   ID: 0x220  LEN: 8  DATA: 8 100 130 48 0 239 15 213   TS: 59375
    CAN2:   ID: 0x101  LEN: 8  DATA: 6 4 0 21 0 0 17 8   TS: 29891
    CAN1:   ID: 0x153  LEN: 8  DATA: 0 12 16 255 0 255 192 78   TS: 59254
    CAN2:   ID: 0x105  LEN: 8  DATA: 0 4 0 21 0 0 1 8   TS: 29891
    CAN2:   ID: 0x101  LEN: 8  DATA: 6 4 0 21 0 0 17 8   TS: 29891
    CAN1:   ID: 0x383  LEN: 8  DATA: 5 3 164 127 130 0 0 12   TS: 58393

    '''
    dict = {'ID':[],
            'LEN':[],
            'DATA':[],
            'TS':[]
        }

    # fig, ax = plt.subplots()
    # fig.patch.set_visible(False)
    # ax.axis('off')
    # ax.axis('tight')

    CAN = pd.DataFrame(dict)
    GATEWAY = pd.DataFrame(dict)
    print(CAN)
    lines = txt.split('\n')
    for line in lines:
        #words = line.split()
        # if words[0] == "CAN1":
        #     print(words)
        if line.startswith('CAN1'):     #TABLE FOR CANID
            words = line.split()
            idx = CAN.index[CAN['ID'] == words[2]]
            if not idx.empty:
            # if words[2] in CAN.values:
                    # idx = CAN.index[CAN['ID'] == words[2]]
                    print("Idx: ",idx[0])
                    print("ID: ", words[2], " already in DF")
                    # CAN.loc[CAN['ID'] == words[2], 'LEN', 'DATA', 'TS:'] = words[4], words[6:13], words[15]     # update record
                    CAN.loc[idx[0],['LEN']] = words[4]
                    CAN.loc[idx[0],['DATA']] = [words[6:13]]
                    CAN.loc[idx[0],['TS']] = words[15]

            else:
                    newRow = {'ID': words[2], 'LEN': words[4], 'DATA': words[6:13], 'TS': words[15]}
                    CAN = CAN.append(newRow, ignore_index=True)
            print(CAN)
            # table = ax.table(cellText=CAN.values, colLabels=CAN.columns, loc='center')
            # fig.tight_layout()
            # plt.show()
        elif line.startswith('CAN2'):     #TABLE FOR CANID
            words = line.split()
            #if words[2] in GATEWAY.values:
            idx = GATEWAY.index[GATEWAY['ID'] == words[2]]
            if not idx.empty:
                    print("Idx: ",idx[0])
                    print("ID: ", words[2], " already in DF")
                    # CAN.loc[CAN['ID'] == words[2], 'LEN', 'DATA', 'TS:'] = words[4], words[6:13], words[15]     # update record
                    GATEWAY.loc[idx[0],['LEN']] = words[4]
                    GATEWAY.loc[idx[0],['DATA']] = [words[6:13]]
                    GATEWAY.loc[idx[0],['TS']] = words[15]

            else:
                    newRow = {'ID': words[2], 'LEN': words[4], 'DATA': words[6:13], 'TS': words[15]}
                    GATEWAY = GATEWAY.append(newRow, ignore_index=True)
            print(GATEWAY)
            # print(words[2])

    # make table

if __name__ == '__main__':
    app = QApplication(sys.argv)
    model = pandasModel(df)
    view = QTableView()
    view.setModel(model)
    view.resize(800, 600)
    view.show()
    sys.exit(app.exec_())