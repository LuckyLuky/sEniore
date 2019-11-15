import os
import configparser
import cloudinary as Cloud
import requests
import cloudinary.uploader
from pathlib import Path


def GetCoordinates(address):
    api_key = getGoogleAPIKey()
    api_response = requests.get(
        "https://maps.googleapis.com/maps/api/geocode/json?address={0}&key={1}".format(
            address, api_key
        )
    )
    api_response_dict = api_response.json()
    latitude = api_response_dict["results"][0]["geometry"]["location"]["lat"]
    longitude = api_response_dict["results"][0]["geometry"]["location"]["lng"]
    return (latitude, longitude)


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


def UploadImage(filePath):
    fileName = Path(filePath).stem
    Cloud.uploader.upload(filePath, width=150, height=150, crop="limit", public_id=fileName)


def GetImageUrl(userId):
    return Cloud.CloudinaryImage(str(userId)).url