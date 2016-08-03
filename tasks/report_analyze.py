# -*- coding: utf-8 -*-
"""
Created on Wed Jul 27 17:17:00 2016

@author: Fabrizio Coccetti (fabrizio.coccetti@centrofermi.it) [www.fc8.net]

Task to read the monitorData class and write the reportData class
"""

from e3monitor.db.E3Report import E3Report
import logging
from datetime import datetime
from e3monitor.tasks.update_time import (compute_update,
        day_of_run)
from e3monitor.tasks.set_version import set_version
from e3monitor.config.__limits__ import (
    TRANSFER_SEC_LIMIT,
    ELOG_WARNING,
    ELOG_ERROR,
    TRACKS_ERROR_HIGH,
    TRACKS_WARNING_HIGH,
    TRACKS_WARNING_LOW,
    TRACKS_ERROR_LOW
    )
from e3monitor.html.__html_headers__ import (
    HEADER_HTML,
    TABELLA1_HTML,
    TABELLA1_P2_HTML,
    FOOTER_HTML,
    BOTTOM_HTML
    )


def report_analyze(monitorData,
                   EEE_ACTIVE_STATIONS,
                   pklReportFile):
    '''Read the monitorData class and write the reportData class
    '''

    # Declare class to write all report data
    reportData = E3Report()

    # Start logger
    logger = logging.getLogger('plain')
    logger.info('Function report_analyze() started.')

    # Define now
    now = datetime.today()

    # Start loop for school names (sorted)
    for schoolName in sorted(monitorData.get_allData()):

        # Skip schools with no data
        if schoolName not in EEE_ACTIVE_STATIONS:
            continue

        # Initialize School List
        reportData.init_School(schoolName)
        logger.info('Generating report data for: ' + str(schoolName))

        ########################################
        # Section on file transfer delay at CNAF
        # Yellow after 3 hours
        # Red after 2 days
        ########################################

        reportData.set_transferDelayDays(
            schoolName, monitorData.get_transferDelayDays(schoolName))
        reportData.set_transferDelaySeconds(
            schoolName, monitorData.get_transferDelaySeconds(schoolName))
        reportData.set_transferTs(
            schoolName, monitorData.get_transferTs(schoolName))

        if monitorData.get_transferDelayDays(schoolName) == 0:
            if monitorData.get_transferDelaySeconds(schoolName) < TRANSFER_SEC_LIMIT:
                reportData.set_transferDelayStatus(schoolName, 0)
            else:
                reportData.set_transferDelayStatus(schoolName, 1)
        elif monitorData.get_transferDelayDays(schoolName) == 1:
            reportData.set_transferDelayStatus(schoolName, 1)
        else:
            reportData.set_transferDelayStatus(schoolName, 2)

        ################################################
        # Section on Elog
        ################################################
        try:
            reportData.set_elogEntryTs(
                schoolName, monitorData.get_elogEntryTs(schoolName))
            elogDelay = now - monitorData.get_elogEntryTs(schoolName)
            if elogDelay.days <= ELOG_WARNING:
                    reportData.set_elogEntryStatus(schoolName, 0)
            elif elogDelay.days <= ELOG_ERROR:
                    reportData.set_elogEntryStatus(schoolName, 1)
            else:
                    reportData.set_elogEntryStatus(schoolName, 2)
        except:
            reportData.set_elogEntryStatus(schoolName, 2)

        ################################################
        # Section on Trigger Rate
        ################################################
        try:
            reportData.get_triggerRate(
                schoolName, monitorData.get_triggerRate(schoolName))
            _triggers = round(monitorData.get_trackRate(schoolName))
            if (_triggers < TRACKS_ERROR_LOW):
                reportData.set_triggerStatus(schoolName, -2)
            elif (_triggers < TRACKS_WARNING_LOW):
                reportData.set_triggerStatus(schoolName, -1)
            elif (_triggers < TRACKS_WARNING_HIGH):
                reportData.set_triggerStatus(schoolName, 0)
            elif (_triggers < TRACKS_ERROR_HIGH):
                reportData.set_triggerStatus(schoolName, 1)
            else:
                reportData.set_triggerStatus(schoolName, 2)
        except:
            reportData.set_triggerStatus(schoolName, 3)

        ################################################
        # Final check
        ################################################
        print(reportData.get_schoolData(schoolName))

    # End
    logger.info('Function report_analyze() finished.')
    return True
