from app import app
import logging
import time
import os
from logging import FileHandler, Formatter

if not os.path.exists('logs/'):
    os.mkdir('logs')
logpath = os.getcwd() + '/logs/' + time.asctime() + '.log'
datefmt = '%m/%d/%g@%H:%M'
fh = FileHandler(logpath)
fh.setLevel(logging.DEBUG)
fmt = Formatter('%(asctime)s:%(levelname)s - %(module)s:%(funcName)s - %(message)s')
fmt.datefmt = datefmt
fh.setFormatter(fmt)
app.logger.addHandler(fh)

app.run(host='0.0.0.0', port=5000, debug=True)
