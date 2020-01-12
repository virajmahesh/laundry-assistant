import csv
import time
import atexit
import chromedriver_binary 
from flask import Flask
from flask import jsonify
from selenium import webdriver
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from apscheduler.schedulers.background import BackgroundScheduler

app = Flask(__name__)

MACHINE_BASE_ID = 'ContentPlaceHolder1_gvRoom_lbl'
MACHINE_NAME_ID = MACHINE_BASE_ID + 'MachineID'
MACHINE_TYPE_ID = MACHINE_BASE_ID + 'MachineTypeName'
MACHINE_STATUS_ID = MACHINE_BASE_ID + 'Status'


def parse_list(lst):
    return list(map(lambda x: x.text, lst))


def get_machine_info(info):
    return parse_list(driver.find_elements_by_css_selector("span[id^={}]".format(info)))


free_washers = 0
free_dryers = 0
last_updated = '0:0:0'

chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")

driver = webdriver.Chrome(chrome_options=chrome_options)

log_file = open('log.csv', 'a+')
field_names = ['time', 'free_washers', 'free_dryers']
log_file_writer = csv.DictWriter(log_file, fieldnames=field_names)


@app.route('/update')
def update_machine_count():

    global free_dryers, free_washers
    free_dryers, free_washers = 0, 0

    driver.get('https://www.mywavevision.com')
    driver.find_element_by_id('txtUserID').send_keys('virajmahesh')
    driver.find_element_by_id('txtPassword').send_keys('luXW&*W6fB#3Q4@f8')

    driver.find_element_by_id('BtnIndex').click()

    WebDriverWait(driver, 100).until(
        EC.title_is('Room Status')
    )

    machine_ids = get_machine_info(MACHINE_NAME_ID)
    machine_types = get_machine_info(MACHINE_TYPE_ID)
    machine_status = get_machine_info(MACHINE_STATUS_ID)

    for i in range(len(machine_ids)):
        if machine_status[i] == 'Available':
            if machine_types[i] == 'Washer':
                free_washers += 1
            elif machine_types[i] == 'Dryer':
                free_dryers += 1

    response = get_response()
    last_updated = time.strftime("%B %d %Y %I:%M:%S %p")
    #print(response)

    log_file_writer.writerow(response)
    return jsonify(response)


def get_response():
    return \
    {
        'time': time.strftime("%B %d %Y %I:%M:%S %p"),
        'last_updated': last_updated,
        'free_washers': free_washers,
        'free_dryers': free_dryers
    }


@app.route('/')
def get_free_machine_count():
    return jsonify(get_response())


if __name__ == '__main__':
    app.run()
