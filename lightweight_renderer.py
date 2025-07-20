"""
Lightweight Video Renderer - Memory efficient and fast
Creates engaging videos with minimal resource usage to prevent crashes.
"""

import os
import json
import subprocess
import tempfile
import math
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont

class LightweightVideoRenderer:
    """Lightweight video renderer optimized for memory efficiency."""
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 24):
        # Reduced resolution and FPS for memory efficiency
        self.width = width
        self.height = height
        self.fps = fps
        
        # Simple emojis for engagement
        self.emojis = ['💻', '⚡', '🚀', '✨', '🎯', '💡', '✅', '🎉']
        
    def create_animated_video(self, code: str, audio_path: str, explanation: Dict[str, Any],
                            output_path: str = "lightweight_video.mp4", narration_text: str = None) -> str:
        """Create a lightweight animated video."""
        
        # Get audio duration
        duration = self._get_audio_duration(audio_path)
        
        # Use very few frames for memory efficiency
        total_frames = min(60, int(duration * self.fps))  # Max 60 frames
        frame_duration = duration / total_frames
        
        # Create minimal frames
        frames = self._create_minimal_frames(code, explanation, total_frames, duration)
        
        # Save frames with compression
        frame_dir = tempfile.mkdtemp()
        frame_paths = []
        
        for i, frame in enumerate(frames):
            frame_path = os.path.join(frame_dir, f"frame_{i:03d}.jpg")  # Use JPG for smaller size
            frame.save(frame_path, 'JPEG', quality=70, optimize=True)  # Compress heavily
            frame_paths.append(frame_path)
        
        # Create video with ffmpeg
        self._create_video_from_frames(frame_paths, audio_path, output_path, duration, frame_duration)
        
        # Cleanup immediately
        for frame_path in frame_paths:
            os.remove(frame_path)
        os.rmdir(frame_dir)
        
        return output_path
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration using ffprobe."""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_path
            ], capture_output=True, text=True)
            return float(result.stdout.strip())
        except:
            return 10.0  # Default duration
    
    def _create_minimal_frames(self, code: str, explanation: Dict[str, Any], 
                             total_frames: int, duration: float) -> List[Image.Image]:
        """Create minimal frames with basic animations."""
        frames = []
        
        # Create only 4 key frames
        key_frames = self._create_key_frames(code, explanation)
        
        for i in range(total_frames):
            progress = i / (total_frames - 1)
            frame = self._interpolate_frame(key_frames, progress)
            frames.append(frame)
        
        return frames
    
    def _create_key_frames(self, code: str, explanation: Dict[str, Any]) -> List[Image.Image]:
        """Create 4 simple key frames."""
        key_frames = []
        
        # Frame 1: Title
        frame1 = self._create_title_frame(explanation.get('title', 'Code Explanation'))
        key_frames.append(frame1)
        
        # Frame 2: Code
        frame2 = self._create_code_frame(code)
        key_frames.append(frame2)
        
        # Frame 3: Explanation
        frame3 = self._create_explanation_frame(explanation.get('overview', 'Code explanation'))
        key_frames.append(frame3)
        
        # Frame 4: Summary
        frame4 = self._create_summary_frame(explanation)
        key_frames.append(frame4)
        
        return key_frames
    
    def _create_title_frame(self, title: str) -> Image.Image:
        """Create simple title frame."""
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Simple gradient
        for y in range(0, self.height, 2):  # Skip every other line for speed
            color = int(30 + (y / self.height) * 20)
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
        
        # Title with emoji
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        emoji = self.emojis[0]
        full_title = f"{emoji} {title} {emoji}"
        
        bbox = draw.textbbox((0, 0), full_title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        # Simple glow
        draw.text((x + 2, y + 2), full_title, fill=(100, 100, 255), font=font)
        draw.text((x, y), full_title, fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_code_frame(self, code: str) -> Image.Image:
        """Create simple code frame."""
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Simple background
        for y in range(0, self.height, 3):  # Skip lines for speed
            color = int(30 + (y / self.height) * 15)
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
        
        # Code area
        draw.rectangle([50, 100, self.width - 50, self.height - 100], 
                      fill=(45, 45, 48), outline=(80, 80, 80), width=2)
        
        # Code text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 24)
        except:
            font = ImageFont.load_default()
        
        lines = code.strip().split('\n')
        y_pos = 150
        
        for i, line in enumerate(lines[:10]):  # Limit lines
            # Line number with emoji
            line_num = f"{i+1:2d} "
            emoji = self.emojis[i % len(self.emojis)]
            
            draw.text((70, y_pos), line_num, fill=(100, 100, 100), font=font)
            draw.text((70 + len(line_num) * 12, y_pos), emoji, fill=(255, 200, 100), font=font)
            draw.text((70 + len(line_num) * 12 + 20, y_pos), line, fill=(255, 255, 255), font=font)
            
            y_pos += 35
        
        return img
    
    def _create_explanation_frame(self, explanation: str) -> Image.Image:
        """Create simple explanation frame."""
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Simple background
        for y in range(0, self.height, 3):
            color = int(30 + (y / self.height) * 10)
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
        
        # Explanation text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        except:
            font = ImageFont.load_default()
        
        # Simple text wrapping
        words = explanation.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < self.width - 200:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        
        if current_line:
            lines.append(current_line)
        
        # Draw lines with emojis
        y_pos = (self.height - len(lines) * 50) // 2
        for i, line in enumerate(lines[:4]):  # Limit lines
            emoji = self.emojis[i % len(self.emojis)]
            line_with_emoji = f"{emoji} {line}"
            
            bbox = draw.textbbox((0, 0), line_with_emoji, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_pos), line_with_emoji, fill=(255, 255, 255), font=font)
            y_pos += 50
        
        return img
    
    def _create_summary_frame(self, explanation: Dict[str, Any]) -> Image.Image:
        """Create simple summary frame."""
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Simple background
        for y in range(0, self.height, 3):
            color = int(30 + (y / self.height) * 10)
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
        
        # Summary text
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 28)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Title
        title = "Success!"
        emoji = "✅"
        full_title = f"{emoji} {title} {emoji}"
        
        bbox = draw.textbbox((0, 0), full_title, font=font_large)
        title_width = bbox[2] - bbox[0]
        title_x = (self.width - title_width) // 2
        draw.text((title_x, 150), full_title, fill=(100, 255, 100), font=font_large)
        
        # Key takeaways
        takeaways = explanation.get('key_takeaways', ['Code explanation completed!'])
        y_pos = 250
        
        for i, takeaway in enumerate(takeaways[:2]):  # Limit takeaways
            emoji = self.emojis[i % len(self.emojis)]
            takeaway_with_emoji = f"{emoji} {takeaway}"
            
            bbox = draw.textbbox((0, 0), takeaway_with_emoji, font=font_small)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_pos), takeaway_with_emoji, fill=(200, 255, 200), font=font_small)
            y_pos += 60
        
        return img
    
    def _interpolate_frame(self, key_frames: List[Image.Image], progress: float) -> Image.Image:
        """Simple frame interpolation."""
        if progress <= 0.25:
            return key_frames[0]
        elif progress <= 0.5:
            return key_frames[1]
        elif progress <= 0.75:
            return key_frames[2]
        else:
            return key_frames[3]
    
    def _create_video_from_frames(self, frame_paths: List[str], audio_path: str, 
                                output_path: str, duration: float, frame_duration: float):
        """Create video from frames using ffmpeg with compression."""
        
        # Create frame list file
        frame_list = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for frame_path in frame_paths:
            frame_list.write(f"file '{frame_path}'\n")
            frame_list.write(f"duration {frame_duration}\n")
        frame_list.close()
        
        # Use ffmpeg with high compression
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-f', 'concat',  # Use concat demuxer
            '-safe', '0',
            '-i', frame_list.name,  # Input frame list
            '-i', audio_path,  # Audio input
            '-c:v', 'libx264',  # Video codec
            '-preset', 'ultrafast',  # Fast encoding
            '-crf', '28',  # High compression
            '-c:a', 'aac',  # Audio codec
            '-b:a', '128k',  # Low audio bitrate
            '-pix_fmt', 'yuv420p',  # Pixel format
            '-shortest',  # End when shortest input ends
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        
        # Cleanup
        os.unlink(frame_list.name)


def main():
    """Test the lightweight renderer."""
    example_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""
    
    example_explanation = {
        "title": "Fibonacci Function",
        "overview": "A recursive function that calculates Fibonacci numbers efficiently",
        "key_takeaways": ["Recursion is powerful", "Base cases are important"]
    }
    
    renderer = LightweightVideoRenderer()
    
    # Test with dummy audio
    silent_audio = "silent.wav"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-t', '5', silent_audio
    ])
    
    output_path = renderer.create_animated_video(
        example_code, silent_audio, example_explanation, "lightweight_test.mp4"
    )
    
    print(f"Lightweight video created: {output_path}")
    
    # Cleanup
    os.remove(silent_audio)


if __name__ == "__main__":
    main() 