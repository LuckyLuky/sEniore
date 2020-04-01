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
from enum import Enum
import traceback, sys
from functools import wraps
import time
from datetime import datetime
import inspect



def GetConfigValue(value):
    result = os.environ.get(value)
    if not result:
        configParser = configparser.RawConfigParser()
        configFilePath = r"config.txt"
        configParser.read(configFilePath)
        result = configParser.get("my-config", value)
    if not result:
        raise Exception(f"Could not find {value} key in enviroment/config file.")
    return result

def getSecretKey():
    return GetConfigValue("SECRET_KEY")
    
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
    return GetConfigValue("GOOGLE_API_KEY")
    
def CloudinaryConfigure():
    cloudName = GetConfigValue("CLOUDINARY_CLOUD_NAME")
    apiKey =  GetConfigValue("CLOUDINARY_API_KEY")
    apiSecret = GetConfigValue("CLOUDINARY_API_SECRET")
    
    Cloud.config(
      cloud_name=cloudName,
      api_key=apiKey,
      api_secret=apiSecret
      )

def UploadImagePrivate(filePath,public_id):
    response = Cloud.uploader.upload(
    filePath,
    width=450,
    height=450,
    crop="limit",
    invalidate=True,
    type='private',
    public_id=public_id)
    return response['url']

def UploadImageRandom(filePath):
    return Cloud.uploader.upload(
      filePath,
      width=450,
      height=450,
      crop="limit",
      invalidate=True)

def UploadImage(filePath, public_id,):
    return Cloud.uploader.upload(
      filePath,
      width=450,
      height=450,
      crop="limit",
      public_id=public_id,
      invalidate=True)

def RenameImage(oldId, newId):
    Cloud.uploader.rename(
      oldId,
      newId,
      invalidate=True,
      overwrite = True)

def RenameImageToPrivate(oldId, newId):
    response  = Cloud.uploader.rename(
      oldId,
      newId,
      invalidate=True,
      overwrite = True,
      to_type='private')
    return response

def DeleteImage(public_id):
    return Cloud.uploader.destroy(
      public_id,
      invalidate=True)

def SetImagePrivate(public_id):
    try:
        response = Cloud.uploader.rename(public_id,public_id,to_type='private', overwrite= True, invalidate=True)
        return response['type']
    except Exception as identifier:
        return identifier.args[0]
 
def GetImageUrl(userId, version=None):
    #return Cloud.CloudinaryImage(str(userId),version = version).url
    httpUrl =  Cloud.CloudinaryImage(str(userId),version = version).url
    httpsUrl = httpUrl.replace('http','https')
    return httpsUrl   

def getEmailAPIKey():
     return GetConfigValue("SENDGRID_API_KEY")

def GetEmail(configKey):
    emailString = GetConfigValue(configKey)
    array = emailString.split(';')
    if len(array)==1:
        return array[0]
    else:
        return array
 
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