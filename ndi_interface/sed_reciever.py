from ndi_interface import ndi_reciever, ndi_finder
import xml.etree.ElementTree as ET

if __name__ == '__main__':
    finder = ndi_finder.NDIFinder()
    sources = finder.get_ndi_sources()
    receiver = None
    print(sources)
    for i in sources:
        print(i.ndi_name)
        if i.ndi_name == 'RHYS-LAPTOP (NDI PANNS)':
            receiver = ndi_reciever.NDIReceiver(i)
            break

    if receiver is None:
        print('Receiver not found')
        exit()
    receiver.start()

    while True:
        if input("Press 'q' to quit: ") == 'q':
            receiver.stop()
            receiver.cleanup()
            finder.cleanup()
        metadata = receiver.pop_metadata_buffer()
        if metadata:
            try:
                print(metadata.length)
                print(metadata.timecode)
                print(metadata.data)
            except Exception as e:
                print(e)
                continue
        #print(receiver.pop_metadata_buffer().data)

