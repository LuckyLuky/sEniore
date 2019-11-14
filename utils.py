import os
import configparser



def getGoogleAPIKey():
  API_Key = os.environ.get('GOOGLE_API_KEY')
  if not API_Key:
    configParser = configparser.RawConfigParser()   
    configFilePath = r'config.txt'
    configParser.read(configFilePath)
    API_Key = configParser.get('my-config', 'google_api_key')
  if not API_Key:
    raise Exception('Could not find API_Key value.')
  return API_Key