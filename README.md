# covid-vaccine-slots-availability-checker

1. Update your phone number in "mobile_number.txt"
   1. Simply enter 10 digit mobile number without any space and new lines
1. Run following commands to generate authentication token
    ```shell
    python generate-otp.py
    <enter otp received on your phone>
    ```
1. Run `python cowin-calendar.py` to fetch available slots
    1. It will fetch 18+ slots in whole delhi for upcoming 7 days.
1. A file will be created called "results.json" which will hold the output of available slots
1. A sound notification ("Book now") is also triggered on laptop if there are available slots

**NOTE** - refresh authentication token every 15mins using `python generate-otp.py`

## Pre requisites
Script is designed and compatible using - 
1. Python 2.7
1. MacOS

## Script setup
1. You need to have python2.7 installed
1. You need to install correct version of pip. Follow these steps - 
   ```shell
   curl https://bootstrap.pypa.io/pip/2.7/get-pip.py  -o get-pip.py
   sudo python get-pip.py
   ```
1. Run following commands to install the packages
   ```shell
   sudo pip install requests
   ```

## Cron schedule configuration

1. Open crontab using `crontab -e`
1. Add following lines to run script every 15 seconds
    ```shell
    */1 * * * * cd <absolute path to script> && /usr/bin/python cowin-calendar.py
    */1 * * * * sleep 15; cd <absolute path to script> && /usr/bin/python cowin-calendar.py
    */1 * * * * sleep 30; cd <absolute path to script> && /usr/bin/python cowin-calendar.py
    */1 * * * * sleep 45; cd <absolute path to script> && /usr/bin/python cowin-calendar.py
    ```
1. Run following commands
   ```shell
   cd <directory containing scripts>
   chmod 755 cowin-calendar.py
   chmod 755 token.txt
   chmod 755 logs.log
   chmod 755 results.json
   ```
1. After above steps, the scheduled execution will start
1. Verify execution by checking `logs.log` file created in the same directory as script

## Troubleshooting

Q. What to do if OTP is not received?

A. We can re-generate OTP only **after 3 minutes**.
   1. Press enter to end current script run
   1. Again run `python generate-otp.py`
   1. Enter `y` and press enter to re-send OTP
   1. Now Enter OTP if received
      1. If not, repeat