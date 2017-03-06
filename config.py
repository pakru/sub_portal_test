import json, sys, argparse, os, logging
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
parser.add_argument ('-g', '--global_ccn_lock', type=argparse.FileType('w'), help="Lock file for coconInt")
args = parser.parse_args()


global_ccn_lock = None
if args.global_ccn_lock:
    print('Acepted lock file')
    global_ccn_lock = args.global_ccn_lock

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

#if testConfigJson['ModulePath'] not in 'None':
sys.path.append(testConfigJson['SystemVars'][0]['%%MODULE_PATH%%']) # add custom path to external modules if it in json config

logPath = testConfigJson['SystemVars'][0]['%%LOG_PATH%%']
logFile = logPath+'/'+testConfigJson['TestScript'] + '.log'

logging.basicConfig(filename=logFile, filemode='w', format = u'%(asctime)-8s %(levelname)-8s [%(module)s -> %(funcName)s:%(lineno)d] %(message)-8s', level = logging.INFO)


login = testConfigJson['SystemVars'][0]['%%DEV_USER%%']
password = testConfigJson['SystemVars'][0]['%%DEV_PASS%%']
host = testConfigJson['SystemVars'][0]['%%SERV_IP%%']
port = int(testConfigJson['SystemVars'][0]['%%CCN_PORT%%'])
httpProtocol = testConfigJson['httpProtocol']
httpPort = testConfigJson['httpPort']
domainName = testConfigJson['DomainName']
shareSetName = testConfigJson['ShareSet'][0]['ShareSetName']
shareSetIP = testConfigJson['ShareSet'][0]['ShareIP']
shareSetPort = testConfigJson['ShareSet'][0]['SharePort']
webDriverServerIP = testConfigJson['SeleniumSettings'][0]['ServerIP']
usedBrowser = testConfigJson['SeleniumSettings'][0]['Browser']