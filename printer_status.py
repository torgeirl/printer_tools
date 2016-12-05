from sys import argv, exit
from netsnmp import Varbind, VarList, snmpget, snmpgetnext

usage = 'Usage: %s <printer>...' % argv[0]

def get_by_oid(printer_name, oid):
    '''Returns the value of a given Object Identifier (OID) for a printer'''
    return snmpgetnext(Varbind(oid), DestHost = printer_name, Community = 'public', Version = 1)

def get_printer_info(printer_name):
    #TODO: use VarList(Varbind<>...) to bulk all SNMP queries for performance boost

    model = get_by_oid(printer_name, '.1.3.6.1.2.1.25.3.2.1.3')
    lines = get_by_oid(printer_name, '.1.3.6.1.2.1.43.5.1.1.11') # TODO: not in use??!
    chars = get_by_oid(printer_name, '.1.3.6.1.2.1.43.5.1.1.12')
    display = get_by_oid(printer_name, '.1.3.6.1.2.1.43.16.5.1.2')

    supply_desc = get_by_oid(printer_name, '.1.3.6.1.2.1.43.11.1.1.6')
    supply_max = get_by_oid(printer_name, '.1.3.6.1.2.1.43.11.1.1.8')
    supply_level = get_by_oid(printer_name, '.1.3.6.1.2.1.43.11.1.1.9')

    tray_unit = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.8')
    tray_max = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.9')
    tray_level = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.10')
    tray_status = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.11')
    tray_type = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.12')
    tray_tray = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.13')

    size_x = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.7')
    size_y = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.6')
    size_type = get_by_oid(printer_name, '.1.3.6.1.2.1.43.8.2.1.3')

    page_count = get_by_oid(printer_name, '.1.3.6.1.2.1.43.10.2.1.4')



    info = 'Querying %s\n' % printer_name
    info += 'Model:\n'
        #TODO
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
        for arg in argv[1:]:  
            print get_printer_info(arg.lower())
    else:
        print usage; exit(1)
