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


const axios = require('axios').default;
const pilotUtils = require('./pilotUtils.js')
const { exit } = require('process')

const args = process.argv.slice(2);
const uuid = args[0];
const email = args[1];
const password = args[2];

const USERS_URL = '/udx/v1/users';

const data = JSON.stringify({
  "email": email,
  "password": password
});
const base_url = 'https://api-staging.lyve.seagate.com/' + uuid;

// pilotUtils Functions included:
//  login
//  get_users
//  get_helper
//  post_helper

async function start() {
  try {
    let jwt = await pilotUtils.login();
    console.log('Login Token: ' + jwt);

    let users = await pilotUtils.get_users(jwt, USERS_URL);
    console.log(users);

  } catch(error) {
    console.log(error);
  }
}

start()

