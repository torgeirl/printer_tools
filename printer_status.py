from netsnmp import Varbind, VarList, snmpget, snmpgetnext
from subprocess import CalledProcessError, check_output, STDOUT
from sys import argv, exit

usage = 'Usage: %s <printer>...' % argv[0]

def get_by_oid(printer_name, oid):
    '''Returns the value of a given Object Identifier (OID) for a printer'''
    return snmpget(Varbind(oid), DestHost = printer_name, Community = 'public', Version = 1)

def get_next_by_oid(printer_name, oid):
    '''Returns the value of a given Object Identifier (OID) for a printer'''
    return snmpgetnext(Varbind(oid), DestHost = printer_name, Community = 'public', Version = 1)

def ping(host):
    try:
        check_output(['ping', '-c', '1', host], stderr=STDOUT, universal_newlines=True)
    except CalledProcessError:
        return False
    return True

def get_printer_info(printer_name):
    # TODO: use VarList(Varbind<>...) to bulk all SNMP queries for performance boost
    #
    # ... but it's not yet supported: "Note that only one varbind should be contained 
    # in the VarList passed in. The code is structured to maybe handle this is the the 
    # future, but right now walking multiple trees at once is not yet supported and 
    # will produce insufficient results."

    model = get_next_by_oid(printer_name, '.1.3.6.1.2.1.25.3.2.1.3')
    lines = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.5.1.1.11') # TODO: not in use??!
    chars = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.5.1.1.12')
    display = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.16.5.1.2')

    supply_desc = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.11.1.1.6')
    supply_max = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.11.1.1.8')
    supply_level = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.11.1.1.9')

    tray_unit = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.8')
    tray_max = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.9')
    tray_level = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.10')
    tray_status = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.11')
    tray_type = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.12')
    tray_tray = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.13')

    size_x = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.7')
    size_y = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.6')
    size_type = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.3')

    page_count = get_next_by_oid(printer_name, '.1.3.6.1.2.1.43.10.2.1.4')

    info = 'Querying \033[1m' + printer_name.split('.')[0] + '\033[0m' + ':'
    info += '\nModel:\n'
    for line in model:
        info += '   %s\n' % line
    info += 'Display:\n'
    for i, element in enumerate(display):
        info += '%4i: [ %-*s ]\n' % (i+1, int(chars[0]), element)
    info += 'Supply status for %s:\n' % printer_name
        #TODO
    info += 'Tray status for %s:\n' % printer_name
        #TODO
    info += 'Page count: %s\n' % page_count
    return info

if __name__ == '__main__':
    if len(argv) > 1:
        print '\n',
        for arg in argv[1:]:
            if ping(arg):
                print get_printer_info(arg.lower())
            elif ping(arg + '.printer.uio.no'):
                print get_printer_info(arg.lower() + '.printer.uio.no')
            else:
                print '\033[91mError\033[0m: host \'' + arg.lower() + '\' not known'
    else:
        print usage; exit(1)
