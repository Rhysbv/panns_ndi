from ndi_interface import ndi_finder, ndi_reciever, ndi_transmitter
import xml.etree.ElementTree as ET
import time
import ffmpeg
import threading
import numpy as np

class NDISEDExtractor:

    def __init__(self, source) -> None:
        ET.register_namespace('sed', "https://www.surrey.ac.uk")
        self.reciever = ndi_reciever.NDIReceiver(source)
        self.transmitter = ndi_transmitter.NDITransmitter("SED Icon Injector")
        self.transmit_thread = threading.Thread(target=self._transmit)
        self.is_running = threading.Event()
        self.predicted_sound = ""
        
    def extract_metadata(self, metadata) -> str:
        try:
            xml_tree = ET.fromstring(metadata.data)
            return xml_tree.find("sed:prediction", namespaces={"sed": "https://www.surrey.ac.uk"}).text
        except Exception as e:
            print(e)
 #           logging.error(e)
            return ""
            
    def _transmit(self):
        while self.is_running.is_set():
            audio_frame = self.reciever.pop_audio_buffer()
            video_frame = self.reciever.pop_video_buffer()
            metadata = self.reciever.pop_metadata_buffer()
            if video_frame is not None:
                new_frame_data = self.numpy_array_to_video(video_frame)
                video_frame.data = new_frame_data            
                self.transmitter.append_video(video_frame)
  #              logging.debug("Transmitting video frame")
            if metadata is not None:
                self.transmitter.append_meta(metadata)
                self.predicted_sound = self.extract_metadata(metadata)
                print("Transmitting metadata with sound prediction: " + self.predicted_sound)
            if audio_frame is not None:
                self.transmitter.append_audio(audio_frame)

    def numpy_array_to_video(self, video_frame):
        video_data = video_frame.data
        fps = round(video_frame.frame_rate_N / video_frame.frame_rate_D,2)
        process = (
            ffmpeg
            .input('pipe:', format='rawvideo', pix_fmt='uyvy422', s=f'{video_frame.xres}x{video_frame.yres}', r=fps)
            .drawtext(text=self.predicted_sound, x=10, y=10, fontsize=20, fontcolor='red')
            .output('pipe:', format='rawvideo', pix_fmt='uyvy422')
            .run_async(pipe_stdin=True, pipe_stdout=True)
        )
        out, _ = process.communicate(input=video_data.astype(np.uint8).tobytes())
        return np.frombuffer(out, np.uint8).reshape([-1, video_frame.xres, video_frame.yres, 2])

    def start(self) -> None:
        self.reciever.start()
        self.transmitter.start()
        self.is_running.set()
        self.transmit_thread.start()
        

    def stop(self) -> None:
        self.reciever.stop()
        self.transmitter.stop()
        self.is_running.clear()
        self.transmit_thread.join()

    def cleanup(self) -> None:
        self.reciever.cleanup()
        self.transmitter.cleanup()

    def get_prediction(self):
        return self.predicted_sound

if __name__ == '__main__':
    finder = ndi_finder.NDIFinder()
    
    found = False
    while not found:
        sources = finder.get_ndi_sources()
        for i in sources:
            print(i.ndi_name)
            if "PANN" in i.ndi_name:
                print("Found PANNS module")
                extractor = NDISEDExtractor(i)
                found = True
                break
    
    extractor.start()

        
        
