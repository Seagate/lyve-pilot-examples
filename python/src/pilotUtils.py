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

import pprint # Pretty Print for request/response data output
import requests
import json

# Printing helper methods

pp = pprint.PrettyPrinter(indent=2) # Pretty Print object

def print_json(output):
  pp.pprint(output)

def print_bold(output):
  print('\033[1m' + output + '\033[0m')


# Helper method to retrieve objects given a URL and optional filters.
def get_helper(jwt, url, filterParams):
  print_bold('Request: GET {}...'.format(url))
  print('\tFilters: {}'.format(json.dumps(filterParams)))
  headers = { 
    'accept': 'application/json',
    'Authorization': 'Bearer {}'.format(jwt)
  }
  try:
    response = requests.get(url, 
                            headers = headers,
                            params = filterParams)
    response_data = response.json()
    return response_data

  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

# Helper method to perform operations
def post_helper(jwt, url, post_data):

  print_bold('Request: POST {}...'.format(url))
  headers = { 
    'accept': 'application/json',
    'Content-Type': 'application/json',
  }

  if jwt:
    headers['Authorization'] = 'Bearer {}'.format(jwt)

  try:
    response = requests.post(url, 
                            headers = headers,
                            data = json.dumps(post_data))
    response_data = response.json()
    return response_data

  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

# Helper method to perform operations
def delete_helper(jwt, url): # url must be passed with user_ID already in it
  print_bold('Request: DELETE {}'.format(url))
  headers = {
    'accept': 'applications/json',
    'Content-Type': 'application/json',
  }

  if jwt:
    headers['Authorization'] = 'Bearer {}'.format(jwt)

  try:
    response = requests.delete(url,
                               headers = headers,
    )
    return response
  
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

# Helper method to perform operations
def patch_helper(jwt, url, patch_data): # url must be passed with user_ID already in it
  print_bold('Request: PATCH {}'.format(url))
  headers = {
    'accept': 'applications/json',
    'Content-Type': 'application/json',
  }

  if jwt:
    headers['Authorization'] = 'Bearer {}'.format(jwt)

  try:
    response = requests.patch(url,
                               headers = headers,
                               data = json.dumps(patch_data)
    )
    print(response)
    print(response.json())
    return response
  
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

# login(host, username, password) - This currently logs the user in and 
#         returns the entire JSON object which includes the session JWT and a refresh token.
#         The refresh token can be used to refresh the JWT when it expires.
# Input - host: Desired url endpoint (string)
#         username: username (string)
#         password: password (string)
# Output - Returns a json web token that is passed through other functions
#          as a valiidation object. Expires after 10 minutes. Also returns
#          a refresh token in order to extend session

def login(host, username, password):
  LOGIN_URL = 'https://{}/udx/v1/login'.format(host)
  req_data = { 
    'email': username,
    'password': password
  }
  print(LOGIN_URL)
  print(req_data)

  return post_helper(None, LOGIN_URL, req_data)


# new_user(host, jwt, req_data) - This will post a new user to the user list 
#                                 to the customer instance. User will not have
#                                 accepted the EULA yet
# Input - host: Desired url endpoint (string)
#         jwt: json web token returned from login() (string)
#         req_data: json object containing relevant new user information (string)
# Output - Returns a json object containing created user's data. The OTC key will
#          need to be pulled in order to accept EULA and set new user password
def new_user(host, jwt, req_data):
  new_user_URL = 'https://{}/udx/v1/saasUser'.format(host)

  print(new_user_URL)
  print(req_data)

  return post_helper(jwt, new_user_URL, req_data)

# get_users(host, jwt) - Fetches an array of usernames currently
#                        saved to customer instance as strings
# Input - host: Desired url endpoint (string)
#         jwt: json web token from login() (string)
# Output - Returns an array of usernames as strings
def get_users(host, jwt):
  get_user_URL = 'https://{}/udx/v1/users'.format(host)

  user_data = get_helper(jwt, get_user_URL, None)
  return user_data

# get_user(host, jwt, username, user_ID=None) - Fetches the json object
#                                               for one specific user
# Input - host: Desired url endpoint (string)
#         jwt: json web token from login() (string)
#         username: name of user to be fetched. Can be left empty
#                   if user ID is known
#         user_ID: The ID of a user as saved in the user's profile.
#                  If the user ID is not known, username can be passed
#                  and the ID will be found automatically by the function
#                  id_from_username(host, jwt, username)
# Output - Returns a json object containing user information
def get_user(host, jwt, username, user_ID=None):

  if user_ID == None:
    user_ID = id_from_username(host, jwt, username)
  print(user_ID)

  get_user_URL = 'https://{}/udx/v1/users/{}'.format(host, user_ID)

  user_data = get_helper(jwt, get_user_URL, None)

  return user_data


# id_from_username(host, jwt, username) - Since user ID's are long and
#                                         randomly generated, users are
#                                         not expected to remember them.
#                                         This function finds the ID from
#                                         username
# Input - host: Desired url endpoint (string)
#         jwt: json web token from login() (string)
#         username: Name of the user whose ID is needed (string)
# Output - Returns the user ID as a string
def id_from_username(host, jwt, username):
  user_data = get_users(host, jwt)

  user_found = False
  
  for i in user_data['data']:
    if i['name'] == username:
      user_ID = i['id']
      user_found = True
  
  if user_found == False:
    print('User name not found. Please try another name')
    return None

  return user_ID

# accept_EULA(host, OTC, email) - Before a new user can set password and
#                                 start working, the user must accept the 
#                                 EULA. This requires the OTC returned in the
#                                 json object returned from new_user(host, jwt, req_data)
# Input - host: Desired url endpoint (string)
#         OTC: One time token returned in the json object from new_user(host, jwt, req_data).
#              Must be passed through as an integer (int)
#         email: email address of new user (string)
# Output - Returns a token as a string that can be used to login the new user for 
#          the first time and allows new user to set password
def accept_EULA(host, OTC, email):

  post_data = {
    'token': OTC,
    'email': email,
    'acceptedSeagateTermsAndConditionsAndPrivacyPolicy': True
  }
  print(post_data)
  accept_URL = 'https://{}/udx/v1/acceptEULAByUser'.format(host)


  print_bold('Request: ACCEPT EULA {}...'.format(accept_URL))
  headers = { 
    'accept': 'application/json',
    'Content-Type': 'application/json',
  }


  try:

    response = requests.post(accept_URL, 
                          headers = headers,
                          data = json.dumps(post_data))
    
    
    return response.json()
  except:
    print('<error message>')
  return response

# first_password_set(host, token, password) - Uses token returned from accepting the EULA
#                                             to set new user password for the first time
# Input - host: Desired url enpoint (string)
#         token: json web token returned fromt the function accept_EULA(host, OTC, email) (string)
#         password: Desired first password (string)
# Output - Returns a json object with new user information and a new created password as a key: value pair
def first_password_set(host, token, password):

  password_URL = 'https://{}/udx/v1/setSaasPassword'.format(host)

  print_bold('Request: CHANGE PASSWORD {}'.format(password_URL))

  headers = {
    'accept': 'application/json',
    'Content-Type': 'application/json'
  }

  post_data = {
    'token': token,
    'password': password,
    'name': 'name',
    'phone': '333-444-5555',
    'location': 'Longmont, CO'
  }

  response = requests.post(password_URL, 
                        headers = headers,
                        data = json.dumps(post_data))

  return response.json()
  
