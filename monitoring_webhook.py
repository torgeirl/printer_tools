from matterhook import Webhook
from printer_monitor import get_printer_errors
import time
import webhookconfig as cfg

mwh = Webhook(cfg.webhook_url, cfg.webhook_key)

if __name__ == '__main__':
    start_time = time.time()
    errors = ''
    for printer in cfg.printers:
        errors += get_printer_errors(printer, cfg.ignore_list, pings=3)
    end_time = time.time()
    if len(errors) > 0:
        mwh.send(errors.replace('\xe6', 'ae').replace('\xf8', 'oe').replace('\xe5', 'aa'))
