import os
import subprocess
import json
from tqdm import tqdm
import re


class VideoProcessor:
    def __init__(self):
        self.ffmpeg = 'ffmpeg'
        self.ffprobe = 'ffprobe'

    def get_video_info(self, video_path):
        if not os.path.exists(video_path):
            raise FileNotFoundError(f"Video file not found: {video_path}")

        cmd = [
            self.ffprobe,
            '-v', 'error',
            '-select_streams', 'v:0',
            '-show_entries', 'stream=height,bit_rate',
            '-show_entries', 'format=duration,bit_rate',
            '-of', 'json',
            video_path
        ]

        try:
            result = json.loads(subprocess.check_output(cmd).decode())

            height = int(result['streams'][0]['height'])
            duration = float(result['format']['duration'])

            try:
                bitrate = int(result['streams'][0]['bit_rate'])
            except (KeyError, TypeError, ValueError):
                try:
                    bitrate = int(result['format']['bit_rate'])
                except (KeyError, TypeError, ValueError):
                    # Estimate bitrate from file size if not available
                    filesize = os.path.getsize(video_path)
                    bitrate = int((filesize * 8) / float(duration))

            return {
                'height': height,
                'duration': duration,
                'bitrate': bitrate
            }
        except Exception as e:
            print(f"Error getting video info: {e}")
            raise

    def convert_video(self, input_path, output_path, callback=None):
        if not os.path.exists(input_path):
            raise FileNotFoundError(f"Input file not found: {input_path}")

        # Get video info
        info = self.get_video_info(input_path)
        target_bitrate = max(info['bitrate'] // 2, 1_000_000)  # Minimum 1Mbps
        bitrate = f"{target_bitrate // 1000}k"

        print("\nVideo conversion settings:")
        print(f"Original bitrate: {info['bitrate']//1000}k")
        print(f"Target bitrate: {bitrate}")

        encoder = 'libx265'
        preset = 'veryfast'

        cmd = [
            self.ffmpeg,
            '-i', input_path,
            '-c:v', encoder,
            '-preset', preset,
            '-b:v', bitrate,
            '-maxrate', f"{int(float(bitrate[:-1]) * 1.5)}k",
            '-bufsize', f"{int(float(bitrate[:-1]) * 2)}k",
            '-c:a', 'copy',
            output_path,
            '-y',
            '-progress', 'pipe:1',
            '-loglevel', 'warning'
        ]

        print("\nFFmpeg command:")
        print(' '.join(cmd))

        try:
            # Start conversion
            process = subprocess.Popen(cmd, stdout=subprocess.PIPE, stderr=subprocess.PIPE, universal_newlines=True)

            progress_bar = tqdm(total=100, desc="Converting", unit="%")
            pattern = re.compile(r"out_time=(\d{2}):(\d{2}):(\d{2})")
            last_progress = 0

            # Process output
            while True:
                stdout_line = process.stdout.readline()
                if not stdout_line and process.poll() is not None:
                    break

                if stdout_line:
                    match = pattern.search(stdout_line)
                    if match:
                        hours, minutes, seconds = map(int, match.groups())
                        time_done = hours * 3600 + minutes * 60 + seconds
                        progress = min(int(time_done / info['duration'] * 100), 100)
                        if progress > last_progress:
                            progress_bar.update(progress - last_progress)
                            last_progress = progress
                            if callback:
                                callback(progress)

            progress_bar.close()

            # Get final output and check for errors
            _, stderr = process.communicate()
            if stderr:
                print("\nFFmpeg output:")
                print(stderr)

            if process.returncode != 0:
                raise subprocess.CalledProcessError(process.returncode, cmd, stderr)

            # Verify output
            if not os.path.exists(output_path):
                raise Exception("Output file was not created")

            if os.path.getsize(output_path) == 0:
                raise Exception("Output file is empty")

            # Get compression results
            results = {
                'input_size': os.path.getsize(input_path),
                'output_size': os.path.getsize(output_path),
                'input_bitrate': info['bitrate'],
                'target_bitrate': target_bitrate
            }
            results['reduction'] = (1 - results['output_size'] / results['input_size']) * 100

            print("\nCompression results:")
            print(f"Original size: {results['input_size']/1024/1024:.2f}MB")
            print(f"Final size: {results['output_size']/1024/1024:.2f}MB")
            print(f"Size reduction: {results['reduction']:.1f}%")

            return results

        except Exception as e:
            print(f"\nError during conversion: {str(e)}")
            if process and process.poll() is not None:
                process.terminate()
            raise
