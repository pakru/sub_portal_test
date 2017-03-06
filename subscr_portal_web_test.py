import config, logging
from selenium import webdriver
#from selenium.webdriver.remote.webdriver import WebDriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import Select
from selenium.common.exceptions import NoSuchElementException
from selenium.common.exceptions import NoAlertPresentException
from selenium.webdriver.common.desired_capabilities import DesiredCapabilities
import unittest, time, re, sys
from time import sleep
import json
import ssh_cocon.ssh_cocon as ccn
from colorama import Fore

testingDomain = config.domainName
sipUsersCfgJson = config.testConfigJson['Users']
sipShareCfgJson = config.testConfigJson['ShareSet'][0]

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

    if ccn.sipShareSetDeclare(sharesetName=config.shareSetName,sipIP=config.shareSetIP,sipPort=config.shareSetPort):
        print(Fore.GREEN + 'Successful shareSet creation')
    else:
        print(Fore.RED + 'Smthing happen wrong with shareSet creation...')
        return False

    if ccn.sipTransportShareSetup(dom=testingDomain,sharesetName=config.shareSetName):
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

    if ccn.ssEnable(dom=testingDomain,subscrNum=sipUsersCfgJson[0]['Number'],ssNames='*'):
        print(Fore.GREEN + 'Successful Subscriber services enable')
    else:
        print(Fore.RED + 'Smthing happen wrong with subscribers services enable...')
        return False

    if ccn.setAliasSubscriberPortalLoginPass(dom=testingDomain,subscrNum=sipUsersCfgJson[0]['Number'], sipGroup=sipUsersCfgJson[0]['SipGroup'],
                                             login=sipUsersCfgJson[0]['Number'], passwd=sipUsersCfgJson[0]['Password']):
        print(Fore.GREEN + 'Successful Subscriber portal login/pass set')
    else:
        print(Fore.RED + 'Failed to set Subscriber portal login/pass...')
        return False

    return True



class SubscriberPortal(unittest.TestCase):
    def setUp(self):
        #self.driver = webdriver.Chrome()
        if config.usedBrowser is 'Chrome':
            self.capabilities = DesiredCapabilities.CHROME
        else:
            self.capabilities = DesiredCapabilities.CHROME

        self.driver = webdriver.Remote('http://'+ config.webDriverServerIP +':4444/wd/hub',desired_capabilities=self.capabilities)
        #self.driver = webdriver.Firefox()
        self.driver.implicitly_wait(10)
        self.base_url = config.httpProtocol + '://' + config.host + ':' + config.httpPort
        self.verificationErrors = []
    # self.accept_next_alert = True

    def test_subscr_portal_login(self):
        driver = self.driver
        driver.set_window_size(1200,800)
        driver.get(self.base_url)


        self.wait_until_element_present(By.ID, 'login')

        driver.find_element_by_id("login").clear()
        driver.find_element_by_id("login").send_keys(sipUsersCfgJson[0]['Number'])
        driver.find_element_by_id("password").clear()
        driver.find_element_by_id("password").send_keys(sipUsersCfgJson[0]['Password'])
        #chooos in combobox
        Select(driver.find_element_by_id("domain")).select_by_visible_text(testingDomain) # choose domain in combobox
        #sleep(2)
        #driver.find_element_by_xpath("//select[@id='domain']/option").click()
        sleep(0.5)
        driver.find_element_by_id("login_btn").click()  # logining
        self.assertTrue(self.is_element_present(By.XPATH, "//img[@title='Eltex']")) ## check main banner
        #self.assertTrue(self.is_element_present(By.XPATH, "//TD[text()='Петя']")) ## check disp name text
        self.assertTrue(self.is_element_present(By.XPATH, "//TD[text()='"+ sipUsersCfgJson[0]['Number'] +"']")) ## check subscriber number
        sleep(0.5)
        driver.find_element_by_id("ss_list").click() # switch to ss list
        self.assertTrue(self.is_element_present(By.XPATH, "//*[contains(text(), 'Обслуживание абонента')]")) # assert text
        sleep(0.5)

        driver.find_element_by_xpath("//LABEL[@for='ss_list_all']").click() ## switch to all ss
        sleep(2)
        self.assertTrue(self.is_element_present(By.XPATH, "//label[contains(text(), 'Трехсторонняя конференция')]")) # check if services displayed
        driver.find_element_by_xpath("//LABEL[@for='ss_list_activated']").click() ## switch to activated ss
        sleep(2)
        self.assertFalse(self.is_element_present(By.XPATH, "//label[contains(text(), 'Трехсторонняя конференция')]"))  # check if services disapeared

        driver.find_element_by_id("call_history").click() # switch to ss call_history
        self.assertTrue(self.is_element_present(By.XPATH, "//*[contains(text(), 'История вызовов')]")) # assert text
        sleep(0.5)

        driver.find_element_by_id("reset").click() # switch to ss call_history
        self.assertTrue(self.is_element_present(By.XPATH, "//*[contains(text(), 'Информация об абоненте')]")) # assert text
        sleep(0.5)

        driver.find_element_by_xpath("//*[contains(text(), 'Выход')]").click() ## logout
        self.assertTrue(self.is_element_present(By.ID, 'login'))


    def wait_until_element_present(self, how, what, wait_timeout=10):
        logging.info('Waiting for ' + str(what) + ' to be appeared on webpage')
        for i in range(wait_timeout):
            print('.', end='')
            try:
                #print('trying to find element')
                if self.is_element_present(how, what):
                    # print('found')
                    return True
            except Exception as e:
                pass
            sleep(1)
        else:
            #print('Didnt found login element')
            self.fail("time out")
            return False

    def is_element_present(self, how, what):
        logging.info('Check if element ' + str(what) + ' presents')
        try:
            self.driver.find_element(by=how, value=what)
        except NoSuchElementException as e:
            #print('No such element exception!')
            logging.warning('No such element ' + str(what))
            return False
        except Exception as e:
            print('Exception :' + str(e))
            logging.warning('No such element ' + str(what))
            return False
        return True

    def is_alert_present(self):
        try:
            self.driver.switch_to_alert()
        except NoAlertPresentException as e:
            return False
        return True

    def tearDown(self):
        self.driver.quit()
        self.assertEqual([], self.verificationErrors)


print('Preconfigure')

if not preconfigure():
    logging.error('Failed at preconfiguration')
    print('Failed at preconfigure')
    sys.exit(1)

print('Main test in browser')
logging.info('Starting main test in browser')
unittest.main()

sys.exit(0)