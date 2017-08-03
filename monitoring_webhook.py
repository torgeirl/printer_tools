from matterhook import Webhook

import config as cfg
from printer_monitor import get_printer_errors

if __name__ == '__main__':
    errors = ''
    for printer in cfg.printers:
        errors += get_printer_errors(printer, cfg.ignore_list, pings=3, quiet=True)
    if len(errors) > 0:
        mwh = Webhook(cfg.webhook_url, cfg.webhook_key)
        mwh.send(errors.replace('\xe6', 'ae').replace('\xf8', 'oe').replace('\xe5', 'aa'))
