import sys
import pilotUtils
import requests

def print_bold(output):
  print('\033[1m' + output + '\033[0m')

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

def login(host, username, password, customerUUID=None):
  LOGIN_URL = 'https://{}/udx/v1/login'.format(host)
  req_data = { 
    'email': username,
    'password': password
  }
  print(LOGIN_URL)
  print(req_data)

  return post_helper(None, LOGIN_URL, req_data)

HOST = 'aptest.colo.seagate.com:32324'
USERNAME = 'admin@seagate.com'
PASSWORD = '389LyvePilot' 

token = pilotUtils.login(HOST, USERNAME, PASSWORD)['token']

print(token)