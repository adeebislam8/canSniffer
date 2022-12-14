from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QTableWidgetItem, QPushButton
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from PyQt5 import QtGui
from sniffer_ui import Ui_MainWindow
import sys
import logging
import time
# sys.path.insert(0, '/home/adeeb/')
from serialTransmission import serialReader

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


file1 = open("brake.txt", "r")
if file1:
    logging.debug("Reading from file")
    txt = file1.read()



logging.basicConfig(format='%(asctime)s : %(levelname)s : %(message)s', level=logging.DEBUG)  



#   FEATURES TO INCLUDE
    #   DOES SERIAL READING
    #   PAUSE PARSING
    #   ADD A 2 TEXT INPUTS AND BUTTON WHICH WILL CREATE A GATEWAY -> PHYSICAL CORRESPONDANCE TABLE
    #  



class parserWorker(QObject):

    parsedLineSignal = pyqtSignal([list])
    finishedSignal = pyqtSignal()


    def loadTxtData(self):

        lines = txt.split('\n')

        for line in lines:
            # logging.debug(line)
            time.sleep(0.1)
            self.parseLine(line)

        self.finishedSignal.emit()

    def connectToSerialCom(self):
        self.canCom = serialReader.arduinoComm()
        while self.canCom.commStart:
            self.loadSerialData()

    def loadSerialData(self):
        if self.canCom.commStart:
            # print("Parsing Serial Line")
            line = self.canCom.readCanLine()
            # print("Check line: ", line)
            self.parseLine(line)
        
        else:
            print("Port not open. Closing")
            self.finishedSignal.emit()

    def parseLine(self, line):

        words = line.split()
        # print("Parsed Line: ", words)
        if line.startswith('CAN1'):     #TABLE FOR CANID

            ID = str(words[2])
            DATA = words[6:14]
            # DATA = str(words[6:13])
            TS = str(words[15])

            self.rowData = ['CAN', ID, DATA, TS]
            # logging.debug("Sending Parsed Line Signal")

            self.parsedLineSignal.emit(self.rowData)
        
        elif line.startswith('CAN2'):     #TABLE FOR Gateway

            ID = str(words[2])
            DATA = words[6:14]
            # DATA = str(words[6:13])
            TS = str(words[15])

            self.rowData = ['GATEWAY', ID, DATA, TS]
            # logging.debug("Sending Parsed Line Signal")

            self.parsedLineSignal.emit(self.rowData)

# THIS CLASS HANDLES THE GUI  
# 
# // Add isolated tablegateway and isolated tableCAN (done)
# // Add a button to add a row to the isolated tablegateway (TODO button not appearing)
# // Add a button to add a row to the isolated tableCAN (TODO button not appearing)
# // use self.ui.tableWidgetIsoltaedGateway.setItem(row, col, self.ui.tableWidgetGateway.item(row, col)))     (done)

class window(QtWidgets.QMainWindow):

    def __init__(self):
        super(window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tableWidget.setColumnCount(10)
        self.ui.tableWidget.itemClicked.connect(self.getTableClickCAN)

        self.ui.addGatewayButton = QPushButton("Add Gateway")
        self.ui.addCANButton = QPushButton("Add CAN")

        self.ui.addGatewayButton.clicked.connect(self.addGatewayRow)
        self.ui.addCANButton.clicked.connect(self.addCANRow)

        self.selectedRow = None

        for i in range(8):
            # self.ui.tableWidget.setColumnWidth(1,150)
            self.ui.tableWidget.setColumnWidth(i+1,50)

        # self.ui.tableWidget.setColumnWidth(2,150)
        self.ui.tableWidget.setHorizontalHeaderLabels(('ID','D[0]', 'D[1]','D[2]','D[3]','D[4]','D[5]','D[6]','D[7]','TS'))


        self.ui.tableWidgetGateway.setColumnCount(10)
        self.ui.tableWidgetGateway.itemClicked.connect(self.getTableClickGateway)

        for i in range(8):
            # self.ui.tableWidget.setColumnWidth(1,150)
            self.ui.tableWidgetGateway.setColumnWidth(i+1,50)

        # self.ui.tableWidgetGateway.setColumnWidth(1,150)
        # self.ui.tableWidgetGateway.setColumnWidth(2,150)
        self.ui.tableWidgetGateway.setHorizontalHeaderLabels(('ID','D[0]', 'D[1]','D[2]','D[3]','D[4]','D[5]','D[6]','D[7]','TS'))
        # self.ui.tableWidgetGateway.setHorizontalHeaderLabels(('ID','DATA','TS'))

        self.parserThread = QThread()
        self.parserObject = parserWorker()
        self.parserObject.moveToThread(self.parserThread)

        self.parserThread.started.connect(self.parserObject.loadTxtData)
        
        # self.parserThread.started.connect(self.parserObject.connectToSerialCom)

        self.parserObject.finishedSignal.connect(self.parserThread.quit)
        self.parserObject.parsedLineSignal.connect(self.updateTableRow)

        self.parserThread.start()
    

    def getTableClickCAN(self, item):
        print("Table Clicked")
        self.row = item.row()
        self.col = item.column()
        self.text = item.text()
        self.selectedRow = self.row
        print("Row: ", self.row, "Col: ", self.col, "Text: ", self.text)
        self.rowData = [self.row, self.col, self.text]
        # self.ui.tableWidgetGateway.selectRow(self.row)

        self.parserObject.parsedLineSignal.emit(self.rowData)


    def getTableClickGateway(self, item):
        print("Table Clicked")
        self.row = item.row()
        self.col = item.column()
        self.text = item.text()
        self.selectedRow = self.row

        print("Row: ", self.row, "Col: ", self.col, "Text: ", self.text)
        self.rowData = [self.row, self.col, self.text]
        # highlight the row
        # self.ui.tableWidgetGateway.selectRow(self.row)
        self.parserObject.parsedLineSignal.emit(self.rowData)

    def addGatewayRow(self):
        self.ui.tableWidgetIsolatedGateway.insertRow(self.ui.tableWidgetIsolatedGateway.rowCount())
        for i in range(10):
            self.ui.tableWidgetIsolatedGateway.setItem(self.ui.tableWidgetIsolatedGateway.rowCount()-1, i, self.ui.tableWidgetGateway.item(self.ui.tableWidgetGateway.rowCount()-1, i).text())

    def addCANRow(self):
        self.ui.tableWidgetIsolatedCAN.insertRow(self.ui.tableWidgetIsolatedCAN.rowCount())
        for i in range(10):
            self.ui.tableWidgetIsolatedCAN.setItem(self.ui.tableWidgetIsolatedCAN.rowCount()-1, i, self.ui.tableWidget.item(self.ui.tableWidget.rowCount()-1, i).text())


    def compareRowData(self,tableWidget, rowIdx, DATA):
        for i in range(8):
            # print("Checking: ", tableWidget.item(rowIdx, i+1).text(), DATA[i])
            if tableWidget.item(rowIdx, i+1).text() > DATA[i]:
                tableWidget.setItem(rowIdx, i+1, QtWidgets.QTableWidgetItem(DATA[i]))
                tableWidget.item(rowIdx, i+1).setBackground(QtGui.QColor(255,0,0))
                # print("RED")
            elif tableWidget.item(rowIdx, i+1).text() < DATA[i]:
                tableWidget.setItem(rowIdx, i+1, QtWidgets.QTableWidgetItem(DATA[i]))
                tableWidget.item(rowIdx, i+1).setBackground(QtGui.QColor(0,255,0))

                # print("GREEN")
            else:
                tableWidget.setItem(rowIdx, i+1, QtWidgets.QTableWidgetItem(DATA[i]))
                tableWidget.item(rowIdx, i+1).setBackground(QtGui.QColor(0,181,226))

                # print("WHITE")
                # print("BLUE")
            # self.ui.tableWidget.setItem(rowIdx, i+1, QtWidgets.QTableWidgetItem(str(DATA[i])))

    def updateTableRow(self, line):

        # logging.debug("Received Parsed Line Signal")
        # logging.debug(line)


        if line[0] == 'CAN':
                ID = line[1]
                DATA = line[2]
                # print(DATA[0])
                TS = line[3]
                # dataList = DATA.split('\'')

                # print(DATA)
                # dataList[:0] = DATA

                matchingItem = self.ui.tableWidget.findItems(ID,Qt.MatchContains)

                # logging.debug(matchingItem)
# 
                if matchingItem:                                            # found matching id
                    # logging.debug("Found matching Item")
                    # logging.debug(matchingItem[0])

                    self.ui.tableWidget.setCurrentItem(matchingItem[0])

                    rowIdx = self.ui.tableWidget.currentRow()
                    # logging.debug(rowIdx)   

                    self.compareRowData(self.ui.tableWidget, rowIdx, DATA)
                    # for i in range(8):
                    #     self.ui.tableWidget.setItem(rowIdx, i+1, QtWidgets.QTableWidgetItem(str(DATA[i])))
                    # for i in range(8):
                    #     self.ui.tableWidget.setItem(rowIdx, i+1, QtWidgets.QTableWidgetItem(str(dataList[i+1])))
                        # self.ui.tableWidget.setItem(rowIdx,1, QTableWidgetItem(DATA))
                    self.ui.tableWidget.setItem(rowIdx,9, QTableWidgetItem(TS))

                    #

                    item = self.ui.tableWidget.item(rowIdx, 0)
                    # self.ui.tableWidget.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    # self.ui.tableWidget.selectRow(rowIdx)

                    # time.sleep(1)
                    # logging.debug(ID)

                else:
                    logging.debug("Didnt find matching Item")

                    rowCount = self.ui.tableWidget.rowCount()
                    # print(rowCount)
                    self.ui.tableWidget.insertRow(rowCount)
                    self.ui.tableWidget.setItem(rowCount,0, QTableWidgetItem(ID))
                    for i in range(8):
                        self.ui.tableWidget.setItem(rowCount, i+1, QtWidgets.QTableWidgetItem(str(DATA[i])))
                    
                    # self.ui.tableWidget.setItem(rowCount,1, QTableWidgetItem(DATA))
                    self.ui.tableWidget.setItem(rowCount,9, QTableWidgetItem(TS))
                    
                    item = self.ui.tableWidget.item(rowCount, 0)
                    # self.ui.tableWidget.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    # self.ui.tableWidget.selectRow(rowCount)
                    
        if line[0] == 'GATEWAY':
                ID = line[1]
                DATA = line[2]
                TS = line[3]
                # print(DATA)
                # dataList = DATA.split(',')
                # print(dataList)

                matchingItem = self.ui.tableWidgetGateway.findItems(ID,Qt.MatchContains)

                # logging.debug(matchingItem)

                if matchingItem:
                    # logging.debug("Found matching Item")
                    # logging.debug(matchingItem[0])

                    self.ui.tableWidgetGateway.setCurrentItem(matchingItem[0])

                    rowIdx = self.ui.tableWidgetGateway.currentRow()
                    # logging.debug(rowIdx)
                    data = self.ui.tableWidgetGateway.item(rowIdx, 2)
                    # print()
                    # logging.debug("DATA")
                    # logging.debug(data.text())


                    self.compareRowData(self.ui.tableWidgetGateway,rowIdx, DATA)

                    # for i in range(8):
                    #     self.ui.tableWidgetGateway.setItem(rowIdx, i+1, QtWidgets.QTableWidgetItem(str(DATA[i])))
                    
                    # self.ui.tableWidgetGateway.setItem(rowIdx,1, QTableWidgetItem(DATA))
                    self.ui.tableWidgetGateway.setItem(rowIdx,9, QTableWidgetItem(TS))

                    item = self.ui.tableWidgetGateway.item(rowIdx, 0)
                    # self.ui.tableWidgetGateway.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    # self.ui.tableWidgetGateway.selectRow(rowIdx)

                    # time.sleep(1)

                    # logging.debug(ID)

                else:
                    # logging.debug("Didnt find matching Item")

                    rowCount = self.ui.tableWidgetGateway.rowCount()
                    # print(rowCount)
                    self.ui.tableWidgetGateway.insertRow(rowCount)
                    self.ui.tableWidgetGateway.setItem(rowCount,0, QTableWidgetItem(ID))

                    for i in range(8):
                        self.ui.tableWidgetGateway.setItem(rowCount, i+1, QtWidgets.QTableWidgetItem(str(DATA[i])))
                    # self.ui.tableWidgetGateway.setItem(rowCount,1, QTableWidgetItem(DATA))

                    self.ui.tableWidgetGateway.setItem(rowCount,9, QTableWidgetItem(TS))

                    item = self.ui.tableWidgetGateway.item(rowCount, 0)
                    # self.ui.tableWidgetGateway.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    # self.ui.tableWidgetGateway.selectRow(rowCount)

def create_app():
    app = QApplication(sys.argv)

    win = window()
    win.show()
 
    app.exec_()


create_app()