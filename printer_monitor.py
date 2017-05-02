from datetime import timedelta
import json
from netsnmp import Varbind, VarList, snmpget
from optparse import OptionParser
from os import environ, path
import re
from subprocess import CalledProcessError, check_output, PIPE, Popen, STDOUT
from sys import argv, exit
import time

# Provide the paths to needed MIBs with a colon (!) separeted list
mibs_dir = path.abspath(path.join(path.dirname( __file__ ), '..', 'mibs'))
mibs_to_load = mibs_dir + '/Printer-MIB.my:' + mibs_dir + '/SNMPv2-MIB.txt'
environ['MIBS'] = mibs_to_load

def ping(host):
    '''Silently pings the host once. Returns true if host answers; false if it doesn't.'''
    try:
        check_output(['ping', '-c', '1', host], stderr=STDOUT, universal_newlines=True)
    except CalledProcessError:
        return False
    return True

def run_script(script_file, argument):
    '''Runs an external script file and return its output.'''
    pipe = Popen([script_file, argument], stdout=PIPE)
    return pipe.communicate()[0]

def get_critical_errors():
    '''Returns all critical errors by running an external Bash script.''' #TODO: needs optimization
    return run_script('./snmpwalk_grep_all.sh', 'Printer-MIB::prtAlertSeverityLevel.+critical').rstrip()

def get_by_mib(printer_name, mib):
    '''Returns the value of a given Management Information Base (MIB) for a printer'''
    return snmpget(Varbind(mib), DestHost = printer_name, Community = 'public', Version = 1)


error_log = get_critical_errors()
parsed_errors = ''

for line in error_log.split('\n'):
    printer = line.split()[0].strip('[]')
    err_id = re.findall(r'\.(\d+\.\d+)', line)[0]
    err_desc = get_by_mib(printer + '.printer.uio.no', 'prtAlertDescription.' + err_id)[0].split(' {')[0]
    err_secs = int(get_by_mib(printer + '.printer.uio.no', 'prtAlertTime.' + err_id)[0])/100
    err_time = str(timedelta(seconds=err_secs))
    message = '[%s] critical error: \'%s\' in %s\n' % (printer, err_desc, err_time)
    parsed_errors += message

print parsed_errors

#if __name__ == '__main__':
#    if len(argv) > 1:
#        for arg in argv[1:]:
#            print ping(arg)
#    else:
#        print usage; exit(1)
