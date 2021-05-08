import datetime
import json
from collections import defaultdict

import requests

api_key = 'Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.eyJ1c2VyX25hbWUiOiJhOWE5MjRjNy05Yzc2LTQ3OWUtOTA3ZS02NTZjMDNhMzM4NzUiLCJ1c2VyX2lkIjoiYTlhOTI0YzctOWM3Ni00NzllLTkwN2UtNjU2YzAzYTMzODc1IiwidXNlcl90eXBlIjoiQkVORUZJQ0lBUlkiLCJtb2JpbGVfbnVtYmVyIjo5OTEwMzM0NDE5LCJiZW5lZmljaWFyeV9yZWZlcmVuY2VfaWQiOjQ3NjQ1MTM1MjY3MzQwLCJ1YSI6Ik1vemlsbGEvNS4wIChNYWNpbnRvc2g7IEludGVsIE1hYyBPUyBYIDEwXzE1XzcpIEFwcGxlV2ViS2l0LzUzNy4zNiAoS0hUTUwsIGxpa2UgR2Vja28pIENocm9tZS85MC4wLjQ0MzAuOTMgU2FmYXJpLzUzNy4zNiIsImRhdGVfbW9kaWZpZWQiOiIyMDIxLTA1LTA1VDE0OjI0OjExLjE0MloiLCJpYXQiOjE2MjAyMjQ2NTEsImV4cCI6MTYyMDIyNTU1MX0.RLVLyIHbBdpQMqKwRur7BwKa2kfIjKOuAdXThGqajG4'
headers_with_api_key = {'Accept-Language': "en_US", 'accept': 'application/json', 'authorization': api_key}
headers_without_api_key = {'Accept-Language': "en_US", 'accept': 'application/json'}

calendar_url_without_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/calendarByDistrict?district_id=%s&date=%s&vaccine=COVAXIN"
calendar_url_with_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/calendarByDistrict?district_id=%s&date=%s&vaccine=COVAXIN"

pincode_url_without_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=%s&date=%s&vaccine=COVAXIN"
pincode_url_with_api_key = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/findByPin?pincode=%s&date=%s&vaccine=COVAXIN"

final_headers = headers_with_api_key
final_calendar_url = calendar_url_with_api_key
final_pincode_url = pincode_url_with_api_key
# final_headers = headers_without_api_key
# final_calendar_url = calendar_url_without_api_key
# final_pincode_url = pincode_url_without_api_key

def get_calendar_by_district_id(district_id, start_date):
    url = final_calendar_url % (district_id, start_date)
    headers = final_headers
    print(url)

    response_object = requests.get(url, headers=headers)
    print (response_object)
    response = response_object.json()
    return response['centers']


def get_calendar_by_pin_code(pin_code, start_date):
    url = final_pincode_url % (pin_code, start_date)
    headers = final_headers
    print (url)

    response_object = requests.get(url, headers=headers)
    response = response_object.json()
    return response['sessions']


def get_vaccine_name_for_centre(response, input_hospital_name):
    for node in response:
        hospital_name = node['name']
        vaccine = node['vaccine']
        if hospital_name == input_hospital_name and len(vaccine) > 0:
            return vaccine
    return ""


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
    district_code_list = []
    for idx in range(0, 11):
        district_code_list.append(str(140 + idx))

    today = datetime.datetime(2021, 06, 11)
    for idx in range(0, 2):
        date = today + datetime.timedelta(days=idx * 7)
        date_list.append(date.strftime("%d-%m-%Y"))

    all_eligible_sites = []
    for district_code in district_code_list:
        for date in date_list:
            print('#####')
            print('date: %s' % date)
            print('district_code: %s' % district_code)
            response = get_calendar_by_district_id(district_code, date)
            eligible_sites = get_eligible_centers_by_age(response, 18)
            all_eligible_sites.extend(eligible_sites)

    grouped_by_pincode = defaultdict(list)
    for site in all_eligible_sites:
        grouped_by_pincode[site['pin_code']].append(site)

    # if len(site['vaccine']) <= 0:
    #     site['vaccine'] = get_vaccine_name_for_centre(site['name'], site['pin_code'], site['availability'][0]['date'])
    for pin_code in grouped_by_pincode:
        sites = grouped_by_pincode[pin_code]

        all_dates = []
        for site in sites:
            for avail in site['availability']:
                all_dates.append(avail['date'])
        all_unique_dates = (list(set(all_dates)))

        pin_code_response = []
        for date in all_unique_dates:
            response = get_calendar_by_pin_code(pin_code, date)
            pin_code_response.extend(response)

        for site in sites:
            if len(site['vaccine']) == 0:
                site['vaccine'] = get_vaccine_name_for_centre(pin_code_response, site['name'])

    result_file = open("result-dose2.json", "w")
    # magic happens here to make it pretty-printed
    result_file.write(json.dumps(grouped_by_pincode, indent=4, sort_keys=True))
    result_file.close()


if __name__ == '__main__':
    execute()
