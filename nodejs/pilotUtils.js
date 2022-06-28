// Copyright (c) 2022 Seagate Technology LLC and/or its Affiliates

// Permission is hereby granted, free of charge, to any person obtaining a copy 
// of this software and associated documentation files (the "Software"), to 
// deal in the Software without restriction, including without limitation the 
// rights to use, copy, modify, merge, publish, distribute, sublicense, and/or 
// sell copies of the Software, and to permit persons to whom the Software is 
// furnished to do so, subject to the following conditions:

// The above copyright notice and this permission notice shall be included in 
// all copies or substantial portions of the Software.

// THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR 
// IMPLIED, INCLUDING BUT NOT LIMITED TO THE WARRANTIES OF MERCHANTABILITY, 
// FITNESS FOR A PARTICULAR PURPOSE AND NONINFRINGEMENT. IN NO EVENT SHALL THE 
// AUTHORS OR COPYRIGHT HOLDERS BE LIABLE FOR ANY CLAIM, DAMAGES OR OTHER 
// LIABILITY, WHETHER IN AN ACTION OF CONTRACT, TORT OR OTHERWISE, ARISING 
// FROM, OUT OF OR IN CONNECTION WITH THE SOFTWARE OR THE USE OR OTHER 
// DEALINGS IN THE SOFTWARE.

const axios = require('axios');
// const { exit } = require('process');

// const args = process.argv.slice(2);
const uuid = '<Your UUID>'; //args[0];
const email = '<Your admin or first user email>'; //args[1];
const password = '<Your Password>'; //args[2];

//These are some of the endpoints of the Lyve Pilot API that can be queried.
//This script is written to use all url endpoints as global variables and used by
//helper functioins. The file pilotUtils.py presents a different way to organize variables
// and url endpoints 
const USERS_URL = '/udx/v1/users';
const NEW_USER_URL = '/udx/v1/saasUser';
const ACCEPT_EULA_URL = '/udx/v1/acceptEULAByUser';
const SET_PASSWORD_URL = '/udx/v1/setSaasPassword';
const FEED_URL = '/udx/v1/feed';

const base_url = 'https://pilot.lyve.seagate.com/' + uuid;

const name = 'name'

const new_user_data = {
  "email": "email@organizaton.com",
  "role": "admin",
  "language": "EN",
  "location": "333 my address",
  "name": name,
  "phone": "123-456-7890"
};

//  login(host, username, password) - This currently logs the user in and 
//          returns the entire JSON object which includes the session JWT and a refresh token.
//          The refresh token can be used to refresh the JWT when it expires.
//  Input - host: Desired url endpoint (string)
//          username: username (string)
//          password: password (string)
//  Output - Returns a json web token that is passed through other functions
//           as a valiidation object. Expires after 10 minutes. Also returns
//           a refresh token in order to extend session

async function login(email, password) {
  const data = JSON.stringify({
    "email": email,
    "password": password
  });
  let response = await axios.post(base_url+'/udx/v1/login', data, {headers: {'Content-Type': 'application/json'}});
  let token = await response.data.token;
  return token;
}

//  get_users(jwt, url, filters) - Fetches an array of usernames currently
//                         saved to customer instance as strings
//  Input - jwt: json web token from login() (string)
//          url: Desired url endpoint (string)
//          filters: list of filters for return (string)
//  Output - Returns an array of usernames as strings
async function get_users(jwt, url, filters){
    let response = await get_helper(jwt, url, filters);
    let users = [];
    for(let i =0; i < response.data.length; i++){
        users[i] = response.data[i].name;
    }

    return users;
}

// id_from_username(jwt, url, username) - Since user ID's are long and
//                                         randomly generated, users are
//                                         not expected to remember them.
//                                         This function finds the ID from
//                                         username
// Input - jwt: json web token from login() (string)
//         url: Desired url endpoint (string)
//         username: Name of the user whose ID is needed (string)
// Output - Returns the user ID as a string
async function id_from_username(jwt, url, username) {
  let user_list = await get_helper(jwt, url);
  for(let i = 0; i < user_list.data.length; i++){
    if (user_list.data[i].name == username) {
      return user_list.data[i].id;
    }
  }
  return error; 
}

//  get_user(jwt, url, username, user_ID=Null) - Fetches the json object
//                                                for one specific user
//  Input - jwt: json web token from login() (string)
//          url: Desired url endpoint (string)
//          username: name of user to be fetched. Can be left empty
//                    if user ID is known
//          user_ID: The ID of a user as saved in the user's profile.
//                   If the user ID is not known, username can be passed
//                   and the ID will be found automatically by the function
//                   id_from_username(jwt, url, username)
//  Output - Returns a json object containing user information
async function get_user(jwt, url, username, user_ID=null) {
  try {
    if (user_ID == null) {
    user_ID = await id_from_username(jwt, url, username);
    }
  }
  catch (error) {
    console.log(error);
  }
  const response = await get_helper(jwt, url + '/' + user_ID);
  return response;
}

//  new_user(jwt, url, req_data) - This will post a new user to the user list 
//                                  to the customer instance. User will not have
//                                  accepted the EULA yet
//  Input - jwt: json web token returned from login() (string)
//          url: Desired url endpoint (string)
//          req_data: json object containing relevant new user information (string)
//  Output - Returns a json object containing created user's data. The OTC key will
//           need to be pulled in order to accept EULA and set new user password
async function new_user(jwt, url, data) {
  return await post_helper(jwt, url, data);
};

// accept_EULA(OTC, url, email) - Before a new user can set password and
//                                 start working, the user must accept the 
//                                 EULA. This requires the OTC returned in the
//                                 json object returned from new_user(host, jwt, req_data)
// Input - OTC: One time token returned in the json object from new_user(host, jwt, req_data).
//         Must be passed through as an integer (int)
//         url: Desired url endpoint (string)
//         email: email address of new user (string)
// Output - Returns a token as a string that can be used to login the new user for 
//          the first time and allows new user to set password
async function accept_EULA(OTC, url, email) {
  post_data = {
    'token': OTC,
    'email': email,
    'acceptedSeagateTermsAndConditionsAndPrivacyPolicy': true
  }

  const config = {
    method: 'post',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json'
    },
    data: post_data
  };

  let response = await axios(config);
  return response.data.token;
}

// first_password_set(token, url, password) - Uses token returned from accepting the EULA
//                                             to set new user password for the first time
// Input - token: json web token returned fromt the function accept_EULA(host, OTC, email) (string)
//         url: Desired url endpoint (string)
//         password: Desired first password (string)
// Output - Returns a json object with new user information and a new created password as a key: value pair
async function first_password_set(token, url, password) {
  const post_data = {
    'token': token,
    'password': password,
    'name': 'New User',
    'phone': '123-456-7890',
    'location': 'Longmont, CO'
  }

  const config = {
    method: 'post',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json'
    },
    data: post_data
  };

  let response = await axios(config);
  return response.data.token;
}

// change_phonenumber(jwt, url, user_ID, new_number) - Changes the phone number
//                                                     saved for specific user. This is
//                                                     only an example for how user data can 
//                                                     be changed via API. This change must be
//                                                     made with a jwt generated from the login
//                                                     of the user whose information is changing
// Input - jwt: json web token generated from login() (string)
//         url: Desired url endpoint (string)
//         user_ID: ID of user to be changed. Can be generated from id_from_username(jwt, url, username) (string)
//         new_number: New phone number to replace old number (string)
async function change_phonenumber(jwt, url, user_ID, new_number) {
  const patch_data = {
    'name': name,
    'phone': new_number,
    'location': 'Longmont, CO'
  }

  return patch_helper(jwt, url + '/' + user_ID, patch_data);
}

// delete_user(jwt, url, id) - Deletes the specified user from the user database for a customer instance
// Input - jwt: json web token generated from login() (string)
//         url: Desired url endpoint (string)
//         user_ID: ID of user to be changed. Can be generated from id_from_username(jwt, url, username) (string)
async function delete_user(jwt, url, user_ID) {

  const response = await delete_helper(jwt, url + '/' + user_ID);
  return response;
}

// get_feed(jwt, url, filters) - Fetches feed for customer instance. Can be parsed via filters
//  Input - jwt: json web token from login() (string)
//          url: Desired url endpoint (string)
//          filters: list of filters for return (string)
// Output - Returns an array of json objects where each object is a transaction from the feed
//          for a user instance. Can be parsed using filters
async function get_feed(jwt, url, filters) {
  return get_helper(jwt, url, filters);
}

async function delete_helper(jwt, url) {
  const config = {
    method: 'delete',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + jwt
    },
  };

  let response = await axios(config);
  return response;
}

async function get_helper(jwt, url, filters) {
  const config = {
    method: 'get',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + jwt
    },
    params: filters
  };

  let response = await axios(config);
  return response.data;
}

async function post_helper(jwt, url, data) {
  const config = {
    method: 'post',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + jwt
    },
    data: data
  };

  let response = await axios(config);
  return response.data;
}

async function patch_helper(jwt, url, data) {
  const config = {
    method: 'patch',
    url: base_url + url,
    headers: {
      'accept': 'application/json',
      'Content-Type': 'application/json',
      'Authorization': 'Bearer ' + jwt
    },
    data: data
  };

  let response = await axios(config);
  return response.data;
}

// This script is written as a single standalone file but pilotUtils.js could be used as a module and exported using a feature like this 
module.exports = {login, id_from_username,get_user, new_user, accept_EULA, first_password_set, delete_user, get_users, get_feed, get_helper, post_helper, delete_helper, patch_helper}

// The script here is written as a single file. This means that variables declared here can be used here. In a situation where
// this is used as an imported module, the variables will need to be declared in a slightly different fashion depending
// on your implementation and needs.
async function start() {
    try {
      let jwt = await login(email, password);
      console.log('Login Token: ' + jwt);
      console.log(base_url + USERS_URL);

      let users = await get_users(jwt, USERS_URL);
      console.log('Users: ' + users);

      let created_user = await new_user(jwt, NEW_USER_URL, new_user_data);
      console.log('New User OTC: ' + created_user.user.OTC);

      let accept_EULA_token = await accept_EULA(created_user.user.OTC, ACCEPT_EULA_URL, 'email@organization.com');
      console.log('EULA Token: ' + accept_EULA_token);

      let new_user_jwt = await first_password_set(accept_EULA_token, SET_PASSWORD_URL, 'Testit123');
      console.log('New User Token: ' + new_user_jwt);

      let single_user = await get_user(jwt, USERS_URL, name);
      console.log(single_user);

      console.log('New User ID: ' + single_user._id);

      let changed_user = await change_phonenumber(new_user_jwt, USERS_URL, single_user._id, '111-222-3333'); // Only the user may change their own info
      console.log('~~~~ Changed Phone Number ~~~~');
      console.log(changed_user);

      let delete_new_user = await delete_user(jwt, USERS_URL, single_user._id);
      console.log('Delete User Response code: ' + delete_new_user.status);

      let feed = await get_feed(jwt, FEED_URL);
      console.log('~~~~ FEED ~~~~')
      console.log(feed);

    } catch(error) {
      console.log(error);
    }
  }
  
  start()