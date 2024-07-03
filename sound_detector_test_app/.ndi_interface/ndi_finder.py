import NDIlib as ndi
#import logging

class NDIFinder:

    def __init__(self) -> None:
        self.ndi_find = ndi.find_create_v2()
        if self.ndi_find is None:
        #    logging.error('Cannot Create NDI Finder!!')
            raise RuntimeError('Cannot Create NDI Finder!!')

    def get_ndi_sources(self) -> list[ndi.Source]:
        '''
        Returns a list of NDI sources available on the local network
        '''
        #Locate NDI Source
        sources = []
        while len(sources) < 1:
            ndi.find_wait_for_sources(self.ndi_find, 1000)
            sources = ndi.find_get_current_sources(self.ndi_find)
        #logging.debug(f"NDI Sources: {[source.ndi_name for source in sources]}")

        return sources

    def cleanup(self) -> None:
        ndi.find_destroy(self.ndi_find)
        #logging.debug('NDI Finder destroyed')        

if __name__ == "__main__":
    t = NDIFinder()
    s = t.get_ndi_sources()
    print(s)
    print(s[0].ndi_name)

    t.cleanup()