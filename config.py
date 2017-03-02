import json, sys, argparse, os
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

#import json

parser = argparse.ArgumentParser()
parser.add_argument('-c', '--custom_config', type=argparse.FileType(), help="Using custom config json file")
args = parser.parse_args()

if args.custom_config is not None:
    print("Custom json config is used: " + str(os.path.realpath(args.custom_config.name)))
    testConfigFile = args.custom_config
else:
    print('Default json config is used')
    try:
        testConfigFile = open('subscr_portal_test.json')
    except Exception as e:
        print('ERROR: Cannot open json config file')
        sys.exit(1)

try:
    testConfigJson = json.loads(testConfigFile.read())
except Exception as e:
    print('ERROR: Cannot parse json config file!')
    sys.exit(1)
finally:
    testConfigFile.close()

if testConfigJson['ModulePath'] not in 'None':
    sys.path.append(testConfigJson['ModulePath']) # add custom path to external modules if it in json config


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
webDriverServerIP = '192.168.118.37'