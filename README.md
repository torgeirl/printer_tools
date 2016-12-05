Printer Tools
=============

## Overview
Python scripts made to help you monitor printers on a network.

## Assumptions
* You're running the scripts on a server with access to the printer network.
* [Python bindings of Net-SNMP](https://net-snmp.svn.sourceforge.net/svnroot/net-snmp/trunk/net-snmp/python/README) are available on that server.

## Usage
`$ python printer_stats.py [-s startdate -e enddate] [-a new_printer]`
`$ python printer_status.py <printer>...`

## Documentation

### printer_stats
`get\_page\_count()` asks a printer for its page count using the `get\_by\_oid()` function and returns that number, or `n/a` if not found.

`add\_printer()` and `remove\_printer()` handles adding and removing a printer from the JSON file.

`check_printers()` checks the page count for all printers using the `get\_page\_count()` function.

`make_report()` returns a report on page count increase for the given period.

### printer_status


## Setting up CRON job
`$ export VISUAL=vim; crontab -e` opens the list of CRON jobs the user have on the server in the VIM editor:

    TERM=xterm
    45 23 * * * python printer_stats.py 2>&1 | mail -s "Subject" "mail@example.com"

## Credits
`printer_status.py` is essentially a port of an old (but still functional) Perl script written by [Peder Stray](https://github.com/pstray) in 2007, 2008 and 2011. 

## License
See the [LICENSE](LICENSE.md) file for license rights and limitations (MIT).
