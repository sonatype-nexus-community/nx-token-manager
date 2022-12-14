
# python 3.10+

import sys
import json
import argparse
import requests
from datetime import datetime

iq_api = 'api/v2'

currentuser_token_endpoint = 'userTokens/currentUser'
currentuser_hastoken_endpoint = 'userTokens/currentUser/hasToken'


def get_args():
    
    global iq_server, iq_user, iq_passwd, mode, iq_realm, expire_tokens, period

    parser = argparse.ArgumentParser(description='Manage your Nexus IQ tokens')

    parser.add_argument('-s', '--server', help='', default='http://localhost:8070', required=False)
    parser.add_argument('-u', '--user', default='admin', help='', required=False)
    parser.add_argument('-p', '--passwd', default='admin123', required=False)
    parser.add_argument('-m', '--mode', help='', default='get_all', required=False)
    parser.add_argument('-r', '--realm', help='', default='Internal', required=False) # SAML, Crowd, <LDAP Server Id>
    #parser.add_argument('-e', '--expire', default=False,  required=False)
    parser.add_argument('-e', '--expire', action='store_true')
    parser.add_argument('--period', default=365, type=int, required=False)

    args = vars(parser.parse_args())

    iq_server = args['server']
    iq_user = args['user']
    iq_passwd = args['passwd']
    mode = args['mode']
    iq_realm = args['realm']
    expire_tokens = args['expire']
    period = args['period']

    return


def http_request(verb, end_point):
    res = ""
    url = "{}/{}/{}" . format(iq_server, iq_api, end_point)

    print(url)

    match verb:
        case 'post':
            req = requests.post(url, auth=(iq_user, iq_passwd), verify=False)

        case 'delete':
            req = requests.delete(url, auth=(iq_user, iq_passwd), verify=False)

        case 'get':
            req = requests.get(url, auth=(iq_user, iq_passwd), verify=False)

        case _:
            print("Invalid mode")

    print(req)

    status_code = req.status_code

    if status_code == 200:
        res = req.json()

    return status_code, res


def user_has_token():
    status = ""
    status_code, data = http_request('get', currentuser_hastoken_endpoint)

    if status_code == 200:
        status = data['userTokenExists']

        if status == True:
            print("User has a token")
        else:
            print("User does not have a token")
    else:
        print("Login error")

    return status


def create_token():

    if not user_has_token():

        status_code, data = http_request('post', currentuser_token_endpoint)

        if status_code == 200:
            print(data)
            # userCode = data['userCode']
            # passCode = data['passCode']

    return


def delete_token():

    if user_has_token():

        status_code, data = http_request('delete', currentuser_token_endpoint)

        if status_code == 204:
            print("Token successfully deleted")

    return


def get_tokens(filter):
    endpoint = ""

    match filter:
        case 'for_expiry':
            search_date = get_query_date()
            endpoint = 'userTokens?createdBefore=' + search_date + '?realm=' + iq_realm

        case 'all':
            endpoint = 'userTokens?realm=' + iq_realm

        case _:
            print ("invalid filter for token search")

    status_code, data = http_request('get', endpoint)

    if status_code == 200:
        tokens = data

        for token in tokens:
            print(token)

    return tokens


def get_query_date():
    oneday = 86400 # seconds

    current_dt = datetime.now()
    current_ts = datetime.timestamp(current_dt)

    print("The current date and time is:", current_dt)
    print("The current timestamp (secs) is:", current_ts)

    previous_ts = current_ts - (period*oneday)

    previous_dt = datetime.fromtimestamp(previous_ts)
    previous_dt_str = previous_dt.strftime("%Y-%d-%m")

    print("The previous date and time:", previous_dt)
    print("The previous timestamp (secs) is:", previous_ts)
    print("Will search for tokens created before '" + previous_dt_str + "'")

    return previous_dt_str


def main():
    get_args()

    match mode:
        case 'create':
            create_token()
        
        case 'delete':
            delete_token()

        case 'get':
            get_tokens('for_expiry')

        case 'get_all':
            get_tokens('all')

        case _:
            print("invalid mode")



if __name__ == "__main__":
    main()

