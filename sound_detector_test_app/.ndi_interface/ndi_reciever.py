import NDIlib as ndi
#import logging
from collections import deque
import threading

class NDIReceiver:

    def __init__(self, ndi_source: ndi.Source, name: str = "NDI SED Receiver") -> None:
        self.audio_buffer = deque(maxlen=64) # Ring buffer that is 64 frames long
        self.video_buffer = deque(maxlen=64) # Ring buffer that is 64 frames long
        self.metadata_buffer = deque(maxlen=64) # Ring buffer that is 64 frames long
        self.audio_thread = threading.Thread(target=self._recieve)
        self.is_running = threading.Event()

        #Create a NDI Receiver
        recv_create_desc = ndi.RecvCreateV3()
        recv_create_desc.source_to_connect_to = ndi_source
        recv_create_desc.ndi_recv_name = name

        self.ndi_recv = ndi.recv_create_v3(recv_create_desc)
        #logging.debug("Reciever Created")

        if self.ndi_recv is None:
        #    logging.error('Cannot Create NDI Receiver!!')
            raise RuntimeError('Cannot Create NDI Receiver!!')

    def cleanup(self) -> None:
        #Free NDI memory
        ndi.recv_destroy(self.ndi_recv)
        #logging.debug('NDI Receiver Destroyed')

    def _recieve(self) -> None:
        while self.is_running.is_set():
            try:
                (t, v, a, m) = ndi.recv_capture_v2(self.ndi_recv, 1000)
        #        logging.debug(f"frame: {t}")
                if t == ndi.FRAME_TYPE_AUDIO:
        #            logging.debug(f"Audio Frame Received (Sample Rate: {a.sample_rate}, No. Channels: {a.no_channels}, No. Samples: {a.no_samples})")
        #            logging.debug(f"Timecode: {a.timecode} Timestamp: {a.timestamp}")
        #            logging.debug(f"audio_buffer length: {len(self.audio_buffer)}")
                    self.audio_buffer.append(a)

                if t == ndi.FRAME_TYPE_VIDEO:
        #            logging.debug('Video Frame Received')
        #            logging.debug(f"xres: {v.xres} yres: {v.yres}")
                    self.video_buffer.append(v)

                if t == ndi.FRAME_TYPE_METADATA:
        #            logging.debug('Metadata Frame Received')
        #            logging.debug(f"Metadata: {m.data}")
                    self.metadata_buffer.append(m)

                if t == ndi.FRAME_TYPE_NONE:
        #            logging.debug('No data received.')
                    pass
            except Exception as e:
        #       logging.error(e)
                print(e)
                continue
            finally:
        #        logging.debug('Freeing resources.')
                ndi.recv_free_audio_v2(self.ndi_recv, a)
                ndi.recv_free_video_v2(self.ndi_recv, v)
                ndi.recv_free_metadata(self.ndi_recv, m)

    def start(self) -> None:
        self.is_running.set()
        self.audio_thread.start()

    def stop(self) -> None:
        self.is_running.clear()
        self.audio_thread.join()
        
    def pop_audio_buffer(self) -> ndi.AudioFrameV2:
        if self.audio_buffer:
            return self.audio_buffer.popleft()
        #logging.debug("No audio data in buffer!!!")
        return None
    
    def pop_video_buffer(self) -> ndi.VideoFrameV2:
        if self.video_buffer:
            return self.video_buffer.popleft()
        #logging.debug("No video data in buffer!!!")
        return None
    
    def pop_metadata_buffer(self) -> ndi.MetadataFrame:
        if self.metadata_buffer:
            return self.metadata_buffer.popleft()
        #logging.debug("No metadata in buffer!!!")
        return None
    
    def get_audio_buffer(self) -> ndi.AudioFrameV2:
        return self.audio_buffer

