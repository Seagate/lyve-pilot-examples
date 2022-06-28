#!/usr/bin/python3
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

# This script is intended to run through some basic common use cases. Some
# unused variables have been left in as a suggestion as to how to organize
# input information. The file pilotUtils.js presents an alternate way to 
# organize endpoints and variables
UUID = '<UUID>' #sys.argv[1] 
HOST = 'pilot.lyve.seagate.com/' + UUID
USERNAME = '<email address>' #sys.argv[2]
PASSWORD = '<password>' #sys.argv[3]

# Define API URLs
VOLUMES_URL = 'https://{}/udx/v1/volumes'.format(HOST)#, CUSTOMER_UUID)
DEVICES_URL = 'https://{}/udx/v1/devices'.format(HOST)#, CUSTOMER_UUID)
IMPORT_URL = 'https://{}/udx/v1/import'.format(HOST)#, CUSTOMER_UUID)
ACTIVITY_URL = 'https://{}/udx/v1/activity'.format(HOST)#, CUSTOMER_UUID)

# Name of the new user
name = 'name'

new_user_data = {
    "email": "email@organization.com",
    "role": "admin",
    "language": "EN",
    "location": "333 my address",
    "name": name,
    "phone": "123-456-7890"
  }


# Get login token. Return is a string containing the jwt login token. Expires after
# 10 miniutes. Can be modified to return refresh token

pilotUtils.print_bold('\n----- LOGIN -----')
token = pilotUtils.login(HOST, USERNAME, PASSWORD)['token'] # This object is the initial login jwt
                                                            # The refresh token can be found with the 
                                                            # key 'refreshToken'



# Prints a list of the names of all users in the customer instance
# Output is an array of strings
pilotUtils.print_bold('\n----- USERS -----')
response_data = pilotUtils.get_users(HOST, token)
for i in response_data['data']:
  print(i['name'])


# Creates a new user in the customer instance. This returns a json object containing
# new user information incliding the OTC. This user is not valid yet and must accept the EULA
# using the OTC pulled from the return object
pilotUtils.print_bold('\n ----- CREATE USER -----')
new_user_JSON = pilotUtils.new_user(HOST, token, new_user_data) # OTC will be used to finalize user creation and set password
print(new_user_JSON)


# ID's for users are long and randomly generated. This function will return the ID
# as a string when given the user's name
user_ID = pilotUtils.id_from_username(HOST, token, name)
pilotUtils.print_bold('\n ----- USER ID -----')
print('User ID: ', user_ID)


# This function pulls the OTC from the returned json object from the function piloutUtils.create_user().
# The OTC expires after one week and must be used to accept the EULA
OTC = int(new_user_JSON['user']['OTC']) # Pulls OTC from JSON and converts to integer for openapi validation
print('OTC: ', OTC)


# Uses the OTC object to accept the EULA. The return is a json object containing a login token
# which can be used to login the new user for the first time. Upon first time login, the new
# user must set a password
EULA_response = pilotUtils.accept_EULA(HOST, OTC, 'name@seagate.com')
EULA_token = EULA_response['token']
print('EULA Token: ', EULA_token)


# Sets the new user password as the string passed to the function
# Returns a jwt login token used to login normally. This will only need to be
# performed once
new_user_login = pilotUtils.first_password_set(HOST, EULA_token, '<new user password>')['token']
print('New User Login Token: ', new_user_login)



pilotUtils.print_bold('\n----- Change Phone Number -----')

patch_user_data = {
    "email": "email@organization.com",
    "role": "admin",
    "language": "EN",
    "location": "333 my address",
    "name": 'name',
    "phone": "111-222-3333"
  }

# This is a one off use of the patch_helper functions found in pilotUtils.py. User ID must be added to 
# URL in order to isolate specific user
pilotUtils.patch_helper(new_user_login, 'https://{}/udx/v1/users/{}'.format(HOST, user_ID), patch_user_data)

# Fetches a single user json object for a specific user. Uses pilotUtils.id_from_username() 
# to identify user from username
single_user = pilotUtils.get_user(HOST, token, name)
print('User Data for', name, ':', single_user)

# This is a one off use of the delete_helper function found in pilotUtils.py
delete_check = pilotUtils.delete_helper(token, 'https://{}/udx/v1/users/{}'.format(HOST, user_ID))
if delete_check.status_code == 200:
  print('Successfully deleted user ', user_ID)
else:
  print('<error message>')

# Pulls feed from customer instance as json objects. Can be parsed along any lines
# considered useful
pilotUtils.print_bold('\n----- Get Feed -----')
feed = pilotUtils.get_helper(token, 'https://{}/udx/v1/feed'.format(HOST), None)
print('Feed Data: ', feed)