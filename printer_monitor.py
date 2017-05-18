from datetime import timedelta
import json
from netsnmp import Varbind, VarList, snmpget
from optparse import OptionParser
from os import environ, path, system
import re
from subprocess import CalledProcessError, check_output, PIPE, Popen, STDOUT
from sys import argv, exit
import time

'''Printer Monitor.

Checks if Ricoh printers are online, and if they report critical errors.

Options:
  -d=True --debug=True      Run in debug mode
 
Made by Torgeir Lebesbye (torgeirl) during the spring of 2017. MIT License.
'''

usage = 'Usage: %s [-d=True] <printer>...' % argv[0]

# Provide the paths to needed MIBs with a colon (!) separeted list
mibs_dir = path.abspath(path.join(path.dirname( __file__ ), '..', 'mibs'))
mibs_to_load = mibs_dir + '/Printer-MIB.my:' + mibs_dir + '/SNMPv2-MIB.txt:' + mibs_dir + '/DISMAN-EVENT-MIB.txt'
environ['MIBS'] = mibs_to_load

def ping(host, times=1):
    '''Silently pings the host once. Returns true if host answers; false if it doesn't.'''
    try:
        check_output(['ping', '-c', times, host], stderr=STDOUT, universal_newlines=True)
    except CalledProcessError:
        return False
    return True

def run_script(script, stdin=None):
    """Returns (stdout, stderr), raises error on non-zero return code"""
    proc = Popen(['bash', '-c', script], stdout=PIPE, stderr=PIPE, stdin=PIPE)
    stdout, stderr = proc.communicate()
    if proc.returncode:
        raise ScriptException(proc.returncode, stdout, stderr, script)
    return stdout, stderr

class ScriptException(Exception):
    def __init__(self, returncode, stdout, stderr, script):
        self.returncode = returncode
        self.stdout = stdout
        self.stderr = stderr
        Exception.__init__('Error in script')

def get_error_list(printer):
    '''Returns all errors and warnings from the printer as a list.'''
    script = 'snmpwalk -v 2c -c public -M %s/ -m all %s | grep -E Printer-MIB::prtAlertSeverityLevel.' % (mibs_dir, printer)
    errors = list(filter(None, run_script(script)))
    if errors > 0:
        errors.append(filter(None, errors.pop(0).split('\n')))
        errors.insert(0, printer.split('.')[0])
    return errors

def get_by_mib(printer_name, mib):
    '''Returns the value of a given Management Information Base (MIB) for a printer'''
    return snmpget(Varbind(mib), DestHost = printer_name, Community = 'public', Version = 1)

def parse_errors(errors):
    parsed_errors = ''
    printer = errors[0]
    for error in errors[1]:
        err_id = re.findall(r'\.(\d+\.\d+)', error)[0]
        err_desc = get_by_mib(printer + '.printer.uio.no', 'prtAlertDescription.' + err_id)[0].split(' {')[0]
        err_ticks = int(get_by_mib(printer + '.printer.uio.no', 'prtAlertTime.' + err_id)[0])
        system_uptime_ticks = int(get_by_mib(printer + '.printer.uio.no', 'sysUpTimeInstance')[0])
        err_time = str(timedelta(seconds=(system_uptime_ticks - err_ticks)/100)) #error time appears relative to system uptime
        message = '[%s] \'%s\' in %s\n' % (printer, err_desc, err_time)
        parsed_errors += message
    return parsed_errors

if __name__ == '__main__':
    parser = OptionParser(usage=usage)
    parser.add_option('-d', '--debug',
        default=False,
        help='Run script in debug mode')
    (options, args) = parser.parse_args()

#    try:
    start_time = time.time()
    error_list = []
    parsed_errors = ''
    for arg in argv[1:]:
        errors = get_error_list(arg)
        if errors > 0:
            error_list.append(errors)    
    if len(error_list) > 0:
        for item in error_list:
            parsed_errors += parse_errors(item)
        print parsed_errors, #TODO remove comma?
        end_time = time.time()
        print 'CRITICAL ERRORS OR WARNINGS DETECTED (%.1f sec)' % (end_time - start_time)
    else:
        end_time = time.time()
        print 'OK (%.1f sec)' % (end_time - start_time)       
#    except:
#        print usage; exit(1)
