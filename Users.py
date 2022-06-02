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

HOST = 'aptest.colo.seagate.com:32324'
CUSTOMER_UUID = '' #'624f6357f47dcc0012126300' #sys.argv[1] # specific instance UUID
USERNAME = 'admin@seagate.com' #sys.argv[2]
PASSWORD = '389LyvePilot' #sys.argv[3]

# Define API URLs
VOLUMES_URL = 'https://{}/udx/v1/volumes'.format(HOST)#, CUSTOMER_UUID)
DEVICES_URL = 'https://{}/udx/v1/devices'.format(HOST)#, CUSTOMER_UUID)
IMPORT_URL = 'https://{}/udx/v1/import'.format(HOST)#, CUSTOMER_UUID)
ACTIVITY_URL = 'https://{}/udx/v1/activity'.format(HOST)#, CUSTOMER_UUID)

name = 'name'

new_user_data = {
    "email": "name@seagate.com",
    "role": "admin",
    "language": "EN",
    "location": "333 my address",
    "name": name,
    "phone": "123-456-7890"
  }

def get_activity(jwt, filterParams):
  return pilotUtils.get_helper(jwt, ACTIVITY_URL, filterParams)

def get_devices(jwt):
  return pilotUtils.get_helper(jwt, DEVICES_URL, {})  

def get_volumes(jwt, filterParams):
  return pilotUtils.get_helper(jwt, VOLUMES_URL, filterParams) 

def importData(jwt, sourceUri, destinationUri, destDeviceId, filterStr='*'):
  req_data = {
    'sourceUri': str(sourceUri),
    'destinationUri': str(destinationUri),
    'filter': filterStr,
    'deviceId': str(destDeviceId),
    'orchestrationMode': 'STANDARD_SECURITY'
  }
  return pilotUtils.post_helper(jwt, IMPORT_URL, req_data)

# Get login token
pilotUtils.print_bold('\n----- LOGIN -----')
token = pilotUtils.login(HOST, USERNAME, PASSWORD)['token'] # This object is the initial login jwt
                                                            # The refresh token can be found with the 
                                                            # key 'refreshToken'

input('Press Enter to continue')

# Prints a list of the names of all users in the customer instance
# Should probably rework to return a json object from pilotUtils.getUsers
pilotUtils.print_bold('\n----- USERS -----')
response_data = pilotUtils.get_users(HOST, token)
for i in response_data['data']:
  print(i['name'])

input('Press Enter to continue')

pilotUtils.print_bold('\n ----- CREATE USER -----')
new_user_JSON = pilotUtils.new_user(HOST, token, new_user_data) # OTC will be used to finalize user creation and set password
print(new_user_JSON)

input('Press Enter to continue')

user_ID = pilotUtils.id_from_username(HOST, token, name)
pilotUtils.print_bold('\n ----- USER ID -----')
print('User ID: ', user_ID)

input('Press Enter to continue')

OTC = int(new_user_JSON['user']['OTC']) # Pulls OTC from JSON and converts to integer for openapi validation
print('OTC: ', OTC)

input('Press Enter to continue')

EULA_response = pilotUtils.accept_EULA(HOST, OTC, 'name@seagate.com')
EULA_token = EULA_response['token']
print('EULA Token: ', EULA_token)

input('Press Enter to continue')

new_user_login = pilotUtils.first_password_set(HOST, EULA_token, 'Testit123!')['token']
print('New User Login Token: ', new_user_login)

input('Press Enter to continue')

pilotUtils.print_bold('\n----- Change Phone Number -----')

patch_user_data = {
    "email": "name@seagate.com",
    "role": "admin",
    "language": "EN",
    "location": "333 my address",
    "name": 'name',
    "phone": "111-222-3333"
  }
pilotUtils.patch_helper(new_user_login, 'https://{}/udx/v1/users/{}'.format(HOST, user_ID), patch_user_data) # ~~~~~~~~~~~~~~~~~~~~~~~~ Patch not working because endpoint isn't getting what it thinks it should FIXME

single_user = pilotUtils.get_user(HOST, token, name)
print('User Data for', name, ':', single_user)

input('Press Enter to continue')


delete_check = pilotUtils.delete_helper(token, 'https://{}/udx/v1/users/{}'.format(HOST, user_ID))
if delete_check.status_code == 200:
  print('Successfully deleted user ', user_ID)
else:
  print('Something went wrong')#~~~~~~~~~~~~FIXME

pilotUtils.print_bold('\n----- Get Feed -----')
feed = pilotUtils.get_helper(token, 'https://{}/udx/v1/feed'.format(HOST), None)
print('Feed Data: ', feed)