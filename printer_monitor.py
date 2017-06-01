from datetime import timedelta
from netsnmp import snmpget, snmpwalk, Varbind
from os import environ, path
from re import search
from subprocess import CalledProcessError, check_output, STDOUT
from sys import argv, exit
import time

usage = 'Usage: python %s <printer_address>...' % argv[0]

mibs_dir = path.abspath(path.join(path.dirname( __file__ ), '..', 'mibs'))
mibs_to_load = mibs_dir + '/Printer-MIB.my:' + mibs_dir + '/DISMAN-EVENT-MIB.txt' #colon-separated (!) list
environ['MIBS'] = mibs_to_load

ignore_list = 'low:|lite:|no paper|tomt for papir|low power mode|energy saver mode|energisparemodus|modus for lavt str|warming up|varmer opp|nearly full|not detected: tray|not detected: input|mismatch: paper size and Type'

def ping(host, times=1):
    '''Silently pings the host once. Returns true if host answers; false if it doesn't.'''
    try:
        check_output(['ping', '-c', str(times), host], stderr=STDOUT, universal_newlines=True)
    except CalledProcessError:
        return False
    return True

def walk_mib(device_address, mib):
    '''Returns the value of all children of the given Management Information Base (MIB) for a network device'''
    return snmpwalk(Varbind(mib), DestHost = device_address, Community = 'public', Version = 1)

def get_mib(device_address, mib):
    '''Returns the value of the given Management Information Base (MIB) for a network device'''
    return snmpget(Varbind(mib), DestHost = device_address, Community = 'public', Version = 1)

def get_printer_errors(printer_address, ignore_list):
    '''Returns all errors from a printer'''
    if ping(printer_address): #TODO: impliment some actual error handling
        err_descriptions = list(walk_mib(printer_address, 'prtAlertDescription.1'))
        err_ticks = list(walk_mib(printer_address, 'prtAlertTime.1'))
        if err_descriptions:
            parsed_errors = ''
            system_uptime_ticks = int(get_mib(printer_address, 'sysUpTimeInstance')[0])
            for index, description in enumerate(err_descriptions):
                err_desc = description.split('{')[0] 
                if not search(ignore_list, err_desc.lower()):
                    err_time = str(timedelta(seconds=(system_uptime_ticks - int(err_ticks[index]))/100))
                    parsed_errors += '[%s] %s in %s\n' % (printer_address.split('.')[0].upper(), err_desc, err_time)
            return parsed_errors
        else:
            return ''
    else:
        return '[%s] host \'%s\' unknown or offline\n' % (printer_address.split('.')[0].upper(), printer_address)

if __name__ == '__main__':
    if len(argv) > 1:
        start_time = time.time()
        errors = ''
        for arg in argv[1:]:
            errors += get_printer_errors(arg, ignore_list)
        end_time = time.time()
        if len(errors) > 0:
            print errors
            print 'DONE: %i printers checked in %.1f seconds' % (len(argv)-1, end_time - start_time)
    else:
        print usage; exit(1)
