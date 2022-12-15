
# python 3.10+

import json
import argparse
import requests
from datetime import datetime
import pprint
import smtplib
from email.message import EmailMessage

iq_api = 'api/v2'

currentuser_token_endpoint = 'userTokens/currentUser'
currentuser_hastoken_endpoint = 'userTokens/currentUser/hasToken'
expired_tokens_file= "./expire-tokens.json"

notification_message_file = './notification_message.txt'
email_sender = "sola@me.com"
smtp_host = 'localhost'
smtp_port = 1025


def get_args():
    
    global iq_server, iq_user, iq_passwd, mode, iq_realm, age, expired_tokens_file

    parser = argparse.ArgumentParser(description='Manage your Nexus IQ tokens')

    parser.add_argument('-s', '--server', help='', default='http://localhost:8070', required=False)
    parser.add_argument('-u', '--user', default='admin', help='', required=False)
    parser.add_argument('-p', '--passwd', default='admin123', required=False)
    parser.add_argument('-m', '--mode', help='', default='listx', required=False) # create, list, delete, delete_expired,notify
    parser.add_argument('-r', '--realm', help='', default='Internal', required=False) # SAML, Crowd, <LDAP Server Id>
    parser.add_argument('-a', '--age', default=365, type=int, required=False) # expiry age
    parser.add_argument('-f', '--tokens_file', default="./expire-tokens.json", required=False) # list of expired tokens

    args = vars(parser.parse_args())

    iq_server = args['server']
    iq_user = args['user']
    iq_passwd = args['passwd']
    mode = args['mode']
    iq_realm = args['realm']
    age = args['age']
    expired_tokens_file = args['tokens_file']

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
    status = False

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

    return


def delete_currentuser_token():

    if user_has_token():
        status_code, data = http_request('delete', currentuser_token_endpoint)

        if status_code == 204:
            print("Token successfully deleted")

    return


def get_tokens(filter):
    tokens = []
    endpoint = ""

    match filter:
        case 'expired':
            search_date = get_query_date()
            endpoint = 'userTokens?createdBefore=' + search_date + '?realm=' + iq_realm

        case 'all':
            endpoint = 'userTokens?realm=' + iq_realm

        case _:
            print ("invalid filter for token search")

    status_code, data = http_request('get', endpoint)

    if status_code == 200:
        tokens = data

    return tokens


def get_query_date():
    oneday = 86400 # seconds

    current_dt = datetime.now()
    current_ts = datetime.timestamp(current_dt)

    print("The current date and time is:", current_dt)
    print("The current timestamp (secs) is:", current_ts)

    previous_ts = current_ts - (age * oneday)

    previous_dt = datetime.fromtimestamp(previous_ts)
    previous_dt_str = previous_dt.strftime("%Y-%d-%m")

    print("The previous date and time:", previous_dt)
    print("The previous timestamp (secs) is:", previous_ts)
    print("Will search for tokens created before '" + previous_dt_str + "'")

    return previous_dt_str


def delete_expired_tokens():
    print("Reading expired tokens from file: " + expired_tokens_file)

    f = open(expired_tokens_file)
    tokens = json.load(f)

    for token in tokens:
        print(token)
        user_code = token['userCode']
        user_name = token['username']

        print("Removing token [username=" + user_name + "] [userCode=" + user_code + "]")

        endpoint = 'userTokens/userCode/' + user_code

        status_code, data = http_request('delete', endpoint)

    return


def send_notifications():
    print("Reading expired tokens from file: " + expired_tokens_file)

    f = open(expired_tokens_file)
    tokens = json.load(f)

    for token in tokens:
        user_code = token['userCode']
        user_name = token['username']

        endpoint = 'users/' + user_name

        status_code, data = http_request('get', endpoint)

        if status_code == 200:
            email_address = data["email"]
            print ("Got email address for " + user_name + "[" + email_address + "]")

            send_expiry_notification(user_name, email_address)

    return


def send_expiry_notification(user_name, email_address):
    # Start test smtp server: 'python3 -m smtpd -c DebuggingServer -n localhost:1025'


    with open(notification_message_file) as fp:
        msg = EmailMessage()
        msg.set_content(fp.read())

    msg['Subject'] = 'Nexus IQ token expiry'
    msg['From'] = email_sender
    msg['To'] = email_address

    s = smtplib.SMTP(smtp_host, smtp_port)
    s.send_message(msg)
    s.quit()

    return


def dump_to_file(json_data):
    #pretty_print_json = pprint.pformat(json_data).replace("'", '"')
    with open(expired_tokens_file, 'w') as fd:
        json.dump(json_data, fd)



def main():
    get_args()

    match mode:
        case 'create':
            create_token()
        
        case 'delete':
            delete_currentuser_token()

        case 'list':
            tokens = get_tokens('all')

            for token in tokens:
                print(token)

        case 'listx':
            tokens = get_tokens('expired')

            for token in tokens:
                print(token)

            dump_to_file(tokens)

        case 'delete_expired':
            delete_expired_tokens()

        case 'notify':
            send_notifications()

        case _:
            print("invalid mode")


if __name__ == "__main__":
    main()

