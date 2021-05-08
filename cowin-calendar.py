import datetime
import json
import os
from collections import defaultdict
from os import path

import requests

log_file = open("logs.log", "a+")


def log(stmt):
    print(stmt)
    log_file.write(stmt)
    log_file.write('\n')


def get_api_key():
    if path.isfile("token.txt"):
        result_file = open("token.txt", "r")
        token = result_file.read()
        result_file.close()
        return token
    else:
        return ""


api_key = get_api_key()
headers_with_api_key = {'Accept-Language': "en_US", 'accept': 'application/json',
                        'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36',
                        'authorization': api_key}
headers_without_api_key = {'Accept-Language': 'en_US', 'accept': 'application/json',
                           'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_10_1) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/39.0.2171.95 Safari/537.36'}

calendar_url_without_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=%s&date=%s"
calendar_url_with_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id=%s&date=%s"

pincode_url_without_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=%s&date=%s"
pincode_url_with_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/findByPin?pincode=%s&date=%s"

if len(api_key) >= 0:
    final_headers = headers_with_api_key
    final_calendar_url = calendar_url_with_api_key
    final_pincode_url = pincode_url_with_api_key
else:
    final_headers = headers_without_api_key
    final_calendar_url = calendar_url_without_api_key
    final_pincode_url = pincode_url_without_api_key


def get_calendar_by_district_id(district_id, start_date):
    url = final_calendar_url % (district_id, start_date)
    headers = final_headers
    print(url)

    response_object = requests.get(url, headers=headers)
    if str(response_object.status_code) == "200":
        print(str(response_object.status_code))
    else:
        log(str(response_object.status_code))
    response = response_object.json()
    return response['centers']


def get_eligible_centers_by_age(response, age):
    eligible_sites = []
    for node in response:
        hospital_name = node['name']
        district_name = node['district_name']
        pin_code = node['pincode']
        vaccine = node['sessions'][0]['vaccine']
        availability = []
        for session in node['sessions']:
            date = session['date']
            age_eligible = session['min_age_limit']
            capacity = session['available_capacity']
            if age_eligible == age and capacity > 2:
                availability.append({'date': date, 'capacity': capacity})
        if len(availability) > 0:
            eligible_sites.append(
                {'name': hospital_name, 'district_name': district_name, 'vaccine': vaccine, 'pin_code': pin_code,
                 'availability': availability})
    return eligible_sites


def execute():
    date_list = []
    # district_code_list = ['265', '276']
    # district_code_list = ['141', '140', '146', '143', '142']
    district_code_list = []
    for idx in range(0, 11):
        district_code_list.append(str(140 + idx))

    today = datetime.datetime.now()
    for idx in range(0, 1):
        date = today + datetime.timedelta(days=idx * 7)
        date_list.append(date.strftime("%d-%m-%Y"))

    all_eligible_sites = []
    for district_code in district_code_list:
        for date in date_list:
            print('#####')
            print('date: %s' % date)
            print('district_code: %s' % district_code)
            try:
                response = get_calendar_by_district_id(district_code, date)
                eligible_sites = get_eligible_centers_by_age(response, 18)
                all_eligible_sites.extend(eligible_sites)
            except Exception as e:
                log("{}".format(e.message))
                log("failed - " + str(district_code) + " - " + str(date))

    log("Completed - " + datetime.datetime.now().__str__())

    grouped_by_pincode = defaultdict(list)
    for site in all_eligible_sites:
        grouped_by_pincode[site['pin_code']].append(site)

    if len(grouped_by_pincode.items()) > 0:
        os.system('say Book Now')
    result_file = open("result.json", "w")
    result_file.write(json.dumps(grouped_by_pincode, indent=4, sort_keys=True))
    result_file.close()


if __name__ == '__main__':
    execute()
    log_file.close()
