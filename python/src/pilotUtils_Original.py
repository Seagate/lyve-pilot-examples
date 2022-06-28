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

def printJson(output):
  pp.pprint(output)

def printBold(output):
  print('\033[1m' + output + '\033[0m')


# Helper method to retrieve objects given a URL and optional filters.
def getHelper(jwt, url, filterParams):
  printBold('Request: GET {}...'.format(url))
  print('\tFilters: {}'.format(json.dumps(filterParams)))
  headers = { 
    'accept': 'application/json',
    'Authorization': 'Bearer {}'.format(jwt)
  }
  try:
    response = requests.get(url, 
                            headers = headers,
                            params = filterParams)
    responseData = response.json()
    return responseData

  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

# Helper method to perform operations

def postHelper(jwt, url, postData):
  printBold('Request: POST {}...'.format(url))
  headers = { 
    'accept': 'application/json',
    'Content-Type': 'application/json',
  }

  if jwt:
    headers['Authorization'] = 'Bearer {}'.format(jwt)

  try:
    response = requests.post(url, 
                            headers = headers,
                            data = json.dumps(postData))
    responseData = response.json()
    return responseData

  except requests.exceptions.RequestException as e:
    raise SystemExit(e)

# Login - This currently logs the user in and returns the entire JSON
#         object which includes the session JWT and a refresh token.
#         The refresh token can be used to refresh the JWT when it expires.

def login(host, customerUUID, username, password):
  LOGIN_URL = 'https://{}/{}/udx/v1/login'.format(host, customerUUID)
  reqData = { 
    'email': username,
    'password': password
  }
  return postHelper(None, LOGIN_URL, reqData)
