import datetime
import requests
import json


def get_calendar_by_pin_code(pin_code, start_date):
    url = "https://cdn-api.co-vin.in/api/v2/appointment/sessions/public/findByPin?pincode=%s&date=%s" \
          % (pin_code, start_date)
    print (url)
    headers = {'Accept-Language': "en_US", 'accept': 'application/json'}

    response_object = requests.get(url, headers=headers)
    response = response_object.json()
    return response['sessions']


def get_eligible_centers_by_age(response, age):
    eligible_sites = []
    for node in response:
        hospital_name = node['name']
        date = node['date']
        age_eligible = node['min_age_limit']
        vaccine = node['vaccine']
        capacity = node['available_capacity']
        pin_code = node['pincode']
        if age_eligible == age and capacity > 0 and vaccine == "COVAXIN":
            eligible_sites.append({'name': hospital_name, 'date': date, 'vaccine': vaccine, 'capacity': capacity,
                                    'pincode': pin_code})
    return eligible_sites


def execute():
    date_list = []
    pin_code_list = ['110034', '110088', '110085', '110026', '110063']

    today = datetime.datetime(2021, 05, 25)
    for idx in range(0, 7):
        date = today + datetime.timedelta(days=idx)
        date_list.append(date.strftime("%d-%m-%Y"))

    all_eligible_sites = []
    for pin_code in pin_code_list:
        for date in date_list:
            print('#####')
            print('date: %s' % date)
            print('pin_code: %s' % pin_code)
            response = get_calendar_by_pin_code(pin_code, date)
            eligible_sites = get_eligible_centers_by_age(response, 45)
            all_eligible_sites.extend(eligible_sites)

    result_file = open("result-papa.json", "w")
    # magic happens here to make it pretty-printed
    result_file.write(json.dumps(all_eligible_sites, indent=4, sort_keys=True))
    result_file.close()


if __name__ == '__main__':
    execute()
