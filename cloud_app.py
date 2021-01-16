import time
import chromedriver_binary
from flask import Flask, jsonify
from selenium import webdriver
from google.cloud import firestore
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


app = Flask(__name__)
db = firestore.Client()

LAUNDRY_ROOM_STATUS_COLLECTION = db.collection(u'laundry_room_statuses')

MACHINE_BASE_ID = 'ContentPlaceHolder1_gvRoom_lbl'
MACHINE_NAME_ID = MACHINE_BASE_ID + 'MachineID'
MACHINE_TYPE_ID = MACHINE_BASE_ID + 'MachineTypeName'
MACHINE_STATUS_ID = MACHINE_BASE_ID + 'Status'


def get_machine_info(info):
    def parse_list(lst):
        return list(map(lambda x: x.text, lst))

    return parse_list(driver.find_elements_by_css_selector("span[id^={}]".format(info)))


# Create the Chrome Webdriver
chrome_options = webdriver.ChromeOptions()
chrome_options.add_argument("--headless")
chrome_options.add_argument("--disable-gpu")
chrome_options.add_argument("window-size=1024,768")
chrome_options.add_argument("--no-sandbox")
driver = webdriver.Chrome(chrome_options=chrome_options)


@app.route('/update')
def update_machine_data():
    driver.get('https://mywavevision.com/')

    WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.ID, "txtUserID"))
    )

    driver.find_element_by_id('txtUserID').send_keys('virajmahesh')
    driver.find_element_by_id('txtPassword').send_keys('luXW&*W6fB#3Q4@f8')

    driver.find_element_by_id('BtnIndex').click()

    WebDriverWait(driver, 300).until(
        EC.title_is('Room Status')
    )

    machine_ids = get_machine_info(MACHINE_NAME_ID)
    machine_types = get_machine_info(MACHINE_TYPE_ID)
    machine_status = get_machine_info(MACHINE_STATUS_ID)

    # Count the number of free washers and dryers
    free_dryers, free_washers = 0, 0
    for i in range(len(machine_ids)):
        if machine_status[i] == 'Available':
            if machine_types[i] == 'Washer':
                free_washers += 1
            elif machine_types[i] == 'Dryer':
                free_dryers += 1

    # Fetch the latest status from Firestore
    status_ref = LAUNDRY_ROOM_STATUS_COLLECTION.document('latest')
    # status = status_ref.get()

    # Create a copy of the object for analysis
    # LAUNDRY_ROOM_STATUS_COLLECTION.add(status.to_dict())

    # Update the latest status
    status_ref.set({
        'free_washers': free_washers,
        'free_dryers': free_dryers,
        'last_updated': firestore.SERVER_TIMESTAMP
    })

    # Return the latest status
    status = status_ref.get()
    return jsonify(status.to_dict())


@app.route('/')
def get_free_machine_data():
    status_ref = LAUNDRY_ROOM_STATUS_COLLECTION.document('latest')
    status = status_ref.get()
    return jsonify(status.to_dict())


if __name__ == '__main__':
    app.run()
