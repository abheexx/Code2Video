#!/usr/bin/env python3

"""
Animated Video Renderer for Code2Vid
Creates animated videos with moving elements using PIL and ffmpeg.
"""

import os
import json
import math
import numpy as np
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import tempfile
import re
import subprocess

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class AnimatedVideoRenderer:
    """Creates animated videos with moving elements and code highlighting."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        """
        Initialize the animated video renderer.
        
        Args:
            width: Video width in pixels
            height: Video height in pixels
            fps: Frames per second
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL not available. Install with: pip install pillow")
        
        self.width = width
        self.height = height
        self.fps = fps
        
        # Video styling
        self.background_color = (30, 30, 30)  # Dark background
        self.code_bg_color = (45, 45, 48)     # Code area background
        self.text_color = (255, 255, 255)     # White text
        self.highlight_color = (255, 215, 0)  # Gold for highlighting
        
        # Animation settings
        self.animation_duration = 0.5  # seconds for transitions
        self.highlight_duration = 2.0  # seconds for code highlighting
        
    def create_animated_video(self, code: str, audio_path: str, explanation: Dict[str, Any],
                            output_path: str = "animated_code.mp4") -> str:
        """
        Create an animated video with moving elements and code highlighting.
        
        Args:
            code: Source code to display
            audio_path: Path to narration audio file
            explanation: Explanation dictionary
            output_path: Path to save the video
            
        Returns:
            Path to the generated video
        """
        try:
            # Get audio duration
            duration = self._get_audio_duration(audio_path)
            total_frames = int(duration * self.fps)
            
            # Create frames directory
            frames_dir = "temp_frames"
            os.makedirs(frames_dir, exist_ok=True)
            
            # Generate animated frames
            self._generate_animated_frames(code, explanation, frames_dir, total_frames)
            
            # Create video from frames using ffmpeg
            self._create_video_from_frames(frames_dir, audio_path, output_path, duration)
            
            # Clean up frames
            self._cleanup_frames(frames_dir)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Animated video rendering failed: {str(e)}")
    
    def _generate_animated_frames(self, code: str, explanation: Dict[str, Any], frames_dir: str, total_frames: int):
        """Generate animated frames with moving elements."""
        code_lines = code.strip().split('\n')
        
        for frame_num in range(total_frames):
            # Calculate animation parameters
            time = frame_num / self.fps
            
            # Create frame
            img = self._create_animated_frame(code_lines, explanation, time, frame_num)
            
            # Save frame
            frame_path = os.path.join(frames_dir, f"frame_{frame_num:06d}.png")
            img.save(frame_path)
    
    def _create_animated_frame(self, code_lines: List[str], explanation: Dict[str, Any], time: float, frame_num: int) -> Image.Image:
        """Create a single animated frame."""
        # Create base image
        img = Image.new('RGB', (self.width, self.height), color=self.background_color)
        draw = ImageDraw.Draw(img)
        
        # Load fonts
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_code = ImageFont.load_default()
            font_small = ImageFont.load_default()
        
        # Animated title with fade-in and bounce
        title_text = explanation.get('title', 'Code Explanation')
        title_alpha = min(1.0, time / 1.0)  # Fade in over 1 second
        title_bounce = math.sin(time * 3) * 5 if time > 1.0 else 0  # Bounce after fade-in
        
        title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        title_y = 80 + title_bounce
        
        # Draw title with fade effect
        title_color = tuple(int(c * title_alpha) for c in self.text_color)
        draw.text((title_x, title_y), title_text, fill=title_color, font=font_large)
        
        # Animated avatar (bouncing emoji)
        avatar_text = "👨‍💻"
        avatar_bounce = math.sin(time * 2) * 10
        avatar_x = 100
        avatar_y = 200 + avatar_bounce
        
        # Draw avatar
        draw.text((avatar_x, avatar_y), avatar_text, fill='white', font=font_large)
        
        # Animated code with line-by-line highlighting
        y_pos = 300
        line_height = 40
        max_lines = min(12, len(code_lines))
        
        for i, line in enumerate(code_lines[:max_lines]):
            # Calculate line animation
            line_start_time = i * 0.5  # Each line appears 0.5 seconds apart
            line_alpha = min(1.0, (time - line_start_time) / 0.3)  # Fade in over 0.3 seconds
            
            if line_alpha > 0:
                # Calculate highlight timing
                highlight_start = line_start_time + 0.5
                highlight_end = highlight_start + self.highlight_duration
                is_highlighted = highlight_start <= time <= highlight_end
                
                # Line number
                line_num = f"{i+1:2d} "
                line_num_color = tuple(int(c * line_alpha) for c in (136, 136, 136))
                draw.text((50, y_pos), line_num, fill=line_num_color, font=font_code)
                
                # Code line with highlighting
                code_x = 50 + len(line_num) * 12
                if is_highlighted:
                    # Highlighted line
                    highlight_intensity = 0.5 + 0.5 * math.sin((time - highlight_start) * 4)
                    line_color = tuple(int(c * line_alpha * (1 + highlight_intensity * 0.5)) for c in self.highlight_color)
                else:
                    # Normal line
                    line_color = tuple(int(c * line_alpha) for c in self.text_color)
                
                draw.text((code_x, y_pos), line, fill=line_color, font=font_code)
                
                y_pos += line_height
        
        # Animated explanation text
        if time > 2.0:  # Start showing explanation after 2 seconds
            explanation_text = explanation.get('overview', 'Code explanation generated by AI')
            explanation_alpha = min(1.0, (time - 2.0) / 1.0)  # Fade in over 1 second
            
            # Wrap text
            words = explanation_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font_small)
                if bbox[2] - bbox[0] < self.width - 100:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Draw explanation lines with animation
            explanation_y = self.height - 120
            for i, line in enumerate(lines[:3]):
                bbox = draw.textbbox((0, 0), line, font=font_small)
                line_width = bbox[2] - bbox[0]
                line_x = (self.width - line_width) // 2
                
                # Staggered fade-in for each line
                line_alpha = min(1.0, (time - 2.0 - i * 0.2) / 0.5)
                line_color = tuple(int(c * line_alpha * explanation_alpha) for c in (204, 204, 204))
                
                draw.text((line_x, explanation_y + i * 30), line, fill=line_color, font=font_small)
        
        # Add animated border
        border_alpha = min(1.0, time / 0.5)
        border_color = tuple(int(c * border_alpha) for c in (60, 60, 60))
        draw.rectangle([40, 280, self.width - 40, y_pos + 20], outline=border_color, width=2)
        
        return img
    
    def _get_audio_duration(self, audio_path: str) -> float:
        """Get audio duration using ffprobe."""
        try:
            result = subprocess.run([
                'ffprobe', '-v', 'quiet', '-show_entries', 'format=duration',
                '-of', 'csv=p=0', audio_path
            ], capture_output=True, text=True)
            
            if result.returncode == 0:
                return float(result.stdout.strip())
            else:
                return 10.0  # Default duration
        except:
            return 10.0  # Default duration
    
    def _create_video_from_frames(self, frames_dir: str, audio_path: str, output_path: str, duration: float):
        """Create video from frames and audio using ffmpeg."""
        try:
            # Create video from frames
            temp_video = "temp_video.mp4"
            subprocess.run([
                'ffmpeg', '-y',
                '-framerate', str(self.fps),
                '-i', os.path.join(frames_dir, 'frame_%06d.png'),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                temp_video
            ], check=True)
            
            # Combine video with audio
            subprocess.run([
                'ffmpeg', '-y',
                '-i', temp_video,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-shortest',
                output_path
            ], check=True)
            
            # Clean up temp video
            if os.path.exists(temp_video):
                os.remove(temp_video)
                
        except subprocess.CalledProcessError as e:
            raise Exception(f"FFmpeg failed: {e}")
    
    def _cleanup_frames(self, frames_dir: str):
        """Clean up temporary frame files."""
        try:
            for file in os.listdir(frames_dir):
                os.remove(os.path.join(frames_dir, file))
            os.rmdir(frames_dir)
        except:
            pass


def main():
    """Test the animated video renderer."""
    if not PIL_AVAILABLE:
        print("PIL not available. Install with: pip install pillow")
        return
    
    renderer = AnimatedVideoRenderer()
    
    # Test code
    test_code = """
def factorial(n):
    if n == 0:
        return 1
    else:
        return n * factorial(n - 1)

result = factorial(5)
print(f"Factorial of 5 is: {result}")
"""
    
    # Test explanation
    explanation = {
        'title': 'Animated Code Explanation',
        'overview': 'This code demonstrates recursion with a factorial function.',
        'key_takeaways': ['Recursion', 'Base case', 'Mathematical concept']
    }
    
    # Create animated video
    try:
        output_path = renderer.create_animated_video(
            code=test_code,
            audio_path="test_audio.wav",  # You'll need to create this
            explanation=explanation,
            output_path="test_animated.mp4"
        )
        print(f"Animated video created: {output_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 