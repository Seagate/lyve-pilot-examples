
// var bodyParser = require('body-parser');
// var express = require('express');
// var app = express();

const axios = require('axios').default;
const pilotUtils = require('./pilotUtils.js')
const { exit } = require('process')

const args = process.argv.slice(2);
const uuid = '156b9cujydh6dq9s44dubnsg7r'; //args[0];
const email = 'adam.j.poppenhagen@seagate.com'; //args[1];
const password = 'Hsft6167#@!'; //args[2];

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
    // console.log(base_url + USERS_URL);
    let users = await pilotUtils.get_users(jwt, USERS_URL);
    console.log(users);

  } catch(error) {
    console.log(error);
  }
}

start()

