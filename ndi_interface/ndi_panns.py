from ndi_interface import ndi_reciever, ndi_transmitter, ndi_finder, ndi_utils, ndi
from panns_inference import AudioTagging, labels
import threading
import numpy as np
import librosa
import xml.etree.ElementTree as ET
import time
import logging
import faulthandler

faulthandler.enable()

class RingBuffer():
    """
    A 1D ring buffer using numpy arrays, designed to efficiently handle
    real-time audio buffering. Modified from
    https://scimusing.wordpress.com/2013/10/25/ring-buffers-in-pythonnumpy/
    """
    def __init__(self, length, dtype=np.float32):
        """
        :param int length: Number of samples in this buffer
        """

        self._length = length
        self._buf = np.zeros(length, dtype=dtype)
        self._bufrange = np.arange(length)
        self._idx = 0  # the oldest location

    def update(self, arr):
        """
        Adds 1D array to ring buffer. Note that ``len(arr)`` must be anything
        smaller than ``self.length``, otherwise it will error.
        """
        len_arr = len(arr)
        assert len_arr < self._length, "RingBuffer too small for this update!"
        idxs = (self._idx + self._bufrange[:len_arr]) % self._length
        self._buf[idxs] = arr
        self._idx = idxs[-1] + 1  # this will be the new oldest location

    def read(self):
        """
        Returns a copy of the whole ring buffer, unwrapped in a way that the
        first element is the oldest, and the last is the newest.
        """
        idxs = (self._idx + self._bufrange) % self._length  # read from oldest
        result = self._buf[idxs]
        return result

class NDIPanns:
    def __init__(self, ndi_source: ndi.Source, name: str = "NDI PANNS") -> None:
        self.receiver = ndi_reciever.NDIReceiver(ndi_source)
        self.transmitter = ndi_transmitter.NDITransmitter(name)
        self.audio_buffer = RingBuffer(47*1024) #  samples

        self.panns_thread = threading.Thread(target=self._panns_handler) # Thread to handle the PANNS
        self.ndi_to_fp_thread = threading.Thread(target=self._ndi_to_fp_handler) # Thread to handle the NDI data
        self.is_running = threading.Event()
        
        self.xml_metadata = None
        self.predicted_sound = None

    def start(self):
        self.receiver.start()
        self.transmitter.start()
        self.is_running.set()
        self.ndi_to_fp_thread.start()
        self.panns_thread.start()

    def stop(self):
        self.receiver.stop()
        self.transmitter.stop()
        self.is_running.clear()
        self.ndi_to_fp_thread.join()
        self.panns_thread.join()

    def _ndi_to_fp_handler(self):
        while self.is_running.is_set():
            audio_frame = self.receiver.pop_audio_buffer()
            video_frame = self.receiver.pop_video_buffer()
            metadata = self.receiver.pop_metadata_buffer()
            
            if video_frame is not None:
                # Do something with the video frame
                self.transmitter.append_video(video_frame)
            if metadata is not None:
                # Do something with the metadata
                self.transmitter.append_meta(metadata)
            elif self.xml_metadata is not None:
                pass
            if audio_frame is not None:
                # Do something with the audio frame
                self.transmitter.append_audio(audio_frame)
                try:
                    fp_data = audio_frame.data
                    fp_data = librosa.to_mono(fp_data)
                    self.audio_buffer.update(fp_data)
                except Exception as e:
                    print(e)
                    continue                

    def _panns_handler(self):
        delay = 1.37
        time_to_wait = time.time() + delay
        at = AudioTagging(checkpoint_path=None, device='cuda')
        while self.is_running.is_set():
            #Wait until new data in buffer
            time.sleep(max(0, time_to_wait - time.time()))

            #read buffer
            buffer = self.audio_buffer.read()
            buffer = buffer[None, :]

            #Run PANNS
            (clipwise_output, embedding) = at.inference(buffer)
            
            #Get the predicted sound
            sorted_output = np.argsort(clipwise_output[0])[::-1]
            predicted_sound = labels[sorted_output[0]]
            self.predicted_sound = predicted_sound

            #Build metadata
            self.xml_metadata = self._build_meta_frame(predicted_sound)
            metadata = ndi_utils.MetadataFrame(data = self.xml_metadata, length = len(self.xml_metadata))
            self.transmitter.append_meta(metadata)
            print(f"Predicted Sound: {predicted_sound}")

            #Update time to wait
            time_to_wait += (time.time() - time_to_wait) // delay * delay + delay

    def _build_meta_frame(self, predicted_sound: str):
        ET.register_namespace('sed', "https://www.surrey.ac.uk")
        root = ET.Element("{https://www.surrey.ac.uk}root")

        prediction = ET.SubElement(root, "{https://www.surrey.ac.uk}prediction")
        
        prediction.text = predicted_sound

        return ET.tostring(root, encoding='utf8', method='xml')

    def cleanup(self):
        self.receiver.cleanup()
        self.transmitter.cleanup()

    def get_prediction(self):
        return self.predicted_sound
        

if __name__ == "__main__":
    finder = ndi_finder.NDIFinder()
    sources = finder.get_ndi_sources()
    print(f"NDI Sources: {[source.ndi_name for source in sources]}")
    test_panns = NDIPanns(sources[0])
    test_panns.start()
    
    while True:
        if input("Press 'q' to quit: ") == 'q':
            test_panns.stop()
            test_panns.cleanup()
            finder.cleanup()
            break
