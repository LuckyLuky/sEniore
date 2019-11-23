import os
import psycopg2
import configparser
from jsonpickle import encode, decode
from flask import session

class DBUser():
    id = None
    first_name  = None
    surname = None
    email  = None
    street = None
    street_number  = None
    post_code = None
    town  = None
    telephone = None
    info = None
    password = None
    salt = None
    latitude = None
    longitude  = None
    level = None
    
    def SaveToSession(self, sessionKey):
        session[sessionKey] = encode(self)

    @classmethod
    def LoadFromSession(cls, sessionKey):
        if(sessionKey in session):
            return decode(session[sessionKey])
        return None
    
    def InsertDB(self):
        DBAccess.ExecuteInsert(
        """insert into users (id, first_name, surname, email, street,
        streetNumber, town, postCode, telephone, password, salt,
        level, latitude,longitude, info)
     values (%s, %s, %s, %s, %s, %s,%s, %s, %s,%s,%s,%s, %s, %s, %s)""",
        (
            self.id,
            self.first_name,
            self.surname,
            self.email,
            self.street,
            self.street_number,
            self.town,
            self.post_code,
            self.telephone,
            self.password,
            self.salt,
            self.level,
            self.latitude,
            self.longitude,
            self.info
        )
    )




class DBAccess:
    @classmethod   # method which return object from class DBUser, ie I get specific user from db
    def GetDBUserById(cls, id):
        user = DBAccess.ExecuteSQL(
            "select id, first_name,surname,email,street,streetnumber, postcode,town,telephone,info,password,salt,latitude,longitude,level from users where id=%s",(id,))
        if len(user)==0:
          return None
        user = user[0]  # returns [()], I need ()
        dbUser = DBUser()
        dbUser.id=user[0]
        dbUser.first_name = user[1]
        dbUser.surname = user[2]
        dbUser.email = user[3]
        dbUser.street = user[4]
        dbUser.street_number = user[5]
        dbUser.postCode = user[6]
        dbUser.town = user[7]
        dbUser.telephone = user[8]
        dbUser.info = user[9]
        dbUser.password = user[10]
        dbUser.salt = user[11]
        dbUser.latitude = user[12]
        dbUser.longitude = user[13]
        dbUser.level = user[14]
        return dbUser


    @staticmethod
    def Get_DB_URL():
        database_url = os.environ.get("DATABASE_URL")
        if not database_url:
            configParser = configparser.RawConfigParser()
            configFilePath = r"config.txt"
            configParser.read(configFilePath)
            database_url = configParser.get("my-config", "database_url")
        if not database_url:
            raise Exception("Could not find database url configuration.")
        return database_url

    @staticmethod
    def Get_DB():
        return psycopg2.connect(DBAccess.Get_DB_URL())

    @staticmethod
    def ExecuteSQL(sql, vars=None):
        db_connection = DBAccess.Get_DB()
        cursor = db_connection.cursor()
        if vars is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, vars)

        # if(cursor.rowcount==1):
        #     return cursor.fetchone()
        if cursor.rowcount > 0:
            entries = cursor.fetchall()
            return entries
        else:
            db_connection.commit()
        return None

    @staticmethod
    def ExecuteScalar(sql, vars=None):
        db_connection = DBAccess.Get_DB()
        cursor = db_connection.cursor()
        if vars is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, vars)
        if cursor.rowcount > 0:
            return cursor.fetchone()[0]
        return None

    @staticmethod
    def ExecuteInsert(sql, vars=None):
        db_connection = DBAccess.Get_DB()
        cursor = db_connection.cursor()
        if vars is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, vars)
        db_connection.commit()
        return None

    @staticmethod
    def ExecuteUpdate(sql, vars=None):
        db_connection = DBAccess.Get_DB()
        cursor = db_connection.cursor()
        if vars is None:
            cursor.execute(sql)
        else:
            cursor.execute(sql, vars)
        db_connection.commit()
        return None

    @staticmethod
    def GetSequencerNextVal(seq):
        db_connection = DBAccess.Get_DB()
        cursor = db_connection.cursor()
        sql = f"select nextval('{seq}')"
        cursor.execute(sql)
        return cursor.fetchone()[0]
