import hashlib
import json
from os import path

import requests


def get_mobile_number():
    result_file = open("mobile_number.txt", "r")
    number = result_file.read()
    result_file.close()

    if len(number) <= 0:
        print("please update mobile_number.txt with your phone number")
        raise Exception("")
    return number


mobile_number = get_mobile_number()

def generate_otp(phone_number):
    url = "https://cdn-api.co-vin.in/api/v2/auth/generateOTP"
    headers = {
        "Accept-Language": "en-US",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Referer": "https://selfregistration.cowin.gov.in/",
        "Origin": "https://selfregistration.cowin.gov.in",
        "DNT": "1",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "content-type": "application/json"
    }
    body = {"mobile": "%s" % phone_number, "secret": "U2FsdGVkX1+z/4Nr9nta+2DrVJSv7KS6VoQUSQ1ZXYDx/CJUkWxFYG6P3iM/VW+6jLQ9RDQVzp/RcZ8kbT41xw=="}

    response_object = requests.post(url, json=body, headers=headers)
    print("Status code: " + str(response_object.status_code))
    print(response_object.content)
    response = response_object.json()
    return response['txnId']


def authenticate_otp(otp, txn_id):
    url = "https://cdn-api.co-vin.in/api/v2/auth/confirmOTP"
    headers = {
        "Accept-Language": "en-US",
        "Accept": "application/json",
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
        "Referer": "https://apisetu.gov.in/public/api/cowin/cowin-public-v2",
        "Origin": "https://apisetu.gov.in",
        "DNT": "1",
        "Connection": "keep-alive",
        "Pragma": "no-cache",
        "Cache-Control": "no-cache",
        "content-type": "application/json"
    }
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
