import psycopg2
import configparser

configParser = configparser.RawConfigParser()   
configFilePath = r'config.txt'
configParser.read(configFilePath)

class DBAccess:

  @staticmethod
  def Get_DB():
      con = psycopg2.connect(user = configParser.get('my-config', 'user'),
                              password = configParser.get('my-config', 'password'),
                              host = configParser.get('my-config', 'host'),
                              port = configParser.get('my-config', 'port'),
                              database = configParser.get('my-config', 'database'))
      return con
  
  @staticmethod
  def ExecuteSQL(sql, vars=None):
      db_connection = DBAccess.Get_DB()
      cursor = db_connection.cursor()
      if(vars == None):
          cursor.execute(sql)
      else:
          cursor.execute(sql,vars)
      
      if(cursor.rowcount==1):
          return cursor.fetchone()
      elif(cursor.rowcount>1):
          entries = cursor.fetchall()
          return entries
      else:
              db_connection.commit()
      return None

  @staticmethod
  def GetSequencerNextVal(seq):
      db_connection = DBAccess.Get_DB()
      cursor = db_connection.cursor()
      sql = 'select nextval(\'%s\')' % seq
      cursor.execute(sql)
      return cursor.fetchone()
