#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
Created on Fri May 18 17:16:15 2018

@author: kgross

Modified: Saturday Fri Feb 15

@author: tere93
"""

from eye_tracking.preprocessing.functions.et_import import import_pl
from eye_tracking.preprocessing.functions.detect_events import make_blinks, make_saccades, make_fixations
from eye_tracking.preprocessing.functions.detect_bad_samples import detect_bad_samples, remove_bad_samples
from eye_tracking.preprocessing.functions.et_helper import add_events_to_samples
from eye_tracking.preprocessing.functions.et_helper import load_file, save_file
from eye_tracking.preprocessing.functions.et_make_df import make_events_df

import logging


# %%

def preprocess_et(subject, datapath='/media/whitney/New Volume/Teresa/bdd-driveratt', load=False, save=False,
                  eventfunctions=(make_blinks, make_saccades, make_fixations), outputprefix='', **kwargs):
    # Output:     3 cleaned dfs: etsamples, etmsgs, etevents   
    # get a logger for the preprocess function    
    logger = logging.getLogger(__name__)

    # load already calculated df
    if load:
        logger.info('Loading et data from file ...')
        try:
            etsamples, etmsgs, etevents = load_file(subject, datapath, outputprefix=outputprefix)
            return etsamples, etmsgs, etevents
        except:
            logger.warning('Error: Could not read file')

    # import pl data
    logger.debug("Importing et data")
    logger.debug('Caution: etevents might be empty')
    etsamples, etmsgs, etevents = import_pl(subject=subject, datapath=datapath, surfaceMap=False, parsemsg=False, **kwargs)

    # Mark bad samples
    logger.debug('Marking bad et samples')
    etsamples = detect_bad_samples(etsamples)

    # etsamples = etsamples[20:]
    # # Remove samples with low confidence
    # ix_low_confidence = (etsamples.confidence < 0.70)
    # etsamples['low_conf'] = ix_low_confidence
    # etsamples = etsamples[etsamples['low_conf'] == False]

    # Detect events
    # by our default first blinks, then saccades, then fixations
    logger.debug('Making event df')
    for evtfunc in eventfunctions:
        logger.debug('Events: calling %s', evtfunc.__name__)
        etsamples, etevents = evtfunc(etsamples, etevents)

    # Make a nice etevent df
    etevents = make_events_df(etevents)

    # Each sample has a column 'type' (blink, saccade, fixation)
    # which is set according to the event df
    logger.debug('Add events to each sample')
    etsamples = add_events_to_samples(etsamples, etevents)

    # Samples get removed from the samples df
    # because of outside monitor, pupilarea Nan, negative sample time
    logger.info('Removing bad samples')
    cleaned_etsamples = remove_bad_samples(etsamples)

    # in case you want to save the calculated results
    if save:
        logger.info('Saving preprocessed et data')
        save_file([etsamples, cleaned_etsamples, etmsgs, etevents], subject, datapath, outputprefix=outputprefix)

    return cleaned_etsamples, etmsgs, etevents