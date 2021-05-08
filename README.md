# covid-vaccine-slots-availability-checker

Update your phone number in "generate-otp.py"

Run following commands
1. python generate-otp.py
2. enter otp received on your phone
3. python cowin-calendar.py

It will fetch 18+ slots in whole delhi for upcoming 7 days.

A file will be created called "results.json" which will hold the output of available slots

NOTE - refresh api-key token every 10mins using "python generate-otp.py"

## Pre requisites
Script is designed and compatible using - 
1. Python 2.7
1. MacOS