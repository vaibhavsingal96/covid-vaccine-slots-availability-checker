import hashlib
import json
from os import path

import requests

mobile_number = 0000000000


def generate_otp(phone_number):
    url = "https://cdn-api.co-vin.in/api/v2/auth/public/generateOTP"
    headers = {'Accept-Language': 'en_US', 'accept': 'application/json',
               'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}
    body = {"mobile": "%s" % phone_number}

    response_object = requests.post(url, json=body, headers=headers)
    print("Status code: " + str(response_object.status_code))
    print(response_object.content)
    response = response_object.json()
    return response['txnId']


def authenticate_otp(otp, txn_id):
    url = "https://cdn-api.co-vin.in/api/v2/auth/public/confirmOTP"
    headers = {'accept': 'application/json', 'Content-Type': 'application/json'}
    body = {'otp': '%s' % otp, 'txnId': '%s' % txn_id}

    response_object = requests.post(url, data=json.dumps(body), headers=headers)
    print(response_object.request.body)
    print(response_object.text)
    response = response_object.json()
    return response['token']


def get_txn_id_from_file():
    if path.isfile("txn_id.txt"):
        result_file = open("txn_id.txt", "r")
        token = result_file.read()
        result_file.close()
        return token
    else:
        return ""


def execute_generate_otp(number):
    txn_id = generate_otp(number)
    result_file = open("txn_id.txt", "w")
    result_file.write(txn_id)
    result_file.close()
    return txn_id


def clear_txn_id():
    result_file = open("txn_id.txt", "w")
    result_file.write("")
    result_file.close()


def execute():
    txn_id = get_txn_id_from_file()
    if len(txn_id) <= 0:
        txn_id = execute_generate_otp(mobile_number)
    else:
        force_refresh = raw_input("Resend OTP? (y/n): ")
        if force_refresh == 'y' or force_refresh == 'Y':
            try:
                temp_txn_id = execute_generate_otp(mobile_number)
                txn_id = temp_txn_id
            except Exception as e:
                print(e.message)
                raise e

    otp = input("Enter otp: ")
    otp_encoded = hashlib.sha256("%s" % otp).hexdigest()
    print(otp_encoded)

    token = authenticate_otp(otp_encoded, txn_id)
    token = "Bearer %s" % token

    result_file = open("token.txt", "w")
    result_file.write(token)
    result_file.close()

    clear_txn_id()


if __name__ == '__main__':
    execute()
