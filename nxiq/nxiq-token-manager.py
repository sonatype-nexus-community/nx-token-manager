
# python 3.10+

import json
import os
import argparse
import requests
import datetime
import pprint
import smtplib
from email.message import EmailMessage

iq_api = 'api/v2'

currentuser_token_endpoint = 'userTokens/currentUser'
currentuser_hastoken_endpoint = 'userTokens/currentUser/hasToken'

notification_message_file = './notification_message.txt'

# test SMTP server (edit accordingly)
email_sender = "none@none.com"
smtp_host = 'localhost'
smtp_port = 1025


def get_args():
    
    global iq_server, iq_user, iq_passwd, iq_realm, expired_tokens_file, created_on, created_since, delete_expired, list_all, create_token, delete_token, notify

    parser = argparse.ArgumentParser(description='Manage your Nexus IQ tokens')

    parser.add_argument('-s', '--server', help='', default='http://localhost:8070', required=False)
    parser.add_argument('-u', '--user', default='admin', help='', required=False)
    parser.add_argument('-p', '--passwd', default='admin123', required=False)
    parser.add_argument('-r', '--realm', help='', default='Internal', required=False) # SAML, Crowd, <LDAP Server Id>
    parser.add_argument('-f', '--expired_tokens_file', default="./expire_tokens.json", required=False) # will contain list of expired tokens

    # only one of the following
    group = parser.add_mutually_exclusive_group(required=True)
    group.add_argument('--created_on', required=False) # find tokens created on this date - yyy-mm-dd
    group.add_argument('--created_since', type=int, required=False) # find tokens created since this age in days
    group.add_argument('--delete_expired', required=False) # delete 'expired' tokens
    group.add_argument('--list_all', action="store_true", required=False) # list all tokens
    group.add_argument('--create_token', action="store_true", required=False) # create a token
    group.add_argument('--delete_token', action="store_true", required=False) # delete a token
    group.add_argument('--notify', action="store_true", required=False) # send email notification for 'expiring' tokens

    args = vars(parser.parse_args())

    iq_server = args['server']
    iq_user = args['user']
    iq_passwd = args['passwd']
    iq_realm = args['realm']
    expired_tokens_file = args['expired_tokens_file']

    created_on = args['created_on']
    created_since = args['created_since']
    delete_expired = args['delete_expired']
    list_all = args['list_all']
    create_token = args['create_token']
    delete_token = args['delete_token']
    notify = args['notify']

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
        case 'list_all':
            endpoint = 'userTokens?realm=' + iq_realm

        case 'created_since':
            date_before = get_query_date_before()
            endpoint = 'userTokens?createdBefore=' + date_before + '?realm=' + iq_realm

        case 'created_on':
            date_after, date_before = get_query_date_range(created_on)
            endpoint = 'userTokens?createdAfter=' + date_after + '?createdBefore=' + date_before + '?realm=' + iq_realm

        case _:
            print ("invalid filter for token search")

    status_code, data = http_request('get', endpoint)

    if status_code == 200:
        tokens = data

    for token in tokens:
        print(token)

    return tokens


def get_query_date_before():
    oneday = 86400 # seconds

    current_dt = datetime.datetime.now()
    current_ts = datetime.datetime.timestamp(current_dt)
    current_dt_str = current_dt.strftime("%Y-%m-%d")

    previous_ts = current_ts - (created_since * oneday)

    previous_dt = datetime.datetime.fromtimestamp(previous_ts)
    previous_dt_str = previous_dt.strftime("%Y-%m-%d")

    print("The current date and time is:", current_dt_str)
    print("The previous date and time:", previous_dt_str)
    print("Will search for tokens created before '" + previous_dt_str + "'")

    return previous_dt_str


def get_query_date_range(created_on):
    # created_on = yyyy-mm-dd
    date_format = "%Y-%m-%d"

    date_after_str = created_on

    date_before = datetime.datetime.strptime(created_on, date_format) + datetime.timedelta(days=1)
    date_before_str = str(date_before.strftime(date_format))

    print("The query date is:", created_on)
    print("Will search for tokens created on and after '" + date_after_str + "'" + " and before '" + date_before_str + "'")

    return date_after_str, date_before_str


def delete_expired_tokens():
    print("Reading expired tokens from file: " + expired_tokens_file)

    tokens = get_expired_tokens()

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

    tokens = get_expired_tokens()

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
    # Start a test smtp server if required:
    #  python3 -m smtpd -c DebuggingServer -n localhost:1025

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


def get_expired_tokens():
    tokens = {}

    if os.path.exists(expired_tokens_file):
        f = open(expired_tokens_file)
        tokens = json.load(f)
    else:
        print ("Error: file does not exist: " + expired_tokens_file)
        print ("Please the script with '--created-since' to create the file")

    return tokens


def dump_to_file(json_data):
    #pretty_print_json = pprint.pformat(json_data).replace("'", '"')
    with open(expired_tokens_file, 'w') as fd:
        json.dump(json_data, fd)


def main():
    get_args()

    if list_all:
        get_tokens('list_all')

    if created_on is not None:
        get_tokens('created_on')

    if created_since is not None:
        tokens = get_tokens('created_since')
        dump_to_file(tokens)

    if create_token:
        create_token()

    if delete_token:
        delete_currentuser_token()

    if delete_expired is not None:
        delete_expired_tokens()

    if notify:
        send_notifications()





if __name__ == "__main__":
    main()

