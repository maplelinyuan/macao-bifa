from PyQt5 import QtCore, QtGui, QtWidgets, QtSql
import time
import datetime
import json
import pdb

def is_chinese(uchar):
    """判断一个unicode是否是汉字"""
    if uchar >= u'\u4e00' and uchar <= u'\u9fa5':
        return True
    else:
        return False

class Ui_MainWindow(object):
    def setupUi(self, MainWindow):
        self.league_name = ''

        MainWindow.setObjectName("MainWindow")
        MainWindow.resize(1000, 600)
        self.centralwidget = QtWidgets.QWidget(MainWindow)
        self.centralwidget.setObjectName("centralwidget")
        self.comboBox = QtWidgets.QComboBox(self.centralwidget)
        self.comboBox.setGeometry(QtCore.QRect(10, 10, 141, 31))
        self.comboBox.setObjectName("comboBox")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.comboBox.addItem("")
        self.pushButton = QtWidgets.QPushButton(self.centralwidget)
        self.pushButton.setGeometry(QtCore.QRect(500, 20, 75, 23))
        self.pushButton.setObjectName("pushButton")
        self.tableWidget = QtWidgets.QTableWidget(self.centralwidget)
        self.tableWidget.setGeometry(QtCore.QRect(10, 60, 860, 500))
        self.tableWidget.setObjectName("tableWidget")
        self.tableWidget.setColumnCount(8)
        self.tableWidget.setRowCount(0)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(0, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(1, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(2, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(3, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(4, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(5, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(6, item)
        item = QtWidgets.QTableWidgetItem()
        self.tableWidget.setHorizontalHeaderItem(7, item)
        MainWindow.setCentralWidget(self.centralwidget)
        self.menubar = QtWidgets.QMenuBar(MainWindow)
        self.menubar.setGeometry(QtCore.QRect(0, 0, 900, 23))
        self.menubar.setObjectName("menubar")
        MainWindow.setMenuBar(self.menubar)
        self.statusbar = QtWidgets.QStatusBar(MainWindow)
        self.statusbar.setObjectName("statusbar")
        MainWindow.setStatusBar(self.statusbar)

        self.retranslateUi(MainWindow)
        QtCore.QMetaObject.connectSlotsByName(MainWindow)

        self.comboBox.activated[str].connect(self.onActivated)   ##用来将combobox关联的函数

    def retranslateUi(self, MainWindow):
        _translate = QtCore.QCoreApplication.translate
        MainWindow.setWindowTitle(_translate("MainWindow", "MatchBook_Analysis"))
        self.comboBox.setItemText(0, _translate("MainWindow", "select league"))
        self.comboBox.setItemText(1, _translate("MainWindow", "belgium"))
        self.comboBox.setItemText(2, _translate("MainWindow", "denmark"))
        self.comboBox.setItemText(3, _translate("MainWindow", "england"))
        self.comboBox.setItemText(4, _translate("MainWindow", "france"))
        self.comboBox.setItemText(5, _translate("MainWindow", "germany"))
        self.comboBox.setItemText(6, _translate("MainWindow", "italy"))
        self.comboBox.setItemText(7, _translate("MainWindow", "netherlands"))
        self.comboBox.setItemText(8, _translate("MainWindow", "portugal"))
        self.comboBox.setItemText(9, _translate("MainWindow", "russia"))
        self.comboBox.setItemText(10, _translate("MainWindow", "scotland"))
        self.comboBox.setItemText(11, _translate("MainWindow", "spain"))
        self.comboBox.setItemText(12, _translate("MainWindow", "turkey"))
        self.comboBox.setItemText(13, _translate("MainWindow", "argentina"))
        self.comboBox.setItemText(14, _translate("MainWindow", "australia"))
        self.comboBox.setItemText(15, _translate("MainWindow", "austria"))
        self.comboBox.setItemText(16, _translate("MainWindow", "switzerland"))
        item = self.tableWidget.horizontalHeaderItem(0)
        item.setText(_translate("MainWindow", "开赛时间"))
        item = self.tableWidget.horizontalHeaderItem(1)
        item.setText(_translate("MainWindow", "主队名"))
        item = self.tableWidget.horizontalHeaderItem(2)
        item.setText(_translate("MainWindow", "盘口"))
        item = self.tableWidget.horizontalHeaderItem(3)
        item.setText(_translate("MainWindow", "客队名"))
        item = self.tableWidget.horizontalHeaderItem(4)
        item.setText(_translate("MainWindow", "主p净支持"))
        item = self.tableWidget.horizontalHeaderItem(5)
        item.setText(_translate("MainWindow", "主v净支持"))
        item = self.tableWidget.horizontalHeaderItem(6)
        item.setText(_translate("MainWindow", "主vp净支持"))
        item = self.tableWidget.horizontalHeaderItem(7)
        item.setText(_translate("MainWindow", "最后更新时间"))
        self.pushButton.setText(_translate("MainWindow", "切换中/英"))

    def onActivated(self, text):  ##用来实现combobox关联的函数
        if text == 'select league':
            self.league_name = ''
            return
        self.league_name = text
        # 先连接至分析数据库获取上次所用分析表的时间
        db = QtSql.QSqlDatabase().addDatabase("QMYSQL")
        db.setDatabaseName("match_" + text + "_analysis")
        db.setHostName("127.0.0.1")  # set address
        db.setUserName("root");  # set user name
        db.setPassword("");  # set user pwd
        if not db.open():
            # 打开失败
            return db.lastError()
        print("连接至 match_",text,"_analysis success!")
        # 创建QsqlQuery对象，用于执行sql语句
        query = QtSql.QSqlQuery()
        build_table = (
            "CREATE TABLE IF NOT EXISTS "' %s '""
            "(event_id VARCHAR(20) NOT NULL PRIMARY KEY,"
            "host_name VARCHAR(20) NOT NULL,"
            "guest_name VARCHAR(20) NOT NULL,"
            "handicap_name VARCHAR(20) NOT NULL,"
            "start_time VARCHAR(20) NOT NULL,"
            "host_price_net_support INT(4) NOT NULL DEFAULT 0,"
            "host_volume_net_support INT(4) NOT NULL DEFAULT 0,"
            "host_volume_price_net_support INT(4) NOT NULL DEFAULT 0,"
            "is_end INT(4) DEFAULT 0,"
            "handicap_result FLOAT(4),"  # 9 表示未知
            "last_updatetime VARCHAR(20))"
        )
        query.exec(build_table % 'analysis_result')
        # 查询出当前数据库中的所有表名
        query.exec('SELECT * FROM analysis_result')
        query.next()
        # 保存最后分析用的表上的时间，以便之后分析跳过用过的表
        if query.size() > 0:
            last_load_data_time = time.mktime(time.strptime(query.value(10), '%Y-%m-%d %H:%M:%S'))
        else:
            last_load_data_time = 0
        db.close()
        # 连接数据库
        db = QtSql.QSqlDatabase().addDatabase("QMYSQL")
        db.setDatabaseName("aoke_macao_complete")
        db.setHostName("127.0.0.1")  # set address
        db.setUserName("root")  # set user name
        db.setPassword("")  # set user pwd
        # 打开数据库
        if not db.open():
            # 打开失败
            return db.lastError()
        print("连接至 match_",text,"success!")

        # 保存比赛分析结果的字典，用event_id 映射单场比赛
        match_analysis_result = {}

        # 创建QsqlQuery对象，用于执行sql语句
        query = QtSql.QSqlQuery()
        # 查询出当前数据库中的所有表名
        query.exec('SHOW TABLES FROM match_'+text)
        query.next()


if __name__ == "__main__":
    import sys

    app = QtWidgets.QApplication(sys.argv)
    MainWindow = QtWidgets.QMainWindow()
    ui = Ui_MainWindow()
    ui.setupUi(MainWindow)
    MainWindow.show()
    sys.exit(app.exec_())
