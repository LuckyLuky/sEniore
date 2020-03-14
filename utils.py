import os
import configparser
import cloudinary as Cloud
import requests
import cloudinary.uploader
from pathlib import Path
from sendgrid import SendGridAPIClient
from sendgrid.helpers.mail import Mail
from dbaccess import DBUser
from flask import redirect,url_for, flash as flaskFlash, current_app as app, abort
from enum  import Enum
import traceback, sys
from functools import wraps
import time
from datetime import datetime
import inspect

def getSecretKey():
    SECRET_KEY = os.environ.get("SECRET_KEY")
    if not SECRET_KEY:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        SECRET_KEY = configParser.get("my-config", "SECRET_KEY")
    if not SECRET_KEY:
        raise Exception("Could not find SECRET_KEY value.")
    return SECRET_KEY


def GetCoordinates(address):
    api_key = getGoogleAPIKey()
    api_response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(
            address, api_key
        )
    )
    api_response_dict = api_response.json()
    try:

        latitude = api_response_dict["results"][0]["geometry"]["location"]["lat"]
        longitude = api_response_dict["results"][0]["geometry"]["location"]["lng"]
        return (latitude, longitude)
    except:
        return None



def getGoogleAPIKey():
    API_Key = os.environ.get("GOOGLE_API_KEY")
    if not API_Key:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        API_Key = configParser.get("my-config", "google_api_key")
    if not API_Key:
        raise Exception("Could not find API_Key value.")
    return API_Key


def CloudinaryConfigure():

    cloudName = os.environ.get("CLOUDINARY_CLOUD_NAME")
    if not cloudName:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        cloudName = configParser.get("my-config", "CLOUDINARY_CLOUD_NAME")
    if not cloudName:
        raise Exception("Could not find CLOUDINARY_CLOUD_NAME value.")

    apiKey = os.environ.get("CLOUDINARY_API_KEY")
    if not apiKey:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        apiKey = configParser.get("my-config", "CLOUDINARY_API_KEY")
    if not apiKey:
        raise Exception("Could not find CLOUDINARY_API_KEY value.")

    apiSecret = os.environ.get("CLOUDINARY_API_SECRET")
    if not apiSecret:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        apiSecret = configParser.get("my-config", "CLOUDINARY_API_SECRET")
    if not apiSecret:
        raise Exception("Could not find CLOUDINARY_API_SECRET value.")

    Cloud.config(
      cloud_name=cloudName,
      api_key=apiKey,
      api_secret=apiSecret
      )


def UploadImage(filePath, public_id,):
    return Cloud.uploader.upload(
      filePath,
      width=150,
      height=150,
      crop="limit",
      public_id=public_id,
      invalidate=True)

def RenameImage(oldId, newId):
    Cloud.uploader.rename(
      oldId,
      newId,
      invalidate=True,
      overwrite = True)

def DeleteImage(public_id):
    Cloud.uploader.destroy(
      public_id,
      invalidate=True)


def GetImageUrl(userId, version=None):
    return Cloud.CloudinaryImage(str(userId),version = version).url   

def getEmailAPIKey():
    API_Key = os.environ.get("SENDGRID_API_KEY")
    if not API_Key:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        API_Key = configParser.get("my-config", "sendgrid_api_key")
    if not API_Key:
        raise Exception("Could not find API_Key value.")
    return API_Key

def SendMail(_from, _to, _subject, _text):
    gmailDontCacheHeader = '''<?php
                              header('Content-Type: image/jpeg');
                              header("Cache-Control: no-store, no-cache, must-revalidate, max-age=0");
                              header("Cache-Control: post-check=0, pre-check=0", false);
                              header("Pragma: no-cache"); ?>
                              '''
    message = Mail(
    from_email=_from,
    to_emails=_to,
    subject=_subject,
    html_content=gmailDontCacheHeader + _text)
    try:
        sg = SendGridAPIClient(getEmailAPIKey())
        response = sg.send(message)
        print(response.status_code)
        print(response.body)
        print(response.headers)
    except Exception as e:
        print(e.message)

class FlashStyle(Enum):
    Normal = 'alert alert-primary'
    Success = 'alert alert-success'
    Warning = 'alert alert-warning'
    Danger = 'alert alert-danger'

def flash(text, style):
    flaskFlash(text, style.value)

def LoginRequired(level= 1):
    try:
        def LoginRequiredInner(function):
            @wraps(function)
            def decorated_function(*args, **kwargs):
                dbUser = DBUser.LoadFromSession('dbUser')
                if dbUser is None :
                    flash('Nejste přihlášeni, pro přístup je nutné se přihlásit.',FlashStyle.Danger)
                    return redirect(url_for("login_bp.login"))
                elif dbUser.level<level :
                    abort(403)
                return function(*args, **kwargs)
            return decorated_function
        return LoginRequiredInner
            
                
          
    except RuntimeError:
        (t, v, tb) = sys.exc_info()
        tracebacks = "".join(traceback.format_exception(t, v, tb))
        return lambda :  tracebacks



    