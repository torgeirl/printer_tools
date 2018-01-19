from netsnmp import snmpgetnext, Varbind
from sys import argv, exit

usage = 'Usage: %s <printer address>...' % argv[0]

def get_by_oid(printer_name, oid):
    '''Returns the value of a given Object Identifier (OID) for a printer'''
    return snmpgetnext(Varbind(oid), DestHost = printer_name, Community = 'public', Version = 1)

def get_billing_info(printer_name):
    copier_mono = get_by_oid(printer_name, '.1.3.6.1.4.1.367.3.2.1.2.19.5.1.9.17')[0]
    copier_full_color = get_by_oid(printer_name, '.1.3.6.1.4.1.367.3.2.1.2.19.5.1.9.61')[0]
    printer_mono = get_by_oid(printer_name, '.1.3.6.1.4.1.367.3.2.1.2.19.5.1.9.19')[0]
    printer_full_color = get_by_oid(printer_name, '.1.3.6.1.4.1.367.3.2.1.2.19.5.1.9.10')[0]
    printer_two_color = get_by_oid(printer_name, '.1.3.6.1.4.1.367.3.2.1.2.19.5.1.9.9')[0]
    total = get_by_oid(printer_name, '.1.3.6.1.2.1.43.10.2.1.4')[0]

    info = 'Querying \033[1m' + printer_name.split('.')[0] + '\033[0m:'
    info += '\nCopier black/white: %s' % copier_mono
    info += '\nPrinter black/white: %s' % printer_mono
    info += '\nCopier full color: %s' % copier_full_color
    info += '\nPrinter full color: %s' % printer_full_color
    info += '\nPrinter two color: %s' % printer_two_color
    info += '\nTotal: %s\n' % total
    return info

if __name__ == '__main__':
    if len(argv) > 1:
        print '\n',
        for arg in argv[1:]:
            print get_billing_info(arg.lower())
    else:
        print usage; exit(1)
