#!/usr/local/bin/python3.5

import config, logging, time, sys, atexit
from selenium import webdriver
# from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
from time import sleep
# import json
import ssh_cocon.ssh_cocon as ccn
from colorama import Fore

testingDomain = config.domainName
sipUsersCfgJson = config.testConfigJson['Users']
sipShareCfgJson = config.testConfigJson['ShareSet'][0]

testResultsList = []

driver = webdriver.Remote('http://' + config.webDriverServerIP + ':4444/wd/hub',
                          desired_capabilities=DesiredCapabilities.CHROME)

def initDriver():
    # global driver
    logging.info('Init remote driver')
    # driver = webdriver.Remote('http://'+ config.webDriverServerIP +':4444/wd/hub',desired_capabilities=DesiredCapabilities.CHROME)
    driver.implicitly_wait(10)
    driver.set_window_size(1200, 800)


def wait_until_element_present(how, what, wait_timeout=10):
    logging.info('Waiting for element ' + str(what))
    for i in range(wait_timeout):
        print('.', end='')
        try:
            # print('trying to find element')
            if is_element_present(how, what):
                # print('found')
                logging.info('Element ' + str(what) + ' found')
                return True
        except Exception as e:
            pass
            sleep(1)
    else:
        # print('Didnt found login element')
        print("time out")
        logging.error('Expected element ' + str(what))
        return False


def is_element_present(how, what):
    logging.info('Check if element ' + str(what) + ' present')
    try:
        driver.find_element(by=how, value=what)
    except NoSuchElementException as e:
        logging.info('Didnt found element')
        # print('No such element exception!')
        return False
    except Exception as e:
        print('Exception :' + str(e))
        logging.warning('Unexpected exception ' + str(e) + ' during searching of ' + str(what))
        return False
    return True


def preconfigure():
    if ccn.domainDeclare(testingDomain, removeIfExists=True):
        print(Fore.GREEN + 'Successful domain declare')
    else:
        print(Fore.RED + 'Smthing happen wrong with domain declaration...')
        return False

    cnt = 0
    time.sleep(2)
    while not ccn.checkDomainInit(testingDomain):  # проверяем инициализацию домена
        print(Fore.YELLOW + 'Not inited yet...')
        cnt += 1
        if cnt > 5:
            print(Fore.RED + "Test domain wasn't inited :(")
            return False
        time.sleep(2)

    if not ccn.ssAddAccessAll(dom=testingDomain):
        return False

    if ccn.sipShareSetDeclare(sharesetName=config.shareSetName, sipIP=config.shareSetIP, sipPort=config.shareSetPort):
        print(Fore.GREEN + 'Successful shareSet creation')
    else:
        print(Fore.RED + 'Smthing happen wrong with shareSet creation...')
        return False

    if ccn.sipTransportShareSetup(dom=testingDomain, sharesetName=config.shareSetName):
        print(Fore.GREEN + 'Successful shareSet setup')
    else:
        print(Fore.RED + 'Smthing happen wrong with shareSet setup...')
        return False

    if ccn.subscriberPortalSetConnection(dom=testingDomain):
        print(Fore.GREEN + 'Successful subscriber portal properties set')
    else:
        print(Fore.RED + 'Smthing happen wrong with subscriber portal properties set...')
        return False

    if ccn.subscribersCreate(dom=testingDomain,
                             sipNumber=sipUsersCfgJson[0]['Number'],
                             sipPass=sipUsersCfgJson[0]['Password'], sipGroup=sipUsersCfgJson[0]['SipGroup'],
                             routingCTX='default_routing'):
        print(Fore.GREEN + 'Successful Subscriber creation')
    else:
        print(Fore.RED + 'Smthing happen wrong with subscribers creation...')
        return False

    if ccn.subscriberPortalCheckConnection(testingDomain):
        print(Fore.GREEN + 'Connection width MySQL is ok')
    else:
        print(Fore.RED + 'Check subscriber portal MySQL connection failure!')
        return False

    if ccn.subscriberPortalSync(testingDomain,password='1234'):
        print(Fore.GREEN + 'Successful subscriber portal sync')
    else:
        print(Fore.RED + 'Successful subscriber portal sync failed')
        #return False

    if ccn.ssEnable(dom=testingDomain, subscrNum=sipUsersCfgJson[0]['Number'], ssNames='*'):
        print(Fore.GREEN + 'Successful Subscriber services enable')
    else:
        print(Fore.RED + 'Smthing happen wrong with subscribers services enable...')
        return False

    if ccn.setAliasSubscriberPortalLoginPass(dom=testingDomain, subscrNum=sipUsersCfgJson[0]['Number'],
                                             sipGroup=sipUsersCfgJson[0]['SipGroup'],
                                             login=sipUsersCfgJson[0]['Number'], passwd=sipUsersCfgJson[0]['Password']):
        print(Fore.GREEN + 'Successful Subscriber portal login/pass set')
    else:
        print(Fore.RED + 'Failed to set Subscriber portal login/pass...')
        return False

    return True


def test_subscr_portal_login():
    driver.set_window_size(1200, 800)
    base_url = config.httpProtocol + '://' + config.host + ':' + config.httpPort
    driver.get(base_url)

    wait_until_element_present(By.ID, 'login')

    driver.find_element_by_id("login").clear()
    driver.find_element_by_id("login").send_keys(sipUsersCfgJson[0]['Number'])
    driver.find_element_by_id("password").clear()
    driver.find_element_by_id("password").send_keys(sipUsersCfgJson[0]['Password'])
    # chooos in combobox
    Select(driver.find_element_by_id("domain")).select_by_visible_text(testingDomain)  # choose domain in combobox
    # sleep(2)
    # driver.find_element_by_xpath("//select[@id='domain']/option").click()
    sleep(0.5)
    driver.find_element_by_id("login_btn").click()  # logining
    if not assertTrue(is_element_present(By.XPATH, "//img[@title='Eltex']")):  ## check main banner
        return False
    # self.assertTrue(self.is_element_present(By.XPATH, "//TD[text()='Петя']")) ## check disp name text
    if not assertTrue(is_element_present(By.XPATH, "//TD[text()='" + sipUsersCfgJson[0][
        'Number'] + "']")):  ## check subscriber number
        return False
    sleep(0.5)
    driver.find_element_by_id("ss_list").click()  # switch to ss list
    if not assertTrue(is_element_present(By.XPATH, "//*[contains(text(), 'Обслуживание абонента')]")):  # assert text
        return False
    sleep(0.5)

    driver.find_element_by_xpath("//LABEL[@for='ss_list_all']").click()  ## switch to all ss
    sleep(2)
    if not assertTrue(is_element_present(By.XPATH,
                                         "//label[contains(text(), 'Трехсторонняя конференция')]")):  # check if services displayed
        return False
    driver.find_element_by_xpath("//LABEL[@for='ss_list_activated']").click()  ## switch to activated ss
    sleep(2)
    if not assertFalse(is_element_present(By.XPATH,
                                          "//label[contains(text(), 'Трехсторонняя конференция')]")):  # check if services disapeared
        return False

    driver.find_element_by_id("call_history").click()  # switch to ss call_history
    if not assertTrue(is_element_present(By.XPATH, "//*[contains(text(), 'История вызовов')]")):  # assert text
        return False
    sleep(0.5)

    driver.find_element_by_id("reset").click()  # switch to ss call_history
    if not assertTrue(is_element_present(By.XPATH, "//*[contains(text(), 'Информация об абоненте')]")):  # assert text
        return False
    sleep(0.5)

    driver.find_element_by_xpath("//*[contains(text(), 'Выход')]").click()  ## logout
    if not assertTrue(is_element_present(By.ID, 'login')):
        return False

    return True


def assertTrue(what, msg=''):
    logging.info('Assertion if true :' + str(what))
    if what is True:
        return True
    else:
        return False


def assertFalse(what, msg=''):
    logging.info('Assertion if false :' + str(what))
    if what is False:
        return True
    else:
        return False


def closeDriver():
	try:
		driver.quit()
	except Exception as e:
		pass



def iterTest(testMethod, testName, terminateOnFailure=False):
    if testMethod:
        res = True
        resultStr = testName + ' - OK'
        logging.info(resultStr)
    else:
        res = False
        resultStr = testName + ' - FAILED'
        logging.error(resultStr)
        if terminateOnFailure:
            sys.exit(1)
    testResultsList.append(resultStr)
    print(resultStr)
    return res

atexit.register(closeDriver)

success = True

print('Preconfigure')
iterTest(preconfigure(),'Preconfiguration',True)
print('Main test in browser')
logging.info('Starting main test in browser')
initDriver()
success = success & iterTest(test_subscr_portal_login(), 'Subscriber portal login')
#closeDriver()

print('Total Results of Teleconference tests:')
for reportStr in testResultsList:
    print(reportStr)
    logging.info(reportStr)

if not success:
    print(Fore.RED + 'Some tests failed!')
    logging.error('Some tests failed!')
    sys.exit(1)
else:
    print(Fore.GREEN + 'It seems to be all FINE...')
    logging.info('All test OK!')
    print('We did it!!')
    sys.exit(0)

