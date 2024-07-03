import NDIlib as ndi
#import logging
from collections import deque
import threading, time

class NDITransmitter:

    def __init__(self, name: str = "NDI SED Transmitter") -> None:
        self.audio_buffer = deque(maxlen=64)
        self.video_buffer = deque(maxlen=64)
        self.meta_buffer = deque(maxlen=64)
        self.audio_thread = threading.Thread(target=self._send)
        self.is_transmitting = threading.Event()
        
        send_create_desc = ndi.SendCreate()
        send_create_desc.ndi_name = name
        send_create_desc.clock_audio = True

        self.ndi_send = ndi.send_create(send_create_desc)

    def _send(self) -> None:
        while self.is_transmitting.is_set():
            try:
                time.sleep(0.01)
                if self.audio_buffer:
                    audio_data = self.audio_buffer.popleft()
                    ndi.send_send_audio_v2(self.ndi_send, audio_data)
                if self.video_buffer:
                    video_data = self.video_buffer.popleft()
                    ndi.send_send_video_v2(self.ndi_send, video_data)

                if self.meta_buffer:
                    meta_data = self.meta_buffer.popleft()
                    ndi.send_send_metadata(self.ndi_send, meta_data)

            except Exception as e:
                #logging.error(e)
                continue
    
    def start(self) -> None:
        self.is_transmitting.set()
        self.audio_thread.start()

    def append_audio(self, audio_data: ndi.AudioFrameV2) -> None:
        self.audio_buffer.append(audio_data)

    def append_video(self, video_data: ndi.VideoFrameV2) -> None:
        self.video_buffer.append(video_data)

    def append_meta(self, meta_data: ndi.MetadataFrame) -> None:
        self.meta_buffer.append(meta_data)

    def stop(self) -> None:
        self.is_transmitting.clear()
        self.audio_thread.join()

    def cleanup(self) -> None:
        ndi.send_destroy(self.ndi_send)