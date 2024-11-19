# getaudio.py
import subprocess
import re

def get_audio_streams(video_file):
    """Get audio stream details from the video file."""
    # Run ffmpeg command to get the stream details of the video file
    command = ["ffmpeg", "-i", video_file]
    result = subprocess.run(command, stderr=subprocess.PIPE, text=True)
    
    # Get raw output of ffmpeg command
    ffmpeg_output = result.stderr
    
    # Find all audio streams using regex
    audio_streams = []
    for match in re.finditer(r"Stream #(\d+):(\d+)\((.*?)\): Audio: (\S+), (\d+) Hz, (\S+),", ffmpeg_output):
        stream_index = match.group(2)
        language = match.group(3)
        codec = match.group(4)
        sample_rate = match.group(5)
        channels = match.group(6)
        
        audio_streams.append({
            "index": stream_index,
            "language": language,
            "codec": codec,
            "sample_rate": sample_rate,
            "channels": channels
        })
    print(audio_streams)
    
    return audio_streams

def extract_audio(video_file, audio_streams):
    """Extract audio streams from video file and save them to MP3 files."""
    for stream in audio_streams:
        stream_index = stream["index"]
        language = stream["language"]
        stream_index = int(stream_index) - 1  # Adjust index for ffmpeg
        # Construct the output filename based on language or stream index
        output_filename = f"output_{language.lower()}.mp3" if language else f"output_{stream_index}.mp3"
        # Construct the ffmpeg command to extract audio
        command = [
            "ffmpeg", "-i", video_file, 
            "-map", f"0:a:{stream_index}", 
            "-c:a", "libmp3lame", 
            "-q:a", "2", 
            output_filename
        ]
        
        # Run the command to extract and save the audio
        subprocess.run(command)
        print(f"Extracted {language} audio to {output_filename}")
