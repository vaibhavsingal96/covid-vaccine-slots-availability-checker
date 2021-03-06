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
headers_with_api_key = {
    "Accept-Language": "en_US",
    "Accept": "application/json",
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.77 Safari/537.36",
    "Referer": "https://apisetu.gov.in/public/api/cowin",
    "Origin": "https://apisetu.gov.in",
    "DNT": "1",
    "Connection": "keep-alive",
    "Pragma": "no-cache",
    "Cache-Control": "no-cache",
    'authorization': api_key
}
headers_without_api_key = {
    "Accept-Language": "en_US",
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

calendar_url_without_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=%s&date=%s"
calendar_url_with_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id=%s&date=%s"

pincode_url_without_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=%s&date=%s"
pincode_url_with_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/findByPin?pincode=%s&date=%s"

if len(api_key) > 0:
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
            capacity_dose_1 = session['available_capacity_dose1']
            capacity_dose_2 = session['available_capacity_dose2']
            if age_eligible == age and (capacity_dose_1 > 2 or capacity_dose_2 > 2):
                availability.append({'date': date, 'capacity_dose_1': capacity_dose_1, 'capacity_dose_2': capacity_dose_2})
        if len(availability) > 0:
            eligible_sites.append(
                {'name': hospital_name, 'district_name': district_name, 'vaccine': vaccine, 'pin_code': pin_code,
                 'availability': availability})
    return eligible_sites


def execute():
    date_list = []
    # district_code_list = ['149', '148']
    # district_code_list = [<enter comma separated values here for manual district codes>]
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

    log("Completed - " + today.__str__())

    grouped_by_pincode = defaultdict(list)
    for site in all_eligible_sites:
        grouped_by_pincode[site['pin_code']].append(site)

    if len(grouped_by_pincode.items()) > 0:
        os.system('say Book Now')
        log("Slots available - " + today.__str__())
    result_file = open("result.json", "w")
    result_file.write(json.dumps(grouped_by_pincode, indent=4, sort_keys=True))
    result_file.close()


if __name__ == '__main__':
    execute()
    log_file.close()
