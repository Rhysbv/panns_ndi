import NDIlib as ndi
import logging
from collections import deque
import threading
import numpy as np
from .ndi_utils import AudioFrame, VideoFrame, MetadataFrame

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
        logging.debug("Reciever Created")

        if self.ndi_recv is None:
            logging.error('Cannot Create NDI Receiver!!')
            raise RuntimeError('Cannot Create NDI Receiver!!')

    def cleanup(self) -> None:
        #Free NDI memory
        ndi.recv_destroy(self.ndi_recv)
        logging.debug('NDI Receiver Destroyed')

    def _recieve(self) -> None:
        while self.is_running.is_set():
            try:
                (t, v, a, m) = ndi.recv_capture_v2(self.ndi_recv, 1000)
                
                if t == ndi.FRAME_TYPE_VIDEO:
                    #logging.debug('Video Frame Received')
                    #logging.debug(f"xres: {v.xres} yres: {v.yres}")
                    
                    py_video_frame = VideoFrame(data=v.data, timestamp=v.timestamp, FourCC=v.FourCC, frame_rate_N=v.frame_rate_N, frame_rate_D=v.frame_rate_D, picture_aspect_ratio=v.picture_aspect_ratio, frame_format_type=v.frame_format_type, line_stride_in_bytes=v.line_stride_in_bytes, timecode=v.timecode, xres=v.xres, yres=v.yres)
                    self.video_buffer.append(py_video_frame)
                
                if t == ndi.FRAME_TYPE_AUDIO:
                    #logging.debug(f"Audio Frame Received (Sample Rate: {a.sample_rate}, No. Channels: {a.no_channels}, No. Samples: {a.no_samples})")
                    #logging.debug(f"Timecode: {a.timecode} Timestamp: {a.timestamp}")
                    #logging.debug(f"audio_buffer length: {len(self.audio_buffer)}")
                    py_audio_frame = AudioFrame(data=a.data, timestamp=a.timestamp, timecode=a.timecode, channels=a.no_channels, sample_rate=a.sample_rate, no_of_samples=a.no_samples)
                    self.audio_buffer.append(py_audio_frame)

                if t == ndi.FRAME_TYPE_METADATA:
                    #logging.debug('Metadata Frame Received')
                    #logging.debug(f"Metadata: {m.data}")
                    py_metadata_frame = MetadataFrame(data=m.data, length=m.length, timecode=m.timecode)
                    self.metadata_buffer.append(py_metadata_frame)

                if t == ndi.FRAME_TYPE_NONE:
                    pass
                    #logging.debug('No data received.')
            except Exception as e:
                #logging.error(e)
                print(f"ERROR recieving {t}: {e}")
                continue
            finally:
                
                #logging.debug('Freeing resources.')
                #This is fucked should be freed after poped and used which is sad as not in this class :(
                #maybe add a free_X_frame functon but also kinda defeats alot of the point of the module
                ndi.recv_free_audio_v2(self.ndi_recv, a)
                ndi.recv_free_video_v2(self.ndi_recv, v)
                ndi.recv_free_metadata(self.ndi_recv, m)

    def start(self) -> None:
        self.is_running.set()
        self.audio_thread.start()

    def stop(self) -> None:
        self.is_running.clear()
        self.audio_thread.join()
        
    def pop_audio_buffer(self):
        if self.audio_buffer:
            audio_frame = self.audio_buffer.popleft()
            return audio_frame
        logging.debug("No audio data in buffer!!!")
        return None
    
    def pop_video_buffer(self):
        if self.video_buffer:
            video_frame = self.video_buffer.popleft()
            return video_frame
        logging.debug("No video data in buffer!!!")
        return None
    
    def pop_metadata_buffer(self):
        if self.metadata_buffer:
            meta_frame = self.metadata_buffer.popleft()
            return meta_frame
        logging.debug("No metadata in buffer!!!")
        return None
    
    def get_audio_buffer(self):
        return self.audio_buffer

