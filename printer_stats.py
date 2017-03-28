from datetime import date, timedelta
import json
from optparse import OptionParser
from os.path import dirname, join
from netsnmp import snmpgetnext, Varbind
from sys import argv, exit
import time

'''Printer Stats.

Stores the page count history for printers. Unless the script is provided with start 
and end dates, it will default to page count development since yesterday 
(Monday-Saturday) or the last week's development (Sundays).

Options:
  -s --start <YYYY-MM-DD>   Start date
  -e --end <YYYY-MM-DD>     End date
  -a --add <name>           Add a new printer
  -r --remove <name>        Remove a printer
  -d=True --debug=True      Run in debug mode

Made by Torgeir Lebesbye (torgeirl) during the fall of 2016. MIT License.
'''

usage = 'Usage: %s [-s startdate -e enddate] [-a new_printer]...' % argv[0]
json_file = 'data.json'

def map_path(target_name):
    '''Enables path names to be dynamically ascertained at runtime.'''
    return join(dirname(__file__), target_name).replace('\\', '/')

def get_by_oid(printer_name, oid):
    '''Returns the value of a given Object Identifier (OID) for a printer'''
    return snmpgetnext(Varbind(oid), DestHost = printer_name, Community = 'public', Version = 1)

def get_page_count(printer_name):
    '''Returns a printer's page count'''
    page_count = get_by_oid(printer_name, '.1.3.6.1.2.1.43.10.2.1.4')[0]
    if not page_count is None and not page_count is '0':
        return page_count
    else:
        return 'n/a'

def add_printer(printer, location):
    '''Add a new printer to the JSON file'''
    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    if printer not in data:
        try:
            data[printer] = {}
            data[printer]['location'] = str(location)
            with open(map_path(json_file), 'w') as outfile:
                json.dump(data, outfile)
            return '%s has successfully been added to dataset' % printer
        except:
            return 'Error: something went wrong while trying to add \'%s\'' % printer
    else:
        return 'Error: %s already in dataset' % printer

def remove_printer(printer):
    '''Remove a printer from the JSON file'''
    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    if printer in data:
        try:
            data.pop(printer, None)
            with open(map_path(json_file), 'w') as outfile:
                json.dump(data, outfile)
            return '%s has successfully been removed from dataset' % printer
        except:
            return 'Error: something went wrong while trying to remove \'%s\'' % printer
    else:
        return 'Error: \'%s\' not in dataset' % printer

def check_printers(debug=False):
    '''Checks page count on printer in the JSON file.'''
    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    for printer in data.keys():
        if debug:
            status = 'Querying %s ...' % printer.split('.')[0]
            print status,
        start_time = time.time()
        page_count = get_page_count(printer)
        end_time = time.time()
        data[printer][date.strftime(date.today(), '%Y-%m-%d')] = page_count
        if debug:
            print 'OK (%.1f sec)' % (end_time - start_time)
    with open(map_path(json_file), 'w') as outfile:
        json.dump(data, outfile)

def make_report(start_date, end_date):
    '''Returns a report on page count increase for the period.'''
    with open(map_path(json_file), 'r') as infile:
        data = json.load(infile)
    total = 0
    report = '\nPRINTER USAGE BETWEEN %s AND %s:\n\n' % (start_date, end_date)
    report += '     PRINTER | ROOM# |  COUNT  | INCREASE\n'
    report += '-----------------------------------------\n'
    for printer in sorted(data,key=lambda x:int(data[x]['location'])):
        start = data[printer].get(start_date, 'n/a')
        end = data[printer].get(end_date, 'n/a')
        if start.isdigit() and end.isdigit():
            increase = int(end)-int(start)
            total += increase
            increase = str(increase)
        else:
            increase = 'n/a'
        location = int(data[printer].get('location'))
        report += '%12s | %5i | %7s | +%s\n' % (printer.split('.')[0], location, end, increase)
    report += '\n%i printers, total increase in period: %i pages\n' % (len(data), total)
    return report

if __name__ == '__main__':
    parser = OptionParser(usage=usage)
    parser.add_option('-s', '--start',
        help='Spesify a start date (YYYY-MM-DD)')
    parser.add_option('-e', '--end',
        help='Spesify an end date (YYYY-MM-DD)')
    parser.add_option('-a', '--add',
        help='Add a new printer')
    parser.add_option('-r', '--remove',
        help='Remove a printer')
    parser.add_option('-d', '--debug',
        default=False,
        help='Run script in debug mode')
    (options, args) = parser.parse_args()

    if options.add != None:
        text = 'Please provide the location (rom number) of \'%s\':' % options.add
        print text,
        location = raw_input()
        print add_printer(options.add, location)

    if options.remove != None:
        text = 'Are you sure you want to remove \'%s\' from the dataset, (Y/N):' % options.remove
        print text,
        reply = raw_input()
        print reply
        if reply.lower() == 'y':
            print remove_printer(options.remove)
        else:
            print '0K, leaving %s in the dataset. Be careful with the remove command!' % options.remove

    if options.start != None and options.end != None:
        start_date = options.start
        end_date = options.end
    else:
        if date.weekday(date.today()) == 6:
            start_date = date.strftime(date.today()- timedelta(7), '%Y-%m-%d')
        else:
            start_date = date.strftime(date.today()- timedelta(1), '%Y-%m-%d')
        end_date = date.strftime(date.today(), '%Y-%m-%d')
    try:
        check_printers(debug=options.debug)
        print make_report(start_date, end_date)
    except:
        print usage; exit(1)
