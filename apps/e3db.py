#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
Created on Fri Dec 17 11:08:30 2014

@author: Fabrizio Coccetti (fabrizio.coccetti@centrofermi.it) [www.fc8.net]
"""

import os
import MySQLdb
import ConfigParser
import pickle
import logging
import logging.config
from e3monitor.config.__files_server__ import (logConfigFile,
                                               dbConfigFile,
                                               plkDqmFile,
                                               pathWorkDir)
from e3monitor.db.E3DbDqmSchools import E3DbDqmSchools

# List with the name of the Schools
schoolNames = []
# Class with methods with last run in DQM from the database
dqmData = E3DbDqmSchools()

# Set up logging
logging.config.fileConfig(logConfigFile)
logger = logging.getLogger('full')
logger.info('Started')
logger = logging.getLogger('plain')

# Reading db ini file
logger.info('Reading ' + dbConfigFile)
parser = ConfigParser.ConfigParser()
parser.read(dbConfigFile)
host = parser.get('General', 'host')
user = parser.get('General', 'user')
dbname = parser.get('General', 'dbname')
passwd = parser.get('General', 'passwd')

# Connecting to the database
logger.info('Connecting to %s on %s (as %s)' % (dbname, host, user))
db = MySQLdb.connect(host=host, user=user, passwd=passwd, db=dbname)

cur = db.cursor()

# Connect to the School's table and get the school name list
logger.info('Connect to the School\'s table and get the school name list')
query = "SELECT name FROM telescope_ids;"
logger.info('Get the School\'s name list: ' + query)
cur.execute(query)
schoolNames = [item[0] for item in cur.fetchall()]
sorted(schoolNames)

# Query for the last run data of each school
logger.info('Query for the last run data of each school')
query = ("SELECT * FROM runs WHERE station_name = %s "
         "AND processing_status_code=0 "
         "ORDER BY last_update DESC LIMIT 1;")
logger.info('About to query: ' + query)
for _schoolName in schoolNames:
    cur.execute(query, _schoolName)
    _entry = cur.fetchone()
    if _entry is None:
        continue
    # Assign parameter to the class
    dqmData.add_entry(_schoolName, _entry)
    logger.info('Read School: ' + _schoolName)
    logger.info(dqmData.schoolData(_schoolName))

# Save the data extracted from the db
logger.info('Writing data to file...')
output = open(os.path.join(pathWorkDir, plkDqmFile), 'wb')
pickle.dump(dqmData, output)
output.close()
logger = logging.getLogger('full')
logger.info('Written ' + os.path.join(pathWorkDir, plkDqmFile))

cur.close()
db.close()
logger.info('Finished')
