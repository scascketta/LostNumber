#!/usr/bin/env python
from logging import FileHandler, Formatter
from app import app
import logging
import time
import os


def config_logging(log_dname="logs"):
	log_dname = "{0}/".format(log_dname)
	if not os.path.exists(log_dname):
	    os.mkdir(log_dname)
	logpath = os.getcwd() + "/{0}/".format(log_dname) + time.asctime() + '.log'
	datefmt = '%m/%d/%g@%H:%M'
	fh = FileHandler(logpath)
	fh.setLevel(logging.DEBUG)
	fmt = Formatter('%(asctime)s:%(levelname)s - %(module)s:%(funcName)s - %(message)s')
	fmt.datefmt = datefmt
	fh.setFormatter(fmt)
	app.logger.addHandler(fh)
	return app


if __name__ == '__main__':
	app = config_logging()
	app.run(host='0.0.0.0', port=5000, debug=True)
