# -*- coding:utf-8 -*-

import os
import time
from datetime import date,timedelta
from PyQt5 import QtCore, QtGui, QtWidgets, uic
from PyQt5.QtWidgets import *
import pymysql.cursors
import sqlite3
import DBconn
from sql import TabDiffSqlMap
from conf import db_account
import paramiko
import unicodedata
import ctypes
import cx_Oracle


ui_folder = os.path.abspath(os.path.dirname('__ui__/'))
form_class = uic.loadUiType(os.path.join(ui_folder, "main_v2.ui"))[0]


# 문자 포메팅
def preformat(string, width, align='<', fill=' '):
    count = (width - sum(1 + (unicodedata.east_asian_width(c) in "WF")
                         for c in string))
    return {
        '>': lambda s: fill * count + s,
        '<': lambda s: s + fill * count,
        '^': lambda s: fill * (count / 2)
                       + s
                       + fill * (count / 2 + count % 2)
    }[align](string)

class MyWindow(QMainWindow, form_class):
    def __init__(self):
        super().__init__()
        self.setupUi(self)

        # button 클릭 이벤트 정의
        self.pb_searchTab.clicked.connect(self.searchTab)
        self.pb_CreInd.clicked.connect(self.createIndex)
        self.pb_scm_diff.clicked.connect(self.scmDiff)
        self.pb_dailycheck.clicked.connect(self.dailyCheck)

        # LineEdit Enter 이벤트 정의
        self.leTabName.returnPressed.connect(self.searchTab)



    # Dialog 팝업 출력
    def showdialog(self,msg_text,detail_msg_text=""):
        msg = QMessageBox()
        msg.setIcon(QMessageBox.Information)

        msg.setText(msg_text)
        # msg.setInformativeText("This is additional information")
        msg.setWindowTitle("MessageBox")
        msg.setDetailedText(str(detail_msg_text))
        msg.setStandardButtons(QMessageBox.Ok | QMessageBox.Cancel)
        retval = msg.exec_()



    # SQL Select 처리 및 결과 반환 함수
    def getSqlList(self, listType=1):
        valschegb =""
        valTabNm = self.leTabName.text()
        if self.rb_rdw.isChecked() :
            valTabScm = "rdw"

        if self.rb_adw.isChecked() :
            valTabScm = "adw"

        try:

            if listType in [1,2]:
                con = DBconn.DBconnMy(db_account.MY_RDW_PROD)
                # con = DBconn.DBconnMy(db_account.MY_ADW_PROD)

                with con.dbcursor as cur:

                    if listType == 1:
                        #MySQL 테이블의 컬럼정보 조회
                        qrystr = TabDiffSqlMap.SELECT_MY_TAB_COLUMN

                    elif listType == 2:
                        # MySQL 테이블의 인덱스컬럼 정보 조회
                        qrystr = TabDiffSqlMap.SELECT_MY_IND_COLUMN

                    cur.execute(qrystr.format(valTabNm.upper()))
                    rows = cur.fetchall()
            elif listType in [3,4,5]:

                con = DBconn.DBconnOra(db_account.ORA_DBKJP_PROD)
                with con.dbcursor as cur:

                    if listType == 3:
                        qrystr = TabDiffSqlMap.SELECT_ORA_TAB_COLUMN

                    elif listType == 4:
                        qrystr = TabDiffSqlMap.SELECT_ORA_IND_COLUMN

                    elif listType == 5:
                        qrystr = TabDiffSqlMap.SELECT_MY_CRE_IND

                    cur.execute(qrystr.format(valTabNm.upper()))
                    rows = cur.fetchall()

            elif listType in [1001,1002,1003]:
                if listType == 1001:
                    valschegb = "dev"
                    if valTabScm == "rdw" :
                        con = DBconn.DBconnMy2(db_account.MY_RDW_DEV)

                    elif valTabScm == "adw":
                        con = DBconn.DBconnMy2(db_account.MY_ADW_DEV)

                elif listType == 1002:
                    valschegb = "qa"
                    if valTabScm == "rdw":
                        con = DBconn.DBconnMy2(db_account.MY_RDW_QA)

                    elif valTabScm == "adw":
                        con = DBconn.DBconnMy2(db_account.MY_ADW_QA)

                elif listType == 1003:
                    valschegb = "prod"
                    if valTabScm == "rdw":
                        con = DBconn.DBconnMy2(db_account.MY_RDW_PROD)

                    elif valTabScm == "adw":
                        con = DBconn.DBconnMy2(db_account.MY_ADW_PROD)


        
                with con.dbcursor as cur:
                    #MySQL Dev,QA,Prod 스키마 구조 조회
                    qrystr = TabDiffSqlMap.SELECT_MY_SCM_TAB_COLUMN

                    cur.execute(qrystr.format(valschegb,valTabScm))
                    rows = cur.fetchall()



        except Exception as e:
            print("Exception 발생 : ", e);
            self.showdialog("GetSqlList Exception 발생",e)
            return ""

        finally:
            con.close()
            con = None

        return rows

    # SQL Select 처리 및 결과 반환 함수
    def getConnInfo(self, conn_info):
        valschegb = ""
        valTabNm = self.leTabName.text()


        try:
            con = DBconn.DBconnMy2(conn_info)
            with con.dbcursor as cur:

                # MySQL 테이블의 컬럼정보 조회
                qrystr = TabDiffSqlMap.SELECT_DAILY_CHECK
                cur.execute(qrystr)
                rows = cur.fetchall()

        except Exception as e:
            print("Exception 발생 : ", e);
            self.showdialog("GetSqlList Exception 발생", e)
            rows = None
            # sys.exit(app.exec())
        finally:
            con.close()
            con = None


        return rows

    # 테이블 구조 비교 버튼 이벤트 처리
    def searchTab(self):
        tblTabCmpList = self.tblwTabCmp
        tblTabCmpList.setRowCount(0)
        tblIndCmpList = self.tblwIndCmp
        tblIndCmpList.setRowCount(0)
        teIndScrt = self.teIndScript

        try:
            # MySQL 컬럼 데이터 조회
            rows = self.getSqlList(1)

            tblTabCmpList.setRowCount(len(rows)+1)
            rownum = 0
            for row in rows:
                item_0 = QTableWidgetItem("")

                tblTabCmpList.setItem(rownum, 0, QTableWidgetItem(row.get("ordinal_position")))
                tblTabCmpList.setItem(rownum, 1, QTableWidgetItem(row.get("column_name")))
                tblTabCmpList.setItem(rownum, 2, QTableWidgetItem(row.get("column_type")))

                rownum += 1

            # 오라클 컬럼 데이터 조회
            rows = self.getSqlList(3)

            # tblTabCmpList.setRowCount(len(rows))
            rownum = 1
            colname_diff_cnt = 0
            coltype_diff_cnt = 0

            for row in rows:
                item_0 = QTableWidgetItem("")

                tblTabCmpList.setItem(rownum, 3, QTableWidgetItem(row[1].lower()))
                tblTabCmpList.setItem(rownum, 4, QTableWidgetItem(row[3].lower()))
                if  tblTabCmpList.item(rownum,1).text() == row[1].lower():
                    tblTabCmpList.setItem(rownum, 5, QTableWidgetItem("O"))
                else:
                    tblTabCmpList.setItem(rownum, 5, QTableWidgetItem("X"))
                    # print(tblTabCmpList.item(rownum, 1).text()+","+ row[1].lower())
                    colname_diff_cnt += 1

                if tblTabCmpList.item(rownum,2).text() == row[3].lower():
                    tblTabCmpList.setItem(rownum, 6, QTableWidgetItem("O"))
                else:
                    tblTabCmpList.setItem(rownum, 6, QTableWidgetItem("X"))
                    # print(tblTabCmpList.item(rownum, 2).text() + "," + row[3].lower())
                    coltype_diff_cnt += 1


                rownum += 1

            # 비교 결과 입력
            tblTabCmpList.setItem(rownum, 1, QTableWidgetItem("오류 컬럼수"))
            tblTabCmpList.setItem(rownum, 5, QTableWidgetItem(str(colname_diff_cnt)))
            tblTabCmpList.setItem(rownum, 6, QTableWidgetItem(str(coltype_diff_cnt)))

            # 작업 후 그리드 처리
            tblTabCmpList.resizeColumnsToContents()

            # Edit하지 않도록 수정(default로 수정 가능함)
            tblTabCmpList.setEditTriggers(QtWidgets.QAbstractItemView.NoEditTriggers)

            ### ORACLE 인덱스 데이터 조회
            rows_4 = self.getSqlList(4) #  oracle 조회

            ### MySQL 인덱스 데이터 조회
            rows_2 = self.getSqlList(2)

            if len(rows_4) > len(rows_2) :
                tblIndCmpList.setRowCount(len(rows_4)+1)
            else :
                tblIndCmpList.setRowCount(len(rows_2)+1)

            rownum = 1

            # 인덱스 전체 컬럼 세팅
            tblIndCmpList.setItem(0, 3, QTableWidgetItem("Ora컬럼수"))
            tblIndCmpList.setItem(0, 4, QTableWidgetItem(str(len(rows_4))))
            for row in rows_4:
                item_0 = QTableWidgetItem("")

                tblIndCmpList.setItem(rownum, 0, QTableWidgetItem(str(row[2])))
                tblIndCmpList.setItem(rownum, 3, QTableWidgetItem(row[1].lower()))
                tblIndCmpList.setItem(rownum, 4, QTableWidgetItem(str(row[2])))
                rownum += 1

            # MySQL 인덱스 데이터 조회 처리


            # tblIndCmpList.setRowCount(len(rows_2))
            rownum = 1
            colname_diff_cnt = 0
            coltype_diff_cnt = 0

            # 인덱스 전체 컬럼 세팅
            tblIndCmpList.setItem(0, 1, QTableWidgetItem("My컬럼수"))
            tblIndCmpList.setItem(0, 2, QTableWidgetItem(str(len(rows_2))))

            for row in rows_2:
                item_0 = QTableWidgetItem("")

                tblIndCmpList.setItem(rownum, 1, QTableWidgetItem(row.get("column_name")))
                tblIndCmpList.setItem(rownum, 2, QTableWidgetItem(str(row.get("seq_in_index"))))

                if tblIndCmpList.item(rownum, 3) is not None and tblIndCmpList.item(rownum, 3).text() == row.get("column_name").lower():
                    tblIndCmpList.setItem(rownum, 5, QTableWidgetItem("O"))
                else:
                    tblIndCmpList.setItem(rownum, 5, QTableWidgetItem("X"))
                    colname_diff_cnt += 1

                if tblIndCmpList.item(rownum,4) is not None and  tblIndCmpList.item(rownum,4).text() == tblIndCmpList.item(rownum,2).text():
                    tblIndCmpList.setItem(rownum, 6, QTableWidgetItem("O"))
                else:
                    tblIndCmpList.setItem(rownum, 6, QTableWidgetItem("X"))
                    coltype_diff_cnt += 1

                rownum += 1

        except Exception as e:
            print("Exception 발생 : ", e);
            self.showdialog("Table 출력 Exception 발생",e)
            # sys.exit(app.exec())
    # 인덱스 재생성 버튼 이벤트 처리
    def createIndex(self):
        teIndScrt = self.teIndScript

        try:

            ### 인덱스 스크립트 생성(오라클 기준)
            rows = self.getSqlList(5)

            teIndScrt.setText("")

            for row in rows:
                teIndScrt.append(str(row[1]).lower())
                teIndScrt.append(str(row[0]).lower())

        except Exception as e:
            print("Exception 발생 : ", e);
            self.showdialog("Create Index  Exception 발생",e)
            # sys.exit(app.exec())

    # 스키마 비교 버튼 이벤트 처리
    def scmDiff(self):
        tblChmDiff = self.tblchmdiff

        try:

            con = DBconn.DBconnSql('c:/testdb.db')

            c = con.dbcursor

            ## 테이블 초기화
            c.execute(TabDiffSqlMap.CREATE_SQLT_TAB1)
            c.execute(TabDiffSqlMap.CREATE_SQLT_TAB2)

            c.execute(TabDiffSqlMap.DELETE_SQLT_TAB1)
            c.execute(TabDiffSqlMap.DELETE_SQLT_TAB2)

            con.commit()




            ### 개발 스키마 가져오기기
            rows = self.getSqlList(1001)
            # print(rows)
            c.executemany(TabDiffSqlMap.INSERT_SQLT_TAB1, rows)

            con.commit()

            ### QA 스키마 가져오기기
            rows = self.getSqlList(1002)
            c.executemany(TabDiffSqlMap.INSERT_SQLT_TAB1, rows)
            con.commit()


            ### 운영 스키마 가져오기기
            rows = self.getSqlList(1003)
            c.executemany(TabDiffSqlMap.INSERT_SQLT_TAB1, rows)

            con.commit()

            ### 기준정보 Imsert
            c.execute(TabDiffSqlMap.INSERT_SQLT_TAB2)

            con.commit()


            ### 오류데이터 Insert
            c.execute(TabDiffSqlMap.INSERT_SQLT_TAB3)

            con.commit()

            ## 오류데이터 조회


            c.execute(TabDiffSqlMap.SELECT_SQLT_SCM_DIFF)
            rows = c.fetchall()

            tblChmDiff.setRowCount(len(rows))

            # 그리드 출력
            rownum = 0
            for row in rows:
                item_0 = QTableWidgetItem("")

                tblChmDiff.setItem(rownum, 0, QTableWidgetItem(row[0]))
                tblChmDiff.setItem(rownum, 1, QTableWidgetItem(row[1]))
                tblChmDiff.setItem(rownum, 2, QTableWidgetItem(str(row[2])))
                tblChmDiff.setItem(rownum, 3, QTableWidgetItem(str(row[3])))
                tblChmDiff.setItem(rownum, 4, QTableWidgetItem(row[4]))
                tblChmDiff.setItem(rownum, 5, QTableWidgetItem(row[5]))
                tblChmDiff.setItem(rownum, 6, QTableWidgetItem(row[6]))
                tblChmDiff.setItem(rownum, 7, QTableWidgetItem(str(row[7])))
                tblChmDiff.setItem(rownum, 8, QTableWidgetItem(row[8]))
                tblChmDiff.setItem(rownum, 9, QTableWidgetItem(row[9]))
                tblChmDiff.setItem(rownum, 10, QTableWidgetItem(row[10]))
                tblChmDiff.setItem(rownum, 11, QTableWidgetItem(str(row[11])))
                tblChmDiff.setItem(rownum, 12, QTableWidgetItem(row[12]))
                tblChmDiff.setItem(rownum, 13, QTableWidgetItem(row[13]))
                tblChmDiff.setItem(rownum, 14, QTableWidgetItem(row[14]))

                rownum += 1


            con.close()

        except Exception as e:
            print("Exception 발생 : ", e)
            con.close()
            self.showdialog("스키마 비교  Exception 발생",e)
            # sys.exit(app.exec())

    def dailyCheck(self):

        try:
            teExecLog = self.teExecLog
            result_summary = []

            # 실행 결과창 초기화
            teExecLog.setText("")

            hostlist = []

            if self.cb_rdw_adw.isChecked():
                if self.cb_prod.isChecked():

                    #운영 호스트별 수행
                    hostlist += [db_account.MY_RDW_PROD,db_account.MY_RDW_PROD2,db_account.MY_RDW_PROD3
                               ,db_account.MY_ADW_PROD,db_account.MY_ADW_PROD2,db_account.MY_ADW_PROD3]

                if self.cb_qadev.isChecked():
                    #QA, 개발 호스트별 수행
                    hostlist += [db_account.MY_RDW_DEV,db_account.MY_RDW_QA
                               ,db_account.MY_ADW_DEV,db_account.MY_ADW_QA]

            if self.cb_sol.isChecked():
                if self.cb_prod.isChecked():
                    # 운영 호스트별 수행
                    hostlist += [db_account.MY_AML_PROD, db_account.MY_FATCA_PROD, db_account.MY_FDS_PROD,db_account.MY_FDS_PROD2
                                , db_account.MY_FDS_PROD3, db_account.MY_FEP_PROD,db_account.MY_FEP_PROD2
                                , db_account.MY_FEP_PROD3, db_account.MY_SSO_PROD,db_account.MY_SSO_PROD2
                                , db_account.MY_SSO_PROD3, db_account.MY_RM_PROD
                                , db_account.MY_META_PROD, db_account.MY_META_PROD2
                                , db_account.MY_BAT_PROD, db_account.MY_BAT_PROD2, db_account.MY_BAT_PROD3]

                if self.cb_qadev.isChecked():
                    #QA, 개발 호스트별 수행
                    hostlist += [db_account.MY_AML_DEV, db_account.MY_AML_QA, db_account.MY_FATCA_DEV,db_account.MY_FATCA_QA
                               , db_account.MY_FDS_DEV, db_account.MY_FDS_QA, db_account.MY_FEP_DEV, db_account.MY_FEP_QA
                               , db_account.MY_SSO_DEV, db_account.MY_SSO_QA, db_account.MY_RM_DEV, db_account.MY_RM_QA, db_account.MY_META_DEV
                               , db_account.MY_BAT_DEV,db_account.MY_BAT_QA]

            for host in hostlist:
                result_summary.append(self.dailyCheckExec(host,teExecLog))
                time.sleep(1)

            # print (result_summary)
            ## 일일점검 결과 요약 추가
            today = date.today()
            with open("c:\daily_check\daily_check_log_"+today.strftime('%Y-%m-%d')+".txt", "a") as logFile:
                logFile.write("### 일일점검 결과 요약 ###"+"총서버 수 : "+str(len(hostlist))+"개 "+"\n")
                # logFile.write("%15s   %20s   %5s   %5s   %5s  %5s   %5s".format("서버명","호스트명","DB접속", "40%이상 사용","MySQL P 개수","모니터링 P 개수", "ERR 로그건수"))
                # logFile.write("{0}   {1}   {2}   {3}   {4}  {5}   {6}\n".format("서버명".ljust(14," "),"호스트명".ljust(15," "),"DB접속".ljust(8," "), "40%이상 사용".ljust(6," "),"MySQL P 개수".ljust(9," "),"모니터링 P 개수".ljust(9," "), "ERR 로그건수".ljust(7," ")))
                logFile.write("{0}   {1}   {2}   {3}   {4}  {5}   {6}\n".format(preformat("서버명",15),preformat("호스트명",20),preformat("DB접속",10), preformat("df 40%이상 사용",10),preformat("MySQL P 개수",10),preformat("모니터링 P 개수",10), preformat("ERR 로그건수",10)))
                for rst in result_summary:
                    # logFile.write(rst[0] + "\t" + rst[1]+ "\t" + rst[2]+ "\t" + rst[3]+ "\t" + rst[4]+ "\t" + rst[5]+ "\t" + rst[6]+"\n")
                    logFile.write("{0}   {1}   {2}   {3}   {4}  {5}   {6}\n".format(preformat(rst[0],15), preformat(rst[1],20),preformat(rst[2],24),preformat(rst[3],12),preformat(rst[4],15),preformat(rst[5],11),preformat(rst[6],3)))

            ctypes.windll.shell32.ShellExecuteA(0,"open","C:/Program Files(x86)/Notepad++/notepad\+\+.exe",None, None, 1)
            calc = ('C:\windows\system32\\calc.exe')
            ctypes.windll.shell32.ShellExecuteA(0, "", calc, None,None, 1)
            # ctypes.windll.shell32.ShellExecuteA(0, "open", "C:/Program Files(x86)/Notepad++/notepad++.exe","c:/daily_check/daily_check_log_" + today.strftime('%Y-%m-%d') + ".txt",None, 1)




        except Exception as e:
            print("Exception 발생 : ", e)
            self.showdialog("스키마 비교  Exception 발생",e)
            # sys.exit(app.exec())

    def dailyCheckExec(self,dbinfo,teEexeLog):


        try:

            # 점검대상 호스트 정보 출력
            teEexeLog.append("[" + dbinfo[5] + "] 일일점검")
            #점검결과 요약 : 서버명
            cr_sv_name = dbinfo[5]
            #점검결과 요약 : 호스트명
            cr_hostname = dbinfo[0]

            #호스트 정보
            k = paramiko.RSAKey.from_private_key_file("c:/id_rsa_kpesc.pem")
            c = paramiko.SSHClient()
            c.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            c.connect(hostname=dbinfo[0], username="deploy", pkey=k)

            #접속정보 출력
            teEexeLog.append("["+dbinfo[5]+"] connected")
            teEexeLog.append("\r\r")
            #점검결과 요약 : 접속여부
            cr_con_yn = "O"

            #MySQL 접속
            teEexeLog.append("[" + dbinfo[5] + "] MySQL 접속 결과")
            rows = self.getConnInfo(dbinfo)
            if rows == None:
                teEexeLog.append("[" + dbinfo[5] + "] 접속 오류 발생")
            else:
                teEexeLog.append("[" + dbinfo[5] + "] DB 호스트명 조회 : " + rows[0][0])

            teEexeLog.append("\r\r")

            teEexeLog.append("[" + dbinfo[5] + "] disk 40% 이상 사용")
            stdin, stdout, stderr = c.exec_command("df -Pk|awk 'int($2) != 0' |grep -v Mounted | awk 'int($3*100/$2) > 39 {print $6 , $5}'")
            stdout_str = str(stdout.read().decode('ascii').strip("\n"))
            teEexeLog.append(stdout_str)
            teEexeLog.append("\r\r")

            # 점검결과 요약 : 디스크 사용량 40% 이상 개수
            cr_disk_usage = stdout_str.count("\n")
            if len(stdout_str) > 0:
                cr_disk_usage += 1

            #df -h 출력
            teEexeLog.append("["+dbinfo[5]+"] df -h 결과 출력")
            stdin, stdout, stderr = c.exec_command("df -h")
            teEexeLog.append(str(stdout.read().decode('ascii').strip("\n")))
            teEexeLog.append("\r\r")



            # MySQL 프로세스 확인
            teEexeLog.append("[" + dbinfo[5] + "] MySQL 프로세스 출력")
            stdin, stdout, stderr = c.exec_command("sudo -s ps -ef | grep '/db/mysql/bin' | grep -v grep")
            stdout_str = str(stdout.read().decode('ascii').strip("\n"))
            teEexeLog.append(stdout_str)
            teEexeLog.append("\r\r")

            # 점검결과 요약 :  MySQL 프로세스 개수
            cr_my_proc_cnt = stdout_str.count("\n")
            if len(stdout_str) > 0:
                cr_my_proc_cnt += 1

            # MySQL 모니터링 프로세스
            teEexeLog.append("[" + dbinfo[5] + "] MySQL 모니터링 프로세스 출력")
            stdin, stdout, stderr = c.exec_command("sudo -s ps -ef | grep mysqld_exporter | grep -v grep")
            stdout_str = str(stdout.read().decode('ascii').strip("\n"))
            teEexeLog.append(stdout_str)
            teEexeLog.append("\r\r")

            # 점검결과 요약 :  MySQL 모니터링 개수
            cr_my_mon_cnt = stdout_str.count("\n")
            if len(stdout_str) > 0:
                cr_my_mon_cnt += 1


            # MySQL Error Log 출력
            teEexeLog.append("[" + dbinfo[5] + "] MySQL Error로그 출력")
            #출력 일자 지정
            now = time.localtime()



            #월요일은 금토일월
            if now.tm_wday == 0 :
                today = date.today()
                dm1 = date.today() - timedelta(1)
                dm2 = date.today() - timedelta(2)
                dm3 = date.today() - timedelta(3)

                log_date_list = [dm3.strftime('%Y-%m-%d'),dm2.strftime('%Y-%m-%d'),dm1.strftime('%Y-%m-%d'),today.strftime('%Y-%m-%d')]

            else:
                # 그 외 전일 당일
                today = date.today()
                dm1 = date.today() - timedelta(1)
                log_date_list = [dm1.strftime('%Y-%m-%d'),today.strftime('%Y-%m-%d')]

            err_log_cnt = 0
            for log_date in log_date_list :
                stdin, stdout, stderr = c.exec_command("sudo -s tail -n 10000000 /log/err-log/mysql.err  | grep -v 'Event Scheduler' | grep '"+log_date+"'")

                stdout_str = str(stdout.read().decode('utf-8',errors="ignore").strip("\n"))
                teEexeLog.append(stdout_str)
                # 에러로그 Error 개수
                err_log_cnt += stdout_str.count("[ERROR]")

            teEexeLog.append("\r\r")
            cr_err_cnt = str(err_log_cnt)

            with open("c:\daily_check\daily_check_log_"+today.strftime('%Y-%m-%d')+".txt", "w") as logFile:
                logFile.write(str(teEexeLog.toPlainText()))


            # return [cr_sv_name,cr_hostname,cr_con_yn,str(cr_disk_usage),str(cr_my_proc_cnt),str(cr_my_mon_cnt),cr_err_cnt]



        except Exception as e:
            print("Exception 발생 : ", e)
            self.showdialog("데일리체크  Exception 발생", e)
            teEexeLog.append("Error : " + e)
        finally:
            return [cr_sv_name, cr_hostname, cr_con_yn, str(cr_disk_usage), str(cr_my_proc_cnt), str(cr_my_mon_cnt),cr_err_cnt]


if __name__ == "__main__":
    import sys
    app = QApplication(sys.argv)
    mywin = MyWindow()
    mywin.show()
    sys.exit(app.exec())