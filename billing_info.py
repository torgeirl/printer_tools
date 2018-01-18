from sys import argv, exit

from printer_stats import get_by_oid
from printer_status import ping

usage = 'Usage: %s <printer>...' % argv[0]

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
    info += '\n\nCopier full color: %s' % copier_full_color
    info += '\nPrinter full color: %s' % printer_full_color
    info += '\nPrinter two color: %s' % printer_two_color
    info += '\n\nTotal: %s\n' % total
    return info

if __name__ == '__main__':
    if len(argv) > 1:
        print '\n',
        for arg in argv[1:]:
            if ping(arg):
                print get_billing_info(arg.lower())
            elif ping(arg + '.printer.uio.no'):
                print get_billing_info(arg.lower() + '.printer.uio.no')
            else:
                print '\033[91mError\033[0m: host \'' + arg.lower() + '\' not known'
    else:
        print usage; exit(1)
