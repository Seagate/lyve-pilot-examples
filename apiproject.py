#!/usr/bin/python
# Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates

# Permission is hereby granted, free of charge, to any person obtaining a copy 
# of this software and associated documentation files (the "Software"), to 
# deal in the Software without restriction, including without limitation the 
# rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
# sell copies of the Software, and to permit persons to whom the Software is 
# furnished to do so, subject to the following conditions:

# The above copyright notice and this permission notice shall be included in 
# all copies or substantial portions of the Software.

# THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
# IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
# FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
# AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
# LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
# FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
# DEALINGS IN THE SOFTWARE.

# IMPORTS #
import sys
import pilotUtils

import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning) #Disables warning for not verifying local user. Production will use UUID, dev does not

# if len(sys.argv) != 4:
#   print('ERROR: usage {} <customer-ID> <username> <password>'.format(sys.argv[0]))
#   sys.exit(1)

HOST = 'aptest.colo.seagate.com:32324'
CUSTOMER_UUID = '' #'624f6357f47dcc0012126300' #sys.argv[1] # specific instance UUID
USERNAME = 'admin@seagate.com' #sys.argv[2]
PASSWORD = '389LyvePilot' #sys.argv[3]

# Define API URLs
VOLUMES_URL = 'https://{}/udx/v1/volumes'.format(HOST)#, CUSTOMER_UUID)
DEVICES_URL = 'https://{}/udx/v1/devices'.format(HOST)#, CUSTOMER_UUID)
IMPORT_URL = 'https://{}/udx/v1/import'.format(HOST)#, CUSTOMER_UUID)
ACTIVITY_URL = 'https://{}/udx/v1/activity'.format(HOST)#, CUSTOMER_UUID)

def getActivity(jwt, filterParams):
  return pilotUtils.getHelper(jwt, ACTIVITY_URL, filterParams)

def getDevices(jwt):
  return pilotUtils.getHelper(jwt, DEVICES_URL, {})  

def getVolumes(jwt, filterParams):
  return pilotUtils.getHelper(jwt, VOLUMES_URL, filterParams) 

def importData(jwt, sourceUri, destinationUri, destDeviceId, filterStr='*'):
  reqData = {
    'sourceUri': str(sourceUri),
    'destinationUri': str(destinationUri),
    'filter': filterStr,
    'deviceId': str(destDeviceId),
    'orchestrationMode': 'STANDARD_SECURITY'
  }
  return pilotUtils.postHelper(jwt, IMPORT_URL, reqData)

# Get login token
pilotUtils.printBold('\n----- LOGIN -----')
token = pilotUtils.login(HOST, USERNAME, PASSWORD)['token']
# print(token)

# pilotUtils.printBold('\n----- DEVICES -----')
# devices = getDevices(token)
# deviceID = getDevices(token)['data'][0]['_id'];
# print(deviceID);
# pilotUtils.printJson(devices);

pilotUtils.printBold('\n----- USERS -----')
responseData = pilotUtils.getUsers(HOST, token)
for i in responseData['data']:
  print(i['name'])
  print('\n')




# Change user's phone number. Must provide either name or id number. If given only id
# number, name must be an empty string

# pilotUtils.printBold('\n----- change phone# -----')
# pilotUtils.setPhonenumber(HOST, token, 'Administrator', '')




# # Build import parameters by getting volume info
# sourceVolume = getVolumes(token, { 'category': 'NON-UDX' })
# destVolume = getVolumes(token, { 'category': 'UDX' })

# # Setup an import task
# sourceUri = sourceVolume['data'][0]['uri']
# destUri = destVolume['data'][0]['uri']
# destDeviceId = destVolume['data'][0]['deviceId']

# print('  source = {}, destination = {}'.format(sourceUri, destUri))

# # Issue Import
# importTask = importData(token, sourceUri, destUri, destDeviceId)

# pilotUtils.printJson(importTask)