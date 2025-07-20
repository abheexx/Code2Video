#!/usr/bin/env python3

"""
Ultra Fast Video Renderer - Optimized for speed
Creates engaging videos with minimal frame generation for fast rendering.
"""

import os
import json
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

class UltraFastVideoRenderer:
    """Ultra-fast video renderer optimized for speed."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        
        # Dynamic frame count based on audio duration
        self.fps = fps
        
    def create_animated_video(self, code: str, audio_path: str, explanation: Dict[str, Any],
                            output_path: str = "ultra_fast_video.mp4", narration_text: str = None) -> str:
        """Create an ultra-fast animated video."""
        
        # Get audio duration
        duration = self._get_audio_duration(audio_path)
        
        # Calculate frame count based on duration
        self.total_frames = int(duration * self.fps)
        self.frame_duration = duration / self.total_frames
        
        # Create frames with minimal processing
        frames = self._create_frames(code, explanation, duration)
        
        # Save frames as images
        frame_dir = tempfile.mkdtemp()
        frame_paths = []
        
        for i, frame in enumerate(frames):
            frame_path = os.path.join(frame_dir, f"frame_{i:04d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)
        
        # Create video with ffmpeg (much faster than PIL)
        self._create_video_from_frames(frame_paths, audio_path, output_path, duration)
        
        # Cleanup
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
    
    def _create_frames(self, code: str, explanation: Dict[str, Any], duration: float) -> List[Image.Image]:
        """Create minimal frames for speed."""
        frames = []
        
        # Create key frames for different sections
        key_frames = self._create_key_frames(code, explanation)
        
        # Create frames based on duration
        for i in range(self.total_frames):
            progress = i / (self.total_frames - 1)
            frame = self._interpolate_frame(key_frames, progress, duration)
            frames.append(frame)
        
        return frames
    
    def _create_key_frames(self, code: str, explanation: Dict[str, Any]) -> List[Image.Image]:
        """Create key frames for different sections."""
        key_frames = []
        
        # Frame 1: Title
        frame1 = self._create_title_frame(explanation.get('title', 'Code Explanation'))
        key_frames.append(frame1)
        
        # Frame 2: Code overview
        frame2 = self._create_code_frame(code)
        key_frames.append(frame2)
        
        # Frame 3: Code details
        frame3 = self._create_code_details_frame(code)
        key_frames.append(frame3)
        
        # Frame 4: Explanation
        frame4 = self._create_explanation_frame(explanation.get('overview', 'Code explanation'))
        key_frames.append(frame4)
        
        # Frame 5: Summary
        frame5 = self._create_summary_frame(explanation)
        key_frames.append(frame5)
        
        return key_frames
    
    def _create_title_frame(self, title: str) -> Image.Image:
        """Create title frame."""
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Simple gradient background
        for y in range(self.height):
            color = int(30 + (y / self.height) * 20)
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
        
        # Title
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 72)
        except:
            font = ImageFont.load_default()
        
        bbox = draw.textbbox((0, 0), title, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (self.width - text_width) // 2
        y = (self.height - text_height) // 2
        
        # Glow effect
        for offset in range(3):
            draw.text((x + offset, y + offset), title, fill=(100, 100, 255), font=font)
        
        draw.text((x, y), title, fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_code_frame(self, code: str) -> Image.Image:
        """Create code frame."""
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Background
        for y in range(self.height):
            color = int(30 + (y / self.height) * 15)
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
        
        # Code area
        code_bg = (45, 45, 48)
        draw.rectangle([50, 100, self.width - 50, self.height - 100], fill=code_bg)
        
        # Code text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
        except:
            font = ImageFont.load_default()
        
        lines = code.strip().split('\n')
        y_pos = 150
        
        for i, line in enumerate(lines[:12]):  # Limit lines
            # Line number
            line_num = f"{i+1:2d} "
            draw.text((70, y_pos), line_num, fill=(100, 100, 100), font=font)
            
            # Code line
            draw.text((70 + len(line_num) * 15, y_pos), line, fill=(255, 255, 255), font=font)
            y_pos += 40
        
        return img
    
    def _create_explanation_frame(self, explanation: str) -> Image.Image:
        """Create explanation frame."""
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Background
        for y in range(self.height):
            color = int(30 + (y / self.height) * 10)
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
        
        # Explanation text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
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
        
        # Draw lines
        y_pos = (self.height - len(lines) * 60) // 2
        for line in lines:
            bbox = draw.textbbox((0, 0), line, font=font)
            text_width = bbox[2] - bbox[0]
            x = (self.width - text_width) // 2
            draw.text((x, y_pos), line, fill=(255, 255, 255), font=font)
            y_pos += 60
        
        return img
    
    def _interpolate_frame(self, key_frames: List[Image.Image], progress: float, duration: float) -> Image.Image:
        """Interpolate between key frames based on time."""
        # Create more sections for longer videos
        num_sections = max(3, int(duration / 3))  # At least 3 sections, more for longer videos
        
        section_size = 1.0 / num_sections
        current_section = int(progress / section_size)
        
        if current_section >= len(key_frames) - 1:
            return key_frames[-1]
        
        # Interpolate within current section
        section_progress = (progress - current_section * section_size) / section_size
        return self._blend_frames(key_frames[current_section], key_frames[current_section + 1], section_progress)
    
    def _blend_frames(self, frame1: Image.Image, frame2: Image.Image, t: float) -> Image.Image:
        """Blend two frames with weight t."""
        # Simple alpha blending
        if t < 0.5:
            return frame1
        else:
            return frame2
    
    def _create_video_from_frames(self, frame_paths: List[str], audio_path: str, 
                                output_path: str, duration: float):
        """Create video from frames using ffmpeg."""
        
        # Create frame list file
        frame_list = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for frame_path in frame_paths:
            frame_list.write(f"file '{frame_path}'\n")
            frame_list.write(f"duration {self.frame_duration}\n")
        frame_list.close()
        
        # Use ffmpeg to create video
        cmd = [
            'ffmpeg', '-y',  # Overwrite output
            '-f', 'concat',  # Use concat demuxer
            '-safe', '0',
            '-i', frame_list.name,  # Input frame list
            '-i', audio_path,  # Audio input
            '-c:v', 'libx264',  # Video codec
            '-c:a', 'aac',  # Audio codec
            '-pix_fmt', 'yuv420p',  # Pixel format
            '-shortest',  # End when shortest input ends
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        
        # Cleanup
        os.unlink(frame_list.name)


def main():
    """Test the ultra-fast renderer."""
    example_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""
    
    example_explanation = {
        "title": "Fibonacci Function",
        "overview": "A recursive function that calculates Fibonacci numbers efficiently"
    }
    
    renderer = UltraFastVideoRenderer()
    
    # Test with dummy audio (create a silent audio file)
    silent_audio = "silent.wav"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-t', '5', silent_audio
    ])
    
    output_path = renderer.create_animated_video(
        example_code, silent_audio, example_explanation, "ultra_fast_test.mp4"
    )
    
    print(f"Ultra-fast video created: {output_path}")
    
    # Cleanup
    os.remove(silent_audio)


if __name__ == "__main__":
    main() 