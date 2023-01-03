#!/bin/bash
# ##########################################################
# Download a Sonatype Nexus Repository user token for a specific user
#
# Supports All versions of Sonatype Nexus Repository that have user tokens enabled.
#
# Latest version:
#   https://support.sonatype.com/hc/en-us/articles/213465878
# Requirements:
#   GNU base64 option OR openssl
#   curl
#   awk
# Author:
#   Sonatype Support Team
# ##########################################################

function base64_encode(){
  local to_encode="$1"
  local result="NOT-BASE64-ENCODED"
  if command -v base64 &> /dev/null; then
      result="$(echo -n "$to_encode" | base64 | tr -d '\n')"
  elif command -v openssl &> /dev/null; then
    result="$(echo -n "$to_encode" | openssl enc -A -base64)"
  fi
  echo "$result"
}

function help()
{
  echo "Usage: `basename $0` repo_url repo_user"
  exit 2
}

# Read secret string - https://stackoverflow.com/a/28393320
function read_secret(){
  oldtty="$(stty -g)"
  # Disable echo.
  stty -echo
  # Set up trap to ensure echo is enabled before exiting if the script
  # is terminated while echo is disabled.
  trap 'stty echo' EXIT
  # Read secret.
  read "$@"
  # Enable echo.
  #stty echo
  stty $oldtty
  trap - EXIT
  # Print a newline because the newline entered by the user after
  # entering the passcode is not echoed. This ensures that the
  # next line of output begins at a new line.
  echo
}

# determine repo version by examining Server response header
function get_server_header(){
  local repo_url="$1"
  server="$(curl -sI "$repo_url" | awk -v FS=": " '/^[sS]erver/{print $2}')"
  echo "$server"
}

# determine supported URL for obtaining single use access token
function get_single_use_token_url(){
  local repo_url="$1"
  local urls=("/service/rest/wonderland/authenticate" "/service/siesta/wonderland/authenticate" "/service/local/usertoken/authenticate")
  local furl=''
  for url in "${urls[@]}"; do
    furl="$repo_url$url"
    resp_code="$(curl -sI "$furl" | awk '/^HTTP/{print $2}')"
    if [[ "$resp_code" != '404' ]]; then
      break;
    fi
  done
  echo "$furl"
}

# determine supported URL for obtaining user token
function get_user_token_url(){
  local repo_url="$1"
  local urls=("/service/rest/internal/current-user/user-token" "/service/rest/usertoken/current" "/service/siesta/usertoken/current" "/service/local/usertoken/current")
  local furl=''
   for url in "${urls[@]}"; do
     furl="$repo_url$url";
     resp_code="$(curl -sI "$furl" | awk '/^HTTP/{print $2}')"
     if [[ "$resp_code" != '404' ]]; then
       break;
     fi
   done
   echo "$furl"
}

# fetch a single use time-limited access token
function fetch_single_use_token(){
local base_url="$1"
local username="$2"
local password="$3"
local creds="$username:$password"
local u_b64="$(base64_encode "$username")"
local p_b64="$(base64_encode "$password")"
local payload="{\"u\":\"$u_b64\",\"p\":\"$p_b64\"}"
local furl="$(get_single_use_token_url $base_url)"
http_resp="$(curl "${furl}" -H "Accept: application/json" -H "Content-Type: application/json" \
  -u "$creds" --data-raw "$payload" 2>/dev/null)"
auth_token_raw="$(echo -n "$http_resp" | awk -F'"' '{printf $4}')"
auth_token_encoded="$(base64_encode "$auth_token_raw")"
echo -n "$auth_token_encoded"
}

# get user token name/passcode for a specific user
function fetch_user_token() {
local base_url="$1"
local username="$2"
local password="$3"
local creds="$username:$password"
local auth_token="$(fetch_single_use_token "$base_url" "$username" "$password")"
local furl="$(get_user_token_url $base_url)"
if [[ "$furl" == *user-token ]]; then
  user_token="$(curl -s -G --data-urlencode "authToken=${auth_token}" -u "$creds" "${furl}")"
else
  user_token="$(curl -s -G -H "X-NX-AuthTicket: ${auth_token}" -H "X-NX-UserToken-AuthTicket" -u "$creds" "${furl}")"
fi
echo -n "$user_token"
}

if [ "$#" -ne 2 ]; then
  help
fi

repo_url="${1%/}"
username="$2"

server_header=$(get_server_header "$repo_url")
echo "$repo_url Server header: $server_header"

printf "Enter repository user '$username' password: "
read_secret password

user_token="$(fetch_user_token "$repo_url" "$username" "$password")"
echo -n "$user_token"
