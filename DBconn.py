import pymysql.cursors
import sqlite3
import cx_Oracle

class DBconnMy:

    def __init__(self,arg):

        self.dbconection = pymysql.connect(host=arg[0],
                                           port=arg[1],
                                           db=arg[2],
                                           user=arg[3],
                                           passwd=arg[4],
                                           cursorclass = pymysql.cursors.DictCursor)

        self.dbcursor = self.dbconection.cursor()

    def commit(self):
        self.dbconection.commit()

    def close(self):
        self.dbcursor.close()
        self.dbconection.close()

class DBconnMy2:

    def __init__(self,arg):

        self.dbconection = pymysql.connect(host=arg[0],
                                           port=arg[1],
                                           db=arg[2],
                                           user=arg[3],
                                           passwd=arg[4])

        self.dbcursor = self.dbconection.cursor()

    def commit(self):
        self.dbconection.commit()

    def close(self):
        self.dbcursor.close()
        self.dbconection.close()

class DBconnOra:

    def __init__(self,arg):

        self.dbconection = cx_Oracle.connect(arg[3] + "/" + arg[4]+ "@" + arg[0] + ":" + str(arg[1]) + "/" + arg[2])

        self.dbcursor = self.dbconection.cursor()

    def commit(self):
        self.dbconection.commit()

    def close(self):
        # self.dbcursor.close()
        self.dbconection.close()



class DBconnSql:

    def __init__(self,filename):
        self.dbconection = sqlite3.connect(":memory:")

        self.dbcursor = self.dbconection.cursor()

    def commit(self):
        self.dbconection.commit()

    def close(self):
        # self.dbcursor.close()
        self.dbconection.close()