
var bodyParser = require('body-parser');
var express = require('express');
var app = express();

const axios = require('axios').default;

const HOST = 'htttps://aptest.colo.seagate.com:32324';
const USERNAME = 'admin@seagate.com';
const PASSWORD = '389LyvePilot';

function login(host, email, password){
    var token = axios.get(HOST.concat('/users/v1/login'))
}
