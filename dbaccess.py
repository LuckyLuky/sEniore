import os
import psycopg2
import configparser


class DBAccess:


  @staticmethod
  def Get_DB_URL():
    database_url = os.environ.get('DATABASE_URL')
    if not database_url:
      configParser = configparser.RawConfigParser()   
      configFilePath = r'config.txt'
      configParser.read(configFilePath)
      database_url = configParser.get('my-config', 'database_url')
    if not database_url:
      raise Exception('Could not find database url configuration.')
    return database_url

  @staticmethod
  def Get_DB():
      return psycopg2.connect(DBAccess.Get_DB_URL())
  
  @staticmethod
  def ExecuteSQL(sql, vars=None):
      db_connection = DBAccess.Get_DB()
      cursor = db_connection.cursor()
      if(vars == None):
          cursor.execute(sql)
      else:
          cursor.execute(sql,vars)
      
      # if(cursor.rowcount==1):
      #     return cursor.fetchone()
      if(cursor.rowcount>0):
          entries = cursor.fetchall()
          return entries 
      else:
              db_connection.commit()
      return None
  
  @staticmethod
  def ExecuteScalar(sql, vars=None):
      db_connection = DBAccess.Get_DB()
      cursor = db_connection.cursor()
      if(vars == None):
          cursor.execute(sql)
      else:
          cursor.execute(sql,vars)
      if(cursor.rowcount>0):
        return cursor.fetchone()[0]
      return None

  @staticmethod
  def ExecuteInsert(sql, vars=None):
      db_connection = DBAccess.Get_DB()
      cursor = db_connection.cursor()
      if(vars == None):
          cursor.execute(sql)
      else:
          cursor.execute(sql,vars)
      db_connection.commit()
      return None

  @staticmethod
  def GetSequencerNextVal(seq):
      db_connection = DBAccess.Get_DB()
      cursor = db_connection.cursor()
      sql = 'select nextval(\'%s\')' % seq
      cursor.execute(sql)
      return cursor.fetchone()
