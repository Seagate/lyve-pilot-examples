#!/bin/bash

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

echo "Example script using the user's API"
echo
# Check cURL command if available (required), abort if does not exists
type curl >/dev/null 2>&1 || { echo >&2 "Required curl but it's not installed. Aborting."; exit 1; }
echo

# Make sure Variables are encapsulated with "" if there are spaces within them
uuid='<Your UUID>'
email='<Your admin or first user email>'
password='<Your Password>'

# These are some of the endpoints of the Lyve Pilot API that can be queried.
# This script is written to use all url endpoints as global variables and used by
# helper functioins. 
USERS_URL='/udx/v1/users'
NEW_USER_URL='/udx/v1/saasUser'
ACCEPT_EULA_URL='/udx/v1/acceptEULAByUser'
SET_PASSWORD_URL='/udx/v1/setSaasPassword'
FEED_URL='/udx/v1/feed'

BASE_URL='https://api-staging.lyve.seagate.com/'$uuid

name="John Doe"

# There are two ways to do JSON objects in bash using '' will make it impossible to
# use variables in the string. Instead use "" and escape the extra "" to create a 
# valid JSON string
new_user_data='{"email":"email@organization.com","role":"admin","language":"EN","location":"0","name":"John Doe","phone":"123-456-7890"}'

#  login(username, password)
#       This currently logs the user in and returns the entire JSON 
#       object which includes the session JWT and a refresh token.
#       The refresh token can be used to refresh the JWT when it expires.
#  Input - username: username  $1
#          password: password  $2
#  Output - Returns a json web token that is passed through other functions
#           as a valiidation object. Expires after 10 minutes. Also returns
#           a refresh token in order to extend session

login () {
    local data="{\"email\": \"$1\",\"password\": \"$2\"}"
    response=`curl -s --request POST -H "Content-type:application/json" $BASE_URL/udx/v1/login --data "$data"`
    # One way of parsing JSON by using grep
    token=`echo $response | grep -o '"token":"[^"]*' | grep -o '[^"]*$'`
    echo $token
}

#  get_users(headers, url)
#       Fetches an array of usernames currently
#       saved to customer instance as strings
#  Input - headers: the headers for the curl request  $1
#          url: Desired url endpoint  $2
#  Output - Returns a string of JSON objects in the form of {name: name}
get_users(){
    response=$(get_helper "$1" $2)
    # another way of parsing JSON by using jq
    names=`$response | jq '.["data"] | .[] | {name: .name}'`
    echo $names
}

# id_from_username(headers, url, username)
#       Since user ID's are long and randomly generated, users are not
#       expected to remember them. This function finds the ID from username
# Input - headers: the headers for the curl request  $1
#         url: Desired url endpoint  $2
#         username: Name of the user whose ID is needed  $3
# Output - Returns the user ID
id_from_username(){
    response=$(get_helper "$1" $USERS_URL)
    # this is an example but be weary as it could fail when users have the same names
    user_id=`$response | jq ".[\"data\"] | .[] | select(.name | contains(\"$3\")) | .[\"id\"]"`
    echo $user_id
}

#  get_user(headers, url, username, user_ID)
#       Fetches the json object for one specific user
#  Input - headers: the headers for the curl request  $1
#          url: Desired url endpoint  $2
#          username: name of user to be fetched. Can be left empty
#                    if user ID is known  $3
#          user_ID: The ID of a user as saved in the user's profile.
#                   If the user ID is not known, username can be passed
#                   and the ID will be found automatically by the function
#                   id_from_username(headers, url, username) accessible by 
#                   using $3
#  Output - Returns a json object containing user information
get_user(){
    id=$4
    if [ -z "$id" ];
    then
        id=$(id_from_username "$1" $2 "$3")
        id=${id:1:-1}
    fi 
    url=$2"/"$id
    response=$(get_helper "$1" $url)
    user=`$response`
    echo $user
}

#  new_user(headers, url, req_data)
#       This will post a new user to the user list to the customer
#       instance. User will not have accepted the EULA yet
#  Input - headers: the headers for the curl request  $1
#          url: Desired url endpoint  $2
#          req_data: json object containing relevant new user information accessible 
#          by using $2
#  Output - Returns a json object containing created user's data. The OTC key will
#           need to be pulled in order to accept EULA and set new user password
new_user(){
    echo $(post_helper "$1" $2 "$3")
}

# accept_EULA(headers, url, OTC, email)
#       Before a new user can set password and start working, the
#       user must accept the EULA. This requires the OTC returned in the
#       json object returned from new_user(headers, url, req_data)
# Input - headers: the headers for the curl request  $1
#         url: Desired url endpoint  $2
#         OTC: One time token returned in the json object from new_user(headers, url, req_data)  $3
#         email: email address of new user  $4
# Output - Returns a token as a string that can be used to login the new user for 
#          the first time and allows new user to set password
accept_EULA(){
    data="{\"token\":\"$3\",\"email\":\"$4\",\"acceptedSeagateTermsAndConditionsAndPrivacyPolicy\":true}"
    echo $(post_helper "$1" $2 $data)
}

# first_password_set(headers, url, token, password)
#       Uses token returned from accepting the EULA to set new user 
#       password for the first time
# Input - headers: the headers for the curl request  $1
#         url: Desired url endpoint  $2
#         token: json web token returned fromt the function accept_EULA(headers, url, OTC, email)  $3
#         password: Desired first password  #4
# Output - Returns a json object with new user information and a new created password as a key: value pair
first_password_set(){
    post_data="{\"token\": \"$3\",\"password\": \"$4\",\"name\": \"John Doe\"}"
    echo $(post_helper "$1" "$2" "$post_data")
}

# change_phonenumber(headers, url, user_ID, new_number)
#       Changes the phone number saved for specific user. This is the
#       only an example for how user data can be changed via API. This
#       change must be made with a jwt generated from the login of the 
#       user whose information is changing
# Input - headers: the headers for the curl request  $1
#         url: Desired url endpoint  $2
#         user_ID: ID of user to be changed. Can be generated from id_from_username(headers, url, username)  $3
#         new_number: New phone number to replace old number  $4
change_phonenumber(){
    patch_data="{\"name\": \"John Doe\",\"phone\": \"$4\"}"
    url=$2"/"$3
    echo $(patch_helper "$1" $url "$patch_data")
}

# delete_user(headers, url, id)
#       Deletes the specified user from the user database for a customer instance
# Input - headers: the headers for the curl request  $1
#         url: Desired url endpoint  $2
#         user_ID: ID of user to be changed. Can be generated from id_from_username(headers, url, username)  $3
delete_user(){
    echo $(delete_helper "$1" $2 "/"$3)
}

# get_feed(headers, url)
#       Fetches feed for customer instance.
#  Input - headers: the headers for the curl request  $1
#          url: Desired url endpoint  $2
# Output - Returns an array of json objects where each object is a transaction from the feed
#          for a user instance.
get_feed(){
    url="/"$2
    response=$(get_helper "$1" $url)
    feed=`$response`
    echo $feed
}


# following are helper functions with multiple ways to return the curl command
delete_helper(){
    url=$BASE_URL$2$3

    response=`curl -X delete $url $1`
    echo $response
}

get_helper(){
    url=$BASE_URL$2$3

    response="curl $1 $url"
    echo $response
}

post_helper(){
    url=$BASE_URL$2
    data=$3

    response=`curl -X POST $url $1 -d "$data"`
    echo $response
}

patch_helper(){
    url=$BASE_URL$2
    data=$3

    response=`curl -X PATCH $url $1 -d "$data"`
    echo $response
}

jwt=$(login $email $password)
headerJWT="-H Content-type:application/json -H accept:application/json -H Authorization:"$jwt
header="-H Content-type:application/json -H accept:application/json"
echo "The JWT token: "$jwt

users=$(get_users "$headerJWT" $USERS_URL)
echo "List of users: " $users

created_user=$(new_user "$headerJWT" $NEW_USER_URL "$new_user_data")
echo "Created User: " $created_user
OTC=`jq -n "$created_user" | jq '.["user"]' | jq -r '.["OTC"]'`
echo $OTC

accept_EULA_token=$(accept_EULA "$header" $ACCEPT_EULA_URL $OTC $email)
accept_EULA_token=`jq -n "$accept_EULA_token" | jq -r '.["token"]'`
echo "EULA token: "$accept_EULA_token

new_user_jwt=$(first_password_set "$header" $SET_PASSWORD_URL $accept_EULA_token $password)
new_user_jwt=`jq -n "$new_user_jwt" | jq -r '.["token"]'`
echo "New User JWT: "$new_user_jwt

single_user=$(get_user "$headerJWT" $USERS_URL "$name")
single_user_id=`jq -n "$single_user" | jq -r '.["id"]'`
echo "Got single user: "$single_user_id

newUserHeaderJWT="-H Content-type:application/json -H accept:application/json -H Authorization:"$new_user_jwt
changed_user=$(change_phonenumber "$newUserHeaderJWT" $USERS_URL $single_user_id "111-222-3333")
echo "Changed User: "$changed_user

delete_new_user=$(delete_user "$headerJWT" $USERS_URL $single_user_id)
echo "Delete user status: "$delete_new_user

feed=$(get_feed "$headerJWT" $FEED_URL)
echo "The Feed: "$feed