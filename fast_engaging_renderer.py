"""
Fast Engaging Video Renderer - Fast but with animations and emojis
Creates engaging videos with emojis, animations, and visual effects while maintaining speed.
"""

import os
import json
import subprocess
import tempfile
import math
import random
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance

class FastEngagingVideoRenderer:
    """Fast video renderer with engaging animations and emojis."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        self.width = width
        self.height = height
        self.fps = fps
        
        # Emoji and animation settings
        self.emojis = {
            'code': ['💻', '⚡', '🚀', '🔥', '✨', '🎯', '💡', '🎨'],
            'function': ['🔧', '⚙️', '🎮', '🎪', '🎭', '🎪'],
            'loop': ['🔄', '⚡', '🎢', '🎡', '🎠'],
            'condition': ['🤔', '❓', '💭', '🧠', '🎯'],
            'success': ['✅', '🎉', '🏆', '🥇', '🌟', '💫'],
            'error': ['❌', '💥', '⚠️', '🚨', '💢'],
            'data': ['📊', '📈', '📉', '🎲', '🎯'],
            'default': ['🎪', '🎭', '🎨', '🎪', '🎪']
        }
        
        # Animation particles
        self.particles = []
        
    def create_animated_video(self, code: str, audio_path: str, explanation: Dict[str, Any],
                            output_path: str = "fast_engaging_video.mp4", narration_text: str = None) -> str:
        """Create a fast but engaging animated video."""
        
        # Get audio duration
        duration = self._get_audio_duration(audio_path)
        
        # Calculate frame count based on duration
        total_frames = int(duration * self.fps)
        frame_duration = duration / total_frames
        
        # Create frames with animations
        frames = self._create_animated_frames(code, explanation, total_frames, duration)
        
        # Save frames as images
        frame_dir = tempfile.mkdtemp()
        frame_paths = []
        
        for i, frame in enumerate(frames):
            frame_path = os.path.join(frame_dir, f"frame_{i:04d}.png")
            frame.save(frame_path)
            frame_paths.append(frame_path)
        
        # Create video with ffmpeg
        self._create_video_from_frames(frame_paths, audio_path, output_path, duration, frame_duration)
        
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
    
    def _create_animated_frames(self, code: str, explanation: Dict[str, Any], 
                              total_frames: int, duration: float) -> List[Image.Image]:
        """Create animated frames with emojis and effects."""
        frames = []
        
        # Initialize particles
        self._init_particles()
        
        for i in range(total_frames):
            progress = i / (total_frames - 1)
            time = progress * duration
            
            # Create frame with animations
            frame = self._create_animated_frame(code, explanation, progress, time, i)
            frames.append(frame)
            
            # Update particles
            self._update_particles()
        
        return frames
    
    def _init_particles(self):
        """Initialize floating particles."""
        self.particles = []
        for _ in range(20):
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'vx': random.uniform(-1, 1),
                'vy': random.uniform(-1, 1),
                'size': random.randint(2, 6),
                'color': random.choice([(100, 150, 255), (255, 100, 150), (100, 255, 150), (255, 200, 100)])
            })
    
    def _update_particles(self):
        """Update particle positions."""
        for particle in self.particles:
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Bounce off edges
            if particle['x'] <= 0 or particle['x'] >= self.width:
                particle['vx'] *= -1
            if particle['y'] <= 0 or particle['y'] >= self.height:
                particle['vy'] *= -1
    
    def _create_animated_frame(self, code: str, explanation: Dict[str, Any], 
                             progress: float, time: float, frame_num: int) -> Image.Image:
        """Create a single animated frame."""
        # Create base image with gradient background
        img = Image.new('RGB', (self.width, self.height), color=(30, 30, 30))
        draw = ImageDraw.Draw(img)
        
        # Animated gradient background
        self._draw_animated_background(draw, progress, time)
        
        # Draw floating particles
        self._draw_particles(draw)
        
        # Determine current section based on progress
        section = self._get_current_section(progress, time)
        
        # Draw content based on section
        if section == 'title':
            self._draw_animated_title(draw, explanation, progress, time)
        elif section == 'code_intro':
            self._draw_code_intro(draw, code, progress, time)
        elif section == 'code_detail':
            self._draw_animated_code(draw, code, progress, time)
        elif section == 'explanation':
            self._draw_animated_explanation(draw, explanation, progress, time)
        else:  # summary
            self._draw_animated_summary(draw, explanation, progress, time)
        
        # Draw animated border
        self._draw_animated_border(draw, progress, time)
        
        return img
    
    def _draw_animated_background(self, draw: ImageDraw.Draw, progress: float, time: float):
        """Draw animated gradient background."""
        for y in range(self.height):
            # Animated gradient
            base_color = 30 + int(20 * math.sin(time * 0.5 + y * 0.01))
            color = (base_color, base_color + 10, base_color + 20)
            draw.line([(0, y), (self.width, y)], fill=color)
    
    def _draw_particles(self, draw: ImageDraw.Draw):
        """Draw floating particles."""
        for particle in self.particles:
            x, y = int(particle['x']), int(particle['y'])
            size = particle['size']
            color = particle['color']
            
            # Draw particle with glow effect
            for offset in range(size):
                alpha = 1 - (offset / size)
                glow_color = tuple(int(c * alpha) for c in color)
                draw.ellipse([x - offset, y - offset, x + offset, y + offset], 
                           fill=glow_color)
    
    def _get_current_section(self, progress: float, time: float) -> str:
        """Determine current section based on progress."""
        if progress < 0.2:
            return 'title'
        elif progress < 0.4:
            return 'code_intro'
        elif progress < 0.7:
            return 'code_detail'
        elif progress < 0.9:
            return 'explanation'
        else:
            return 'summary'
    
    def _draw_animated_title(self, draw: ImageDraw.Draw, explanation: Dict[str, Any], 
                           progress: float, time: float):
        """Draw animated title with emojis."""
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 72)
            font_emoji = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
        except:
            font_large = ImageFont.load_default()
            font_emoji = ImageFont.load_default()
        
        title = explanation.get('title', 'Code Explanation')
        
        # Animated title with bounce effect
        bounce = math.sin(time * 3) * 5
        title_y = 200 + bounce
        
        # Title with emoji
        emoji = random.choice(self.emojis['code'])
        full_title = f"{emoji} {title} {emoji}"
        
        # Glow effect
        for offset in range(5):
            alpha = 1 - (offset / 5)
            glow_color = (int(100 * alpha), int(150 * alpha), int(255 * alpha))
            draw.text((self.width//2 - 300 + offset, title_y + offset), 
                     full_title, fill=glow_color, font=font_large)
        
        # Main title
        draw.text((self.width//2 - 300, title_y), full_title, 
                 fill=(255, 255, 255), font=font_large)
        
        # Floating emojis
        for i in range(3):
            emoji_x = 100 + i * 200 + math.sin(time * 2 + i) * 50
            emoji_y = 400 + math.cos(time * 1.5 + i) * 30
            floating_emoji = random.choice(self.emojis['default'])
            draw.text((emoji_x, emoji_y), floating_emoji, 
                     fill=(255, 200, 100), font=font_emoji)
    
    def _draw_code_intro(self, draw: ImageDraw.Draw, code: str, progress: float, time: float):
        """Draw animated code introduction."""
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 32)
            font_emoji = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
            font_emoji = ImageFont.load_default()
        
        # Animated code box
        box_alpha = min(1.0, progress * 5)  # Fade in
        box_color = (int(45 * box_alpha), int(45 * box_alpha), int(48 * box_alpha))
        
        # Code area with animation
        box_y = 150 + int(20 * math.sin(time * 2))
        draw.rectangle([50, box_y, self.width - 50, self.height - 150], 
                      fill=box_color, outline=(80, 80, 80), width=3)
        
        # Code lines with staggered animation
        lines = code.strip().split('\n')
        y_pos = box_y + 50
        
        for i, line in enumerate(lines[:8]):
            line_alpha = min(1.0, (progress - i * 0.1) * 3)
            if line_alpha > 0:
                # Line number with emoji
                line_num = f"{i+1:2d} "
                emoji = random.choice(self.emojis['code'])
                line_with_emoji = f"{emoji} {line}"
                
                # Animated position
                line_x = 70 + int(10 * math.sin(time + i))
                
                # Draw line
                color = tuple(int(c * line_alpha) for c in (255, 255, 255))
                draw.text((line_x, y_pos), line_num, fill=(100, 100, 100), font=font)
                draw.text((line_x + len(line_num) * 15, y_pos), line_with_emoji, 
                         fill=color, font=font)
                
                y_pos += 40
    
    def _draw_animated_code(self, draw: ImageDraw.Draw, code: str, progress: float, time: float):
        """Draw animated code with syntax highlighting and emojis."""
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 28)
            font_emoji = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
        except:
            font = ImageFont.load_default()
            font_emoji = ImageFont.load_default()
        
        # Code area
        draw.rectangle([50, 100, self.width - 50, self.height - 100], 
                      fill=(45, 45, 48), outline=(80, 80, 80), width=3)
        
        lines = code.strip().split('\n')
        y_pos = 150
        
        for i, line in enumerate(lines[:12]):
            # Animated highlighting
            highlight_alpha = 0.5 + 0.5 * math.sin(time * 2 + i)
            
            # Line number with emoji
            line_num = f"{i+1:2d} "
            emoji = self._get_line_emoji(line)
            
            # Syntax highlighting with emojis
            if 'def ' in line:
                color = (255, 200, 100)  # Orange for functions
                emoji = random.choice(self.emojis['function'])
            elif 'if ' in line or 'else' in line:
                color = (100, 200, 255)  # Blue for conditions
                emoji = random.choice(self.emojis['condition'])
            elif 'for ' in line or 'while ' in line:
                color = (200, 255, 100)  # Green for loops
                emoji = random.choice(self.emojis['loop'])
            elif 'return ' in line:
                color = (255, 100, 100)  # Red for returns
                emoji = random.choice(self.emojis['success'])
            elif 'print(' in line:
                color = (100, 255, 100)  # Green for prints
                emoji = random.choice(self.emojis['data'])
            else:
                color = (255, 255, 255)  # White for regular code
                emoji = random.choice(self.emojis['default'])
            
            # Animated position
            line_x = 70 + int(5 * math.sin(time + i * 0.5))
            
            # Draw line with emoji
            draw.text((line_x, y_pos), line_num, fill=(100, 100, 100), font=font)
            draw.text((line_x + len(line_num) * 15, y_pos), emoji, 
                     fill=(255, 200, 100), font=font_emoji)
            draw.text((line_x + len(line_num) * 15 + 25, y_pos), line, 
                     fill=color, font=font)
            
            # Highlight current line
            if i == int(time * 2) % len(lines):
                highlight_rect = [line_x - 10, y_pos - 5, 
                                line_x + len(line) * 15 + 50, y_pos + 30]
                highlight_color = (int(255 * highlight_alpha), 
                                 int(200 * highlight_alpha), 
                                 int(100 * highlight_alpha))
                draw.rectangle(highlight_rect, fill=highlight_color, outline=(255, 200, 100))
            
            y_pos += 35
    
    def _get_line_emoji(self, line: str) -> str:
        """Get appropriate emoji for a code line."""
        if 'def ' in line:
            return random.choice(self.emojis['function'])
        elif 'if ' in line or 'else' in line:
            return random.choice(self.emojis['condition'])
        elif 'for ' in line or 'while ' in line:
            return random.choice(self.emojis['loop'])
        elif 'return ' in line:
            return random.choice(self.emojis['success'])
        elif 'print(' in line:
            return random.choice(self.emojis['data'])
        else:
            return random.choice(self.emojis['default'])
    
    def _draw_animated_explanation(self, draw: ImageDraw.Draw, explanation: Dict[str, Any], 
                                 progress: float, time: float):
        """Draw animated explanation with emojis."""
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
            font_emoji = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_emoji = ImageFont.load_default()
        
        # Title with emoji
        title = "Explanation"
        emoji = random.choice(self.emojis['code'])
        full_title = f"{emoji} {title} {emoji}"
        
        # Animated title
        title_y = 100 + int(10 * math.sin(time * 2))
        draw.text((self.width//2 - 200, title_y), full_title, 
                 fill=(255, 255, 255), font=font_large)
        
        # Explanation text with emojis
        explanation_text = explanation.get('overview', 'Code explanation')
        words = explanation_text.split()
        
        y_pos = 200
        for i, word in enumerate(words):
            # Add emoji every few words
            if i % 3 == 0:
                word_emoji = random.choice(self.emojis['default'])
                word_with_emoji = f"{word} {word_emoji}"
            else:
                word_with_emoji = word
            
            # Animated position
            word_x = 100 + i * 50 + int(10 * math.sin(time + i * 0.5))
            
            # Word animation
            word_alpha = min(1.0, (progress - i * 0.05) * 2)
            if word_alpha > 0:
                color = tuple(int(c * word_alpha) for c in (200, 200, 255))
                draw.text((word_x, y_pos), word_with_emoji, fill=color, font=font_small)
            
            # New line every 8 words
            if (i + 1) % 8 == 0:
                y_pos += 50
    
    def _draw_animated_summary(self, draw: ImageDraw.Draw, explanation: Dict[str, Any], 
                             progress: float, time: float):
        """Draw animated summary with success emojis."""
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 64)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            font_emoji = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
        except:
            font_large = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_emoji = ImageFont.load_default()
        
        # Success title with emojis
        title = "Success!"
        emoji = random.choice(self.emojis['success'])
        full_title = f"{emoji} {title} {emoji}"
        
        # Bouncing title
        bounce = math.sin(time * 4) * 10
        title_y = 150 + bounce
        draw.text((self.width//2 - 200, title_y), full_title, 
                 fill=(100, 255, 100), font=font_large)
        
        # Key takeaways with emojis
        takeaways = explanation.get('key_takeaways', ['Code explanation completed!'])
        y_pos = 300
        
        for i, takeaway in enumerate(takeaways[:3]):
            takeaway_emoji = random.choice(self.emojis['success'])
            takeaway_with_emoji = f"{takeaway_emoji} {takeaway}"
            
            # Animated position
            takeaway_x = 200 + int(20 * math.sin(time + i))
            
            # Fade in animation
            takeaway_alpha = min(1.0, (progress - i * 0.2) * 3)
            if takeaway_alpha > 0:
                color = tuple(int(c * takeaway_alpha) for c in (200, 255, 200))
                draw.text((takeaway_x, y_pos), takeaway_with_emoji, 
                         fill=color, font=font_small)
            
            y_pos += 80
        
        # Celebration emojis
        for i in range(5):
            emoji_x = 100 + i * 200 + math.sin(time * 2 + i) * 30
            emoji_y = 600 + math.cos(time * 1.5 + i) * 20
            celebration_emoji = random.choice(self.emojis['success'])
            draw.text((emoji_x, emoji_y), celebration_emoji, 
                     fill=(255, 200, 100), font=font_emoji)
    
    def _draw_animated_border(self, draw: ImageDraw.Draw, progress: float, time: float):
        """Draw animated border."""
        # Animated border color
        border_color = (
            int(100 + 50 * math.sin(time)),
            int(150 + 50 * math.cos(time)),
            int(200 + 50 * math.sin(time * 0.5))
        )
        
        # Animated border thickness
        border_width = 2 + int(2 * math.sin(time * 3))
        
        draw.rectangle([20, 20, self.width - 20, self.height - 20], 
                      outline=border_color, width=border_width)
    
    def _create_video_from_frames(self, frame_paths: List[str], audio_path: str, 
                                output_path: str, duration: float, frame_duration: float):
        """Create video from frames using ffmpeg."""
        
        # Create frame list file
        frame_list = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for frame_path in frame_paths:
            frame_list.write(f"file '{frame_path}'\n")
            frame_list.write(f"duration {frame_duration}\n")
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
    """Test the fast engaging renderer."""
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
        "key_takeaways": ["Recursion is powerful", "Base cases are important", "Math meets programming"]
    }
    
    renderer = FastEngagingVideoRenderer()
    
    # Test with dummy audio
    silent_audio = "silent.wav"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-t', '8', silent_audio
    ])
    
    output_path = renderer.create_animated_video(
        example_code, silent_audio, example_explanation, "fast_engaging_test.mp4"
    )
    
    print(f"Fast engaging video created: {output_path}")
    
    # Cleanup
    os.remove(silent_audio)


if __name__ == "__main__":
    main() 