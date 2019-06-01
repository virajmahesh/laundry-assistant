from flask import Flask
from selenium import webdriver
from flask import jsonify
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

app = Flask(__name__)

MACHINE_BASE_ID = 'ContentPlaceHolder1_gvRoom_lbl'
MACHINE_NAME_ID = MACHINE_BASE_ID + 'MachineID'
MACHINE_TYPE_ID = MACHINE_BASE_ID + 'MachineTypeName'
MACHINE_STATUS_ID = MACHINE_BASE_ID + 'Status'


def parse_list(lst):
    return list(map(lambda x: x.text, lst))


def get_machine_info(driver, info):
    return parse_list(driver.find_elements_by_css_selector("span[id^={}]".format(info)))


driver = webdriver.Chrome()


@app.route('/')
def hello_world():

    driver.get('https://www.mywavevision.com')
    driver.find_element_by_id('txtUserID').send_keys('virajmahesh')
    driver.find_element_by_id('txtPassword').send_keys('luXW&*W6fB#3Q4@f8')

    driver.find_element_by_id('BtnIndex').click()

    WebDriverWait(driver, 100).until(
        EC.title_is('Room Status')
    )

    machine_ids = get_machine_info(driver, MACHINE_NAME_ID)
    machine_types = get_machine_info(driver, MACHINE_TYPE_ID)
    machine_status = get_machine_info(driver, MACHINE_STATUS_ID)

    free_washers, free_dryers = 0, 0
    for i in range(len(machine_ids)):
        if machine_status[i] == 'Available':
            if machine_types[i] == 'Washer':
                free_washers += 1
            elif machine_types[i] == 'Dryer':
                free_dryers += 1

    return jsonify({'free_washers': free_washers, 'free_dryers': free_dryers})


if __name__ == '__main__':
    app.run()
