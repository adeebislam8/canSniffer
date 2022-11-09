from PyQt5 import QtWidgets
from PyQt5.QtWidgets import QApplication, QTableWidgetItem
from PyQt5.QtCore import Qt, QObject, QThread, pyqtSignal
from sniffer_ui import Ui_MainWindow
import sys
import logging
import time
sys.path.insert(0, '/home/adeeb/')
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


# file1 = open("CAN_Log.txt", "r")
# if file1:
#     logging.debug("Reading from file")
#     txt = file1.read()



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
            logging.debug(line)
            time.sleep(0.1)
            self.parseLine(line)

        self.finishedSignal.emit()

    def connectToSerialCom(self):
        self.canCom = serialReader.arduinoComm()
        while self.canCom.commStart:
            self.loadSerialData()

    def loadSerialData(self):
        if self.canCom.commStart:
            print("Parsing Serial Line")
            line = self.canCom.readCanLine()
            print("Check line: ", line)
            self.parseLine(line)
        
        else:
            print("Port not open. Closing")
            self.finishedSignal.emit()

    def parseLine(self, line):

        words = line.split()
        print("Parsed Line: ", words)
        if line.startswith('CAN1'):     #TABLE FOR CANID

            ID = str(words[2])
            DATA = str(words[6:13])
            TS = str(words[15])

            self.rowData = ['CAN', ID, DATA, TS]
            logging.debug("Sending Parsed Line Signal")

            self.parsedLineSignal.emit(self.rowData)
        
        elif line.startswith('CAN2'):     #TABLE FOR Gateway

            ID = str(words[2])
            DATA = str(words[6:13])
            TS = str(words[15])

            self.rowData = ['GATEWAY', ID, DATA, TS]
            logging.debug("Sending Parsed Line Signal")

            self.parsedLineSignal.emit(self.rowData)


# THIS CLASS HANDLES THE GUI        
class window(QtWidgets.QMainWindow):

    def __init__(self):
        super(window, self).__init__()
        self.ui = Ui_MainWindow()
        self.ui.setupUi(self)
        self.ui.tableWidget.setColumnCount(3)
        self.ui.tableWidget.setColumnWidth(1,550)
        self.ui.tableWidget.setColumnWidth(2,150)
        self.ui.tableWidget.setHorizontalHeaderLabels(('ID','DATA','TS'))


        self.ui.tableWidget_2.setColumnCount(3)
        self.ui.tableWidget_2.setColumnWidth(1,550)
        self.ui.tableWidget_2.setColumnWidth(2,150)
        self.ui.tableWidget_2.setHorizontalHeaderLabels(('ID','DATA','TS'))

        self.parserThread = QThread()
        self.parserObject = parserWorker()
        self.parserObject.moveToThread(self.parserThread)

        # self.parserThread.started.connect(self.parserObject.loadTxtData)
        
        self.parserThread.started.connect(self.parserObject.connectToSerialCom)

        self.parserObject.finishedSignal.connect(self.parserThread.quit)
        self.parserObject.parsedLineSignal.connect(self.updateTableRow)

        self.parserThread.start()
    
    def updateTableRow(self, line):

        logging.debug("Received Parsed Line Signal")
        logging.debug(line)

        if line[0] == 'CAN':
                ID = line[1]
                DATA = line[2]
                TS = line[3]

                matchingItem = self.ui.tableWidget.findItems(ID,Qt.MatchContains)

                logging.debug(matchingItem)

                if matchingItem:
                    logging.debug("Found matching Item")
                    logging.debug(matchingItem[0])

                    self.ui.tableWidget.setCurrentItem(matchingItem[0])

                    rowIdx = self.ui.tableWidget.currentRow()
                    logging.debug(rowIdx)

                    self.ui.tableWidget.setItem(rowIdx,1, QTableWidgetItem(DATA))
                    self.ui.tableWidget.setItem(rowIdx,2, QTableWidgetItem(TS))

                    item = self.ui.tableWidget.item(rowIdx, 0)
                    self.ui.tableWidget.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    self.ui.tableWidget.selectRow(rowIdx)

                    # time.sleep(1)
                    logging.debug(ID)

                else:
                    logging.debug("Didnt find matching Item")

                    rowCount = self.ui.tableWidget.rowCount()
                    # print(rowCount)
                    self.ui.tableWidget.insertRow(rowCount)
                    self.ui.tableWidget.setItem(rowCount,0, QTableWidgetItem(ID))
                    self.ui.tableWidget.setItem(rowCount,1, QTableWidgetItem(DATA))
                    self.ui.tableWidget.setItem(rowCount,2, QTableWidgetItem(TS))
                    
                    item = self.ui.tableWidget.item(rowCount, 0)
                    self.ui.tableWidget.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    self.ui.tableWidget.selectRow(rowCount)
                    
        if line[0] == 'GATEWAY':
                ID = line[1]
                DATA = line[2]
                TS = line[3]

                matchingItem = self.ui.tableWidget_2.findItems(ID,Qt.MatchContains)

                logging.debug(matchingItem)

                if matchingItem:
                    logging.debug("Found matching Item")
                    logging.debug(matchingItem[0])

                    self.ui.tableWidget_2.setCurrentItem(matchingItem[0])

                    rowIdx = self.ui.tableWidget_2.currentRow()
                    logging.debug(rowIdx)

                    self.ui.tableWidget_2.setItem(rowIdx,1, QTableWidgetItem(DATA))
                    self.ui.tableWidget_2.setItem(rowIdx,2, QTableWidgetItem(TS))

                    item = self.ui.tableWidget_2.item(rowIdx, 0)
                    self.ui.tableWidget_2.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    self.ui.tableWidget_2.selectRow(rowIdx)

                    # time.sleep(1)

                    logging.debug(ID)

                else:
                    logging.debug("Didnt find matching Item")

                    rowCount = self.ui.tableWidget_2.rowCount()
                    # print(rowCount)
                    self.ui.tableWidget_2.insertRow(rowCount)
                    self.ui.tableWidget_2.setItem(rowCount,0, QTableWidgetItem(ID))
                    self.ui.tableWidget_2.setItem(rowCount,1, QTableWidgetItem(DATA))
                    self.ui.tableWidget_2.setItem(rowCount,2, QTableWidgetItem(TS))

                    item = self.ui.tableWidget_2.item(rowCount, 0)
                    self.ui.tableWidget_2.scrollToItem(item, QtWidgets.QAbstractItemView.PositionAtTop)
                    self.ui.tableWidget_2.selectRow(rowCount)

def create_app():
    app = QApplication(sys.argv)

    win = window()
    win.show()
 
    app.exec_()


create_app()