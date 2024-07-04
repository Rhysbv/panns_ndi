from dataclasses import dataclass
import numpy as np
import NDIlib as ndi

@dataclass
class AudioFrame:
    data: np.ndarray
    timestamp: float
    timecode: int = 0
    channels: int = 1
    sample_rate: int = 48000
    no_of_samples: int = 1024
    FourCC: ndi.FourCCAudioType = ndi.FOURCC_AUDIO_TYPE_FLTP

@dataclass
class VideoFrame:
    data: np.ndarray
    timestamp: float
    FourCC: ndi.FourCCVideoType = ndi.FOURCC_VIDEO_TYPE_BGRX
    frame_rate_N: int = 30000
    frame_rate_D: int = 1001
    picture_aspect_ratio: float = 16.0/9.0
    frame_format_type: ndi.FrameFormatType = ndi.FRAME_FORMAT_TYPE_PROGRESSIVE
    line_stride_in_bytes: int = 1920*4
    timecode: int = 0
    xres: int = 1920
    yres: int = 1080

@dataclass
class MetadataFrame:
    data: str
    length: int = 0
    timecode: int = 0
