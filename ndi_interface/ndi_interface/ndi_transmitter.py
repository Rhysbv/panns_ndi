import NDIlib as ndi
from collections import deque
import threading

class NDITransmitter:

    def __init__(self, name: str = "NDI SED Transmitter") -> None:
        self.audio_buffer = deque(maxlen=64)
        self.video_buffer = deque(maxlen=64)
        self.meta_buffer = deque(maxlen=64)

        self.audio_thread = threading.Thread(target=self._send_audio)
        self.video_thread = threading.Thread(target=self._send_video)
        self.meta_thread = threading.Thread(target=self._send_meta)

        self.is_transmitting = threading.Event()
        
        send_create_desc = ndi.SendCreate()
        send_create_desc.ndi_name = name
        send_create_desc.clock_audio = True

        self.ndi_send = ndi.send_create(send_create_desc)

    def _send_audio(self) -> None:
        while self.is_transmitting.is_set():
            try:
                if self.audio_buffer:
                    audio_data = self.audio_buffer.popleft()
                    audio_frame = ndi.AudioFrameV2()
                    audio_frame.data = audio_data.data
                    audio_frame.sample_rate = audio_data.sample_rate
                    audio_frame.no_channels = audio_data.channels
                    audio_frame.no_samples = audio_data.no_of_samples
                    audio_frame.timecode = audio_data.timecode
                    audio_frame.timestamp = audio_data.timestamp
                    ndi.send_send_audio_v2(self.ndi_send, audio_frame)
            except Exception as e:
                print(f"Transmitter Error: {e}")
                continue

    def _send_video(self) -> None:
        while self.is_transmitting.is_set():
            try:
                if self.video_buffer:
                    video_data = self.video_buffer.popleft()
                    video_frame = ndi.VideoFrameV2()
                    video_frame.data = video_data.data
                    video_frame.FourCC = video_data.FourCC
                    video_frame.frame_rate_N = video_data.frame_rate_N
                    video_frame.frame_rate_D = video_data.frame_rate_D
                    video_frame.picture_aspect_ratio = video_data.picture_aspect_ratio
                    video_frame.frame_format_type = video_data.frame_format_type
                    video_frame.line_stride_in_bytes = video_data.line_stride_in_bytes
                    video_frame.timecode = video_data.timecode
                    video_frame.timestamp = video_data.timestamp
                    video_frame.xres = video_data.xres
                    video_frame.yres = video_data.yres 
                    ndi.send_send_video_v2(self.ndi_send, video_frame)

            except Exception as e:
                print(f"Transmitter Error: {e}")
                continue

    def _send_meta(self) -> None:
        while self.is_transmitting.is_set():
            try:
                if self.meta_buffer:
                    meta_data = self.meta_buffer.popleft()
                    meta_frame = ndi.MetadataFrame()
                    meta_frame.data = meta_data.data
                    meta_frame.length = meta_data.length
                    meta_frame.timecode = meta_data.timecode
                    ndi.send_send_metadata(self.ndi_send, meta_frame)

            except Exception as e:
                print(f"Transmitter Error: {e}")
                continue
    
    def start(self) -> None:
        self.is_transmitting.set()
        self.audio_thread.start()
        self.video_thread.start()
        self.meta_thread.start()

    def append_audio(self, audio_data) -> None:
        self.audio_buffer.append(audio_data)

    def append_video(self, video_data) -> None:
        self.video_buffer.append(video_data)

    def append_meta(self, meta_data) -> None:
        self.meta_buffer.append(meta_data)

    def stop(self) -> None:
        self.is_transmitting.clear()
        self.audio_thread.join()
        self.video_thread.join()
        self.meta_thread.join()

    def cleanup(self) -> None:
        ndi.send_destroy(self.ndi_send)