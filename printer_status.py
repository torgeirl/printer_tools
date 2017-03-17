from netsnmp import Varbind, VarList, snmpget
from os import environ, path
from subprocess import CalledProcessError, check_output, STDOUT
from sys import argv, exit

usage = 'Usage: %s <printer>...' % argv[0]

# Provide the paths to needed MIBs with a comma (!) separeted list
mibs_dir = path.abspath(path.join(path.dirname( __file__ ), '..', 'mibs'))
mibs_to_load = mibs_dir + '/Printer-MIB.my:' + mibs_dir + '/SNMPv2-MIB.txt'

def get_by_mib(printer_name, mib):
    '''Returns the value of a given Management Information Base (MIB) for a printer'''
    return snmpget(Varbind(mib), DestHost = printer_name, Community = 'public', Version = 1)

def ping(host):
    '''Silently pings the host once. Returns true if host answers; false if it doesn't.'''
    try:
        check_output(['ping', '-c', '1', host], stderr=STDOUT, universal_newlines=True)
    except CalledProcessError:
        return False
    return True

def get_printer_info(printer_name):
    '''Queries a printer and returns its info ready to print.'''
    # Loading MIBs with environ is a bit hacky, but worked.
    # TODO: configure netsnmp properly
    environ['MIBS'] = mibs_to_load

    # TODO: use VarList(Varbind<>...) to bulk all SNMP queries for performance boost
    #
    # ... but it's not yet supported: "Note that only one varbind should be contained 
    # in the VarList passed in. The code is structured to maybe handle this is the the 
    # future, but right now walking multiple trees at once is not yet supported and 
    # will produce insufficient results."

    model = map(str.strip, get_by_mib(printer_name, 'sysDescr.0')[0].split('/'))
    try:
        location = get_by_mib(printer_name, 'sysLocation.0')[0].split(',')[2]
    except IndexError:
        location = None
    display = get_by_mib(printer_name, 'prtConsoleDisplayBufferText.1.1')
    supply_level_black = get_by_mib(printer_name, 'prtMarkerSuppliesLevel.1.1')[0]
    supply_level_cyan = get_by_mib(printer_name, 'prtMarkerSuppliesLevel.1.3')[0]
    supply_level_magenta = get_by_mib(printer_name, 'prtMarkerSuppliesLevel.1.4')[0]
    supply_level_yellow = get_by_mib(printer_name, 'prtMarkerSuppliesLevel.1.5')[0]
    supply_level_waste = get_by_mib(printer_name, 'prtMarkerSuppliesLevel.1.2')[0]
    page_count = get_by_mib(printer_name, 'prtMarkerLifeCount.1.1')[0]

    info = 'Querying \033[1m' + printer_name.split('.')[0] + '\033[0m'
    if location:
        info += ' (rom ' + location +')'
    info += ':\nModel:\n'
    for line in model:
        info += '   %s\n' % line
    info += 'Display:\n'
    for line in display:
        info += '   %s\n' % line
    info += 'Supply status:\n'
    info += '%6i %% Black\n' % int(supply_level_black)
    info += '%6i %% Cyan\n' % int(supply_level_cyan)
    info += '%6i %% Magenta\n' % int(supply_level_magenta)
    info += '%6i %% Yellow\n' % int(supply_level_yellow)
    info += '%6i %% Waste\n' % int(supply_level_waste)
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
