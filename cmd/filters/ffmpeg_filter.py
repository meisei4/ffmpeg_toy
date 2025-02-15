def create_gap_segment_filter(from_time: float, to_time: float, label: str) -> str:
    """
    Creates a no-effect segment by trimming the input video from 'from_time'..'to_time',
    labeling it as '[label]'.
    """
    return f"[0:v]trim=start={from_time}:end={to_time},setpts=PTS-STARTPTS[{label}]"
