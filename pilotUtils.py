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
                            verify = False,
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
                            verify = False,
                            data = json.dumps(post_data))
    response_data = response.json()
    return response_data

  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

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
                               verify = False,
    )
    return response
  
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

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
                               verify = False,
                               data = json.dumps(patch_data)
    )
    print(response)
    print(response.json())
    return response
  
  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

# Login - This currently logs the user in and returns the entire JSON
#         object which includes the session JWT and a refresh token.
#         The refresh token can be used to refresh the JWT when it expires.

def login(host, username, password, customerUUID=None):
  LOGIN_URL = 'https://{}/udx/v1/login'.format(host)
  req_data = { 
    'email': username,
    'password': password
  }
  print(LOGIN_URL)
  print(req_data)

  return post_helper(None, LOGIN_URL, req_data)


# newUser - This will post a new user to the user list. Not sure what
#           is going to be the most helpful return yet, just making it work ~~~~~~~~~~~~~~~ FIXME
def new_user(host, jwt, req_data):
  new_user_URL = 'https://{}/udx/v1/saasUser'.format(host)
  # req_data = {
  #   "email": "name@email.com",
  #   "role": "admin",
  #   "language": "EN",
  #   "location": "string",
  #   "name": "string",
  #   "phone": "string"
  # }

  print(new_user_URL)
  print(req_data)

  return post_helper(jwt, new_user_URL, req_data)

# get_users - Returns a list of all user names for a given domain.
#            Maybe reutrn passwords or jwt ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FIXME
def get_users(host, jwt):
  get_user_URL = 'https://{}/udx/v1/users'.format(host)

  user_data = get_helper(jwt, get_user_URL, None)
  return user_data

def get_user(host, jwt, username, user_ID=None):

  if user_ID == None:
    user_ID = id_from_username(host, jwt, username)
  print(user_ID)

  get_user_URL = 'https://{}/udx/v1/users/{}'.format(host, user_ID)

  user_data = get_helper(jwt, get_user_URL, None)

  return user_data

# Two ways this could be done, can either use user_ID or the name of the user. Will try to 
# accomodate both

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


# def set_phone_number(host, jwt, username, newNumber, user_ID=None):

#   if user_ID == None:

#     user_ID = id_from_username(host, jwt, username)

#   set_phone_number_URL = 'https://{}/udx/v1/users/{}'.format(host, user_ID)

#   post_data = {
#     'token': jwt,
#     ''
#   }

#   return response

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
                          verify = False,
                          data = json.dumps(post_data))
    
    
    return response.json()
  except:
    print('request has failed') # Elaborate further ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~FIXME
  return response

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
                        verify = False,
                        data = json.dumps(post_data))

  return response.json()
  
