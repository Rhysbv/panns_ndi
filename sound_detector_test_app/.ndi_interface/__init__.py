import NDIlib as ndi
#import logging

# Set up logging
#logging.basicConfig(filename='ndi_log.txt', level=logging.DEBUG, format='%(asctime)s - %(levelname)s - %(message)s')

# Initialise NDI
if not ndi.initialize():
    #logging.error('Cannot Initalise NDI!!')
    raise RuntimeError('Cannot Initalise NDI!!')
#logging.info("NDI Initalised")