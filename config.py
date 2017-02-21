'''
login = 'admin'
password = 'password'
host = '192.168.118.47'
port = 8023
'''
testConfigJson = None
coreNode = 'core1@ecss1'
sipNode = 'sip1@ecss1'
dsNode = 'ds1@ecss1'

import json

try:
    testConfigFile = open('subscr_portal_test.json')
    testConfigJson = json.loads(testConfigFile.read())
except:
    print('Cannot open json config file for test')
finally:
    testConfigFile.close()

login = testConfigJson['Cocon'][0]['Login']
password = testConfigJson['Cocon'][0]['Password']
host = testConfigJson['Cocon'][0]['Host']
port = int(testConfigJson['Cocon'][0]['Port'])
httpProtocol = testConfigJson['httpProtocol']
httpPort = testConfigJson['httpPort']
domainName = testConfigJson['DomainName']
shareSetName = testConfigJson['ShareSet'][0]['ShareSetName']
shareSetIP = testConfigJson['ShareSet'][0]['ShareIP']
shareSetPort = testConfigJson['ShareSet'][0]['SharePort']