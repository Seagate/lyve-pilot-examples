#!/bin/bash

echo "Example script using the user's API"
echo
# Check cURL command if available (required), abort if does not exists
type curl >/dev/null 2>&1 || { echo >&2 "Required curl but it's not installed. Aborting."; exit 1; }
echo

uuid='156b9cujydh6dq9s44dubnsg7r'
email='dylan.sain@seagate.com'
password='Testit123'
name="New Guy"

USERS_URL='/udx/v1/users'
NEW_USER_URL='/udx/v1/saasUser'
ACCEPT_EULA_URL='/udx/v1/acceptEULAByUser'
SET_PASSWORD_URL='/udx/v1/setSaasPassword'
FEED_URL='/udx/v1/feed'

BASE_URL='https://api-staging.lyve.seagate.com/'$uuid

new_user_data='{"email":"bigtest@seagate.com","role":"admin","language":"EN","location":"0","name":"New Guy","phone":"123-456-7890"}'

login () {
    local data="{\"email\": \"$1\",\"password\": \"$2\"}"
    response=`curl -s --request POST -H "Content-type:application/json" $BASE_URL/udx/v1/login --data "$data"`
    token=`echo $response | grep -o '"token":"[^"]*' | grep -o '[^"]*$'`
    echo $token
}

get_users(){
    response=$(get_helper "$1" $2)
    names=`$response | jq '.["data"] | .[] | {name: .name}'`
    echo $names
}

id_from_username(){
    response=$(get_helper "$1" $USERS_URL)
    #this is an example but we weary as it could fail with user with same names
    user_id=`$response | jq ".[\"data\"] | .[] | select(.name | contains(\"$3\")) | .[\"id\"]"`
    echo $user_id
}

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

new_user(){
    echo $(post_helper "$1" $2 "$3")
}

accept_EULA(){
    data="{\"token\":\"$3\",\"email\":\"$4\",\"acceptedSeagateTermsAndConditionsAndPrivacyPolicy\":true}"
    echo $(post_helper "$1" $2 $data)
}

first_password_set(){
    post_data="{\"token\": \"$3\",\"password\": \"$4\",\"name\": \"New Guy\",\"phone\": \"123-456-7890\",\"location\": \"Longmont, CO\"}"
    echo $(post_helper "$1" "$2" "$post_data")
}

change_phonenumber(){
    patch_data="{\"name\": \"New Guy\",\"phone\": \"$4\",\"location\": \"Longmont, CO\"}"
    url=$2"/"$3
    echo $(patch_helper "$1" $url "$patch_data")
}

delete_user(){
    echo $(delete_helper "$1" $2 "/"$3)
}

get_feed(){
    url="/"$2
    response=$(get_helper "$1" $url)
    feed=`$response`
    echo $feed
}



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

accept_EULA_token=$(accept_EULA "$header" $ACCEPT_EULA_URL $OTC bigtest@seagate.com)
accept_EULA_token=`jq -n "$accept_EULA_token" | jq -r '.["token"]'`
echo "EULA token: "$accept_EULA_token

new_user_jwt=$(first_password_set "$header" $SET_PASSWORD_URL $accept_EULA_token Testit123)
new_user_jwt=`jq -n "$new_user_jwt" | jq -r '.["token"]'`
echo "New User JWT: "$new_user_jwt

single_user=$(get_user "$headerJWT" $USERS_URL "$name" 62bc949ac0522200101b9bac)
single_user_id=`jq -n "$single_user" | jq -r '.["id"]'`
echo "Got single user: "$single_user_id

newUserHeaderJWT="-H Content-type:application/json -H accept:application/json -H Authorization:"$new_user_jwt
changed_user=$(change_phonenumber "$newUserHeaderJWT" $USERS_URL $single_user_id "111-222-3333")
echo "Changed User: "$changed_user

delete_new_user=$(delete_user "$headerJWT" $USERS_URL $single_user_id)
echo "Delete user status: "$delete_new_user

feed=$(get_feed "$headerJWT" $FEED_URL)
#echo "The Feed: "$feed