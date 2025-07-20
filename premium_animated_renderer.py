#!/usr/bin/env python3

"""
Premium Animated Video Renderer for Code2Vid
Creates stunning, engaging videos with advanced animations and visual effects.
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
import random

try:
    from PIL import Image, ImageDraw, ImageFont, ImageFilter, ImageEnhance
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class PremiumAnimatedVideoRenderer:
    """Creates premium animated videos with stunning visual effects."""
    
    def __init__(self, width: int = 1920, height: int = 1080, fps: int = 30):
        """
        Initialize the premium animated video renderer.
        
        Args:
            width: Video width in pixels
            height: Video height in pixels
            fps: Frames per second for smooth animations
        """
        if not PIL_AVAILABLE:
            raise ImportError("PIL not available. Install with: pip install pillow")
        
        self.width = width
        self.height = height
        self.fps = fps
        
        # Premium color scheme
        self.background_gradient = [(20, 25, 35), (35, 40, 55)]  # Dark blue gradient
        self.code_bg_color = (25, 30, 40)  # Dark code background
        self.text_color = (255, 255, 255)  # White text
        self.highlight_color = (0, 255, 255)  # Cyan for highlighting
        self.accent_color = (255, 105, 180)  # Hot pink accents
        self.explanation_color = (173, 216, 230)  # Light blue explanations
        
        # Animation settings
        self.particle_count = 50
        self.particles = []
        self._init_particles()
        
    def _init_particles(self):
        """Initialize floating particles for background effect."""
        for _ in range(self.particle_count):
            self.particles.append({
                'x': random.randint(0, self.width),
                'y': random.randint(0, self.height),
                'vx': random.uniform(-0.5, 0.5),
                'vy': random.uniform(-0.5, 0.5),
                'size': random.uniform(1, 3),
                'alpha': random.uniform(0.1, 0.3)
            })
    
    def create_animated_video(self, code: str, audio_path: str, explanation: Dict[str, Any],
                            output_path: str = "premium_code.mp4", narration_text: str = None) -> str:
        """
        Create a premium animated video with stunning effects.
        
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
            
            # Generate line-by-line explanations
            line_explanations = self._generate_line_explanations(code, explanation)
            
            # Initialize subtitle overlay if narration text is provided
            subtitle_overlay = None
            subtitle_segments = None
            if narration_text:
                try:
                    from subtitle_overlay import SubtitleOverlay
                    subtitle_overlay = SubtitleOverlay()
                    subtitle_segments = subtitle_overlay.process_narration(narration_text)
                    print(f"📝 Generated {len(subtitle_segments)} subtitle segments with emojis")
                except Exception as e:
                    print(f"⚠️ Subtitle overlay failed: {e}")
            
            # Use more frames for smooth animations
            frame_interval = 1.0 / self.fps  # 30 FPS for smooth motion
            total_frames = int(duration * self.fps)
            
            print(f"🎬 Creating {total_frames} premium frames for {duration:.1f}s video...")
            
            # Create frames directory
            frames_dir = "temp_frames"
            os.makedirs(frames_dir, exist_ok=True)
            
            # Generate premium frames with subtitle overlay
            self._generate_premium_frames(code, explanation, line_explanations, frames_dir, total_frames, frame_interval, subtitle_overlay, subtitle_segments)
            
            # Create video from frames using ffmpeg
            self._create_video_from_frames(frames_dir, audio_path, output_path, duration, frame_interval)
            
            # Clean up frames
            self._cleanup_frames(frames_dir)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"Premium video rendering failed: {str(e)}")
    
    def _generate_line_explanations(self, code: str, explanation: Dict[str, Any]) -> List[Dict[str, Any]]:
        """Generate detailed explanations for each line of code."""
        code_lines = code.strip().split('\n')
        line_explanations = []
        
        for i, line in enumerate(code_lines):
            line = line.strip()
            if not line:  # Skip empty lines
                continue
                
            # Generate explanation based on line content
            explanation_text = self._analyze_line(line, i, code_lines)
            
            line_explanations.append({
                'line_number': i + 1,
                'code': line,
                'explanation': explanation_text,
                'start_time': i * 2.0,  # Each line gets 2 seconds
                'duration': 1.5  # Explanation duration
            })
        
        return line_explanations
    
    def _analyze_line(self, line: str, line_index: int, all_lines: List[str]) -> str:
        """Analyze a single line of code and generate explanation."""
        line = line.strip()
        
        # Function definition
        if line.startswith('def '):
            func_name = line.split('(')[0].replace('def ', '')
            return f"This defines a function called '{func_name}' that can be called later in the code."
        
        # If statement
        elif line.startswith('if '):
            condition = line.replace('if ', '').replace(':', '').strip()
            return f"This checks if {condition} is true. If it is, the code inside the if block will run."
        
        # Else statement
        elif line.startswith('else'):
            return "This runs when the previous if condition is false. It's the alternative path."
        
        # Return statement
        elif line.startswith('return '):
            value = line.replace('return ', '').strip()
            return f"This returns the value {value} from the function, ending its execution."
        
        # Print statement
        elif line.startswith('print('):
            content = line.replace('print(', '').replace(')', '').strip()
            return f"This prints {content} to the console so we can see the output."
        
        # Variable assignment
        elif '=' in line and not line.startswith('#'):
            parts = line.split('=')
            var_name = parts[0].strip()
            value = parts[1].strip()
            return f"This assigns the value {value} to the variable '{var_name}'."
        
        # Function call
        elif '(' in line and ')' in line and not line.startswith('#'):
            func_name = line.split('(')[0].strip()
            return f"This calls the function '{func_name}' to execute its code."
        
        # Comment
        elif line.startswith('#'):
            comment = line.replace('#', '').strip()
            return f"This is a comment: {comment}. Comments help explain the code but don't affect execution."
        
        # Indented code (likely inside a block)
        elif line.startswith('    ') or line.startswith('\t'):
            return "This line is indented, meaning it's part of a code block (like inside an if statement or function)."
        
        # Default explanation
        else:
            return f"This line contains: {line}. It's part of the program's logic."
    
    def _generate_premium_frames(self, code: str, explanation: Dict[str, Any], line_explanations: List[Dict[str, Any]], 
                               frames_dir: str, total_frames: int, frame_interval: float,
                               subtitle_overlay=None, subtitle_segments=None):
        """Generate premium frames with advanced animations."""
        code_lines = code.strip().split('\n')
        
        for frame_num in range(total_frames):
            # Calculate animation parameters
            time = frame_num * frame_interval
            
            # Create frame
            img = self._create_premium_frame(code_lines, explanation, line_explanations, time, frame_num, subtitle_overlay, subtitle_segments)
            
            # Save frame with high quality
            frame_path = os.path.join(frames_dir, f"frame_{frame_num:06d}.png")
            img.save(frame_path, optimize=True, quality=95)
            
            # Progress indicator
            if frame_num % 30 == 0:
                print(f"   Generated frame {frame_num}/{total_frames}")
    
    def _create_gradient_background(self, width: int, height: int) -> Image.Image:
        """Create a beautiful gradient background."""
        img = Image.new('RGB', (width, height))
        draw = ImageDraw.Draw(img)
        
        # Create gradient from top to bottom
        for y in range(height):
            ratio = y / height
            r = int(self.background_gradient[0][0] * (1 - ratio) + self.background_gradient[1][0] * ratio)
            g = int(self.background_gradient[0][1] * (1 - ratio) + self.background_gradient[1][1] * ratio)
            b = int(self.background_gradient[0][2] * (1 - ratio) + self.background_gradient[1][2] * ratio)
            draw.line([(0, y), (width, y)], fill=(r, g, b))
        
        return img
    
    def _draw_particles(self, draw: ImageDraw.Draw, time: float):
        """Draw floating particles in the background."""
        for particle in self.particles:
            # Update particle position
            particle['x'] += particle['vx']
            particle['y'] += particle['vy']
            
            # Wrap around edges
            if particle['x'] < 0:
                particle['x'] = self.width
            elif particle['x'] > self.width:
                particle['x'] = 0
            if particle['y'] < 0:
                particle['y'] = self.height
            elif particle['y'] > self.height:
                particle['y'] = 0
            
            # Draw particle with pulsing effect
            pulse = 0.5 + 0.5 * math.sin(time * 2 + particle['x'] * 0.01)
            size = particle['size'] * pulse
            alpha = int(particle['alpha'] * 255 * pulse)
            
            color = (100, 150, 255, alpha)
            x, y = int(particle['x']), int(particle['y'])
            
            # Draw particle as a small circle
            draw.ellipse([x-size, y-size, x+size, y+size], fill=color)
    
    def _create_premium_frame(self, code_lines: List[str], explanation: Dict[str, Any], 
                            line_explanations: List[Dict[str, Any]], time: float, frame_num: int,
                            subtitle_overlay=None, subtitle_segments=None) -> Image.Image:
        """Create a premium frame with advanced visual effects."""
        # Create gradient background
        img = self._create_gradient_background(self.width, self.height)
        draw = ImageDraw.Draw(img, 'RGBA')
        
        # Draw particles
        self._draw_particles(draw, time)
        
        # Load fonts
        try:
            font_large = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 56)
            font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 36)
            font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 28)
            font_explanation = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font_large = ImageFont.load_default()
            font_code = ImageFont.load_default()
            font_small = ImageFont.load_default()
            font_explanation = ImageFont.load_default()
        
        # Animated title with glow effect
        title_text = explanation.get('title', 'Premium Code Explanation')
        title_alpha = min(1.0, time / 1.5)  # Fade in over 1.5 seconds
        
        title_bbox = draw.textbbox((0, 0), title_text, font=font_large)
        title_width = title_bbox[2] - title_bbox[0]
        title_x = (self.width - title_width) // 2
        title_y = 80 + math.sin(time * 0.5) * 3  # Gentle floating
        
        # Draw title glow
        glow_alpha = int(50 * title_alpha)
        for offset in range(1, 4):
            glow_color = (0, 255, 255, glow_alpha // offset)
            draw.text((title_x + offset, title_y + offset), title_text, fill=glow_color, font=font_large)
        
        # Draw main title
        title_color = tuple(int(c * title_alpha) for c in self.text_color)
        draw.text((title_x, title_y), title_text, fill=title_color, font=font_large)
        
        # Animated avatar with effects
        avatar_text = "👨‍💻"
        avatar_bounce = math.sin(time * 1.2) * 8
        avatar_rotation = math.sin(time * 0.8) * 5
        avatar_x = 120
        avatar_y = 180 + avatar_bounce
        
        # Draw avatar glow
        avatar_glow = int(30 * (0.5 + 0.5 * math.sin(time * 2)))
        for offset in range(1, 3):
            glow_color = (255, 105, 180, avatar_glow // offset)
            draw.text((avatar_x + offset, avatar_y + offset), avatar_text, fill=glow_color, font=font_large)
        
        # Draw avatar
        draw.text((avatar_x, avatar_y), avatar_text, fill='white', font=font_large)
        
        # Code area with premium styling
        code_start_y = 280
        line_height = 45
        max_lines = min(10, len(code_lines))
        
        # Find which line is currently being explained
        current_explanation = None
        for exp in line_explanations:
            if exp['start_time'] <= time <= exp['start_time'] + exp['duration']:
                current_explanation = exp
                break
        
        # Draw code background with rounded corners effect
        code_bg_rect = [60, code_start_y - 20, self.width - 60, code_start_y + max_lines * line_height + 20]
        draw.rectangle(code_bg_rect, fill=(*self.code_bg_color, 200), outline=(100, 150, 255, 100), width=2)
        
        # Draw code lines with advanced effects
        for i, line in enumerate(code_lines[:max_lines]):
            # Line animation with easing
            line_start_time = i * 2.0
            line_alpha = min(1.0, (time - line_start_time) / 0.8)
            
            if line_alpha > 0:
                # Check if this line is currently being explained
                is_currently_explained = (current_explanation and 
                                        current_explanation['line_number'] == i + 1)
                
                # Line number with glow
                line_num = f"{i+1:2d} "
                line_num_color = tuple(int(c * line_alpha) for c in (150, 150, 150))
                draw.text((80, code_start_y + i * line_height), line_num, fill=line_num_color, font=font_code)
                
                # Code line with advanced highlighting
                code_x = 80 + len(line_num) * 15
                if is_currently_explained:
                    # Currently explained line - premium highlighting
                    pulse = 0.5 + 0.5 * math.sin((time - current_explanation['start_time']) * 8)
                    line_color = tuple(int(c * line_alpha * (1 + pulse * 0.3)) for c in self.highlight_color)
                    
                    # Draw highlight background with gradient
                    highlight_rect = [
                        code_x - 15, 
                        code_start_y + i * line_height - 8,
                        code_x + len(line) * 15 + 15,
                        code_start_y + i * line_height + 35
                    ]
                    
                    # Gradient highlight background
                    for y_offset in range(highlight_rect[1], highlight_rect[3]):
                        ratio = (y_offset - highlight_rect[1]) / (highlight_rect[3] - highlight_rect[1])
                        r = int(self.highlight_color[0] * 0.2 * (1 - ratio))
                        g = int(self.highlight_color[1] * 0.2 * (1 - ratio))
                        b = int(self.highlight_color[2] * 0.2 * (1 - ratio))
                        alpha = int(100 * line_alpha * pulse)
                        draw.line([(highlight_rect[0], y_offset), (highlight_rect[2], y_offset)], 
                                fill=(r, g, b, alpha))
                    
                    # Draw line glow
                    glow_alpha = int(50 * line_alpha * pulse)
                    for offset in range(1, 3):
                        glow_color = (*self.highlight_color, glow_alpha // offset)
                        draw.text((code_x + offset, code_start_y + i * line_height + offset), 
                                line, fill=glow_color, font=font_code)
                else:
                    # Normal line
                    line_color = tuple(int(c * line_alpha) for c in self.text_color)
                
                draw.text((code_x, code_start_y + i * line_height), line, fill=line_color, font=font_code)
        
        # Draw current line explanation with premium styling
        if current_explanation:
            explanation_text = current_explanation['explanation']
            explanation_alpha = min(1.0, (time - current_explanation['start_time']) / 0.5)
            
            # Wrap explanation text
            words = explanation_text.split()
            lines = []
            current_line = ""
            
            for word in words:
                test_line = current_line + " " + word if current_line else word
                bbox = draw.textbbox((0, 0), test_line, font=font_explanation)
                if bbox[2] - bbox[0] < self.width - 200:
                    current_line = test_line
                else:
                    if current_line:
                        lines.append(current_line)
                    current_line = word
            if current_line:
                lines.append(current_line)
            
            # Draw explanation background
            explanation_bg_rect = [100, self.height - 200, self.width - 100, self.height - 80]
            draw.rectangle(explanation_bg_rect, fill=(25, 30, 40, 180), outline=(100, 150, 255, 150), width=2)
            
            # Draw explanation lines with effects
            explanation_y = self.height - 180
            for j, line in enumerate(lines[:3]):
                bbox = draw.textbbox((0, 0), line, font=font_explanation)
                line_width = bbox[2] - bbox[0]
                line_x = (self.width - line_width) // 2
                
                # Staggered fade-in with glow
                line_alpha = min(1.0, (time - current_explanation['start_time'] - j * 0.2) / 0.6)
                
                # Draw text glow
                glow_alpha = int(30 * line_alpha * explanation_alpha)
                for offset in range(1, 2):
                    glow_color = (*self.explanation_color, glow_alpha // offset)
                    draw.text((line_x + offset, explanation_y + j * 30 + offset), 
                            line, fill=glow_color, font=font_explanation)
                
                # Draw main text
                line_color = tuple(int(c * line_alpha * explanation_alpha) for c in self.explanation_color)
                draw.text((line_x, explanation_y + j * 30), line, fill=line_color, font=font_explanation)
        
        # Add animated border with glow
        border_alpha = min(1.0, time / 1.0)
        border_glow = int(50 * border_alpha * (0.5 + 0.5 * math.sin(time * 2)))
        
        # Draw border glow
        for offset in range(1, 4):
            glow_color = (100, 150, 255, border_glow // offset)
            draw.rectangle([40 + offset, 250 + offset, self.width - 40 + offset, 
                          code_start_y + max_lines * line_height + 40 + offset], 
                         outline=glow_color, width=2)
        
        # Draw main border
        border_color = tuple(int(c * border_alpha) for c in (100, 150, 255))
        draw.rectangle([40, 250, self.width - 40, code_start_y + max_lines * line_height + 40], 
                      outline=border_color, width=2)
        
        # Add subtitle overlay if available
        if subtitle_overlay and subtitle_segments:
            for segment in subtitle_segments:
                # Create subtitle frame
                subtitle_img = subtitle_overlay.create_subtitle_frame(
                    segment, self.width, self.height, time
                )
                if subtitle_img:
                    img = Image.alpha_composite(img.convert('RGBA'), subtitle_img)
                
                # Create emoji overlay
                emoji_img = subtitle_overlay.create_emoji_overlay(
                    segment, self.width, self.height, time
                )
                if emoji_img:
                    img = Image.alpha_composite(img.convert('RGBA'), emoji_img)
        
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
    
    def _create_video_from_frames(self, frames_dir: str, audio_path: str, output_path: str, duration: float, frame_interval: float):
        """Create video from frames and audio using ffmpeg with high quality."""
        try:
            print("🎥 Creating premium video...")
            
            # Create video from frames with high quality
            temp_video = "temp_video.mp4"
            subprocess.run([
                'ffmpeg', '-y',
                '-framerate', str(self.fps),
                '-i', os.path.join(frames_dir, 'frame_%06d.png'),
                '-c:v', 'libx264',
                '-pix_fmt', 'yuv420p',
                '-crf', '18',  # High quality
                '-preset', 'slow',  # Better compression
                temp_video
            ], check=True)
            
            # Combine video with audio
            print("🔊 Adding audio to video...")
            subprocess.run([
                'ffmpeg', '-y',
                '-i', temp_video,
                '-i', audio_path,
                '-c:v', 'copy',
                '-c:a', 'aac',
                '-b:a', '192k',  # High quality audio
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
    """Test the premium animated video renderer."""
    if not PIL_AVAILABLE:
        print("PIL not available. Install with: pip install pillow")
        return
    
    renderer = PremiumAnimatedVideoRenderer()
    
    # Test code
    test_code = """
def calculate_factorial(n):
    # This function calculates the factorial of a number
    if n <= 1:
        return 1
    else:
        result = n * calculate_factorial(n - 1)
        return result

# Test the function
number = 5
answer = calculate_factorial(number)
print(f"The factorial of {number} is {answer}")
"""
    
    # Test explanation
    explanation = {
        'title': 'Premium Code Explanation',
        'overview': 'This code demonstrates recursion with a factorial function.',
        'key_takeaways': ['Recursion', 'Base case', 'Mathematical concept']
    }
    
    # Create animated video
    try:
        output_path = renderer.create_animated_video(
            code=test_code,
            audio_path="test_audio.wav",  # You'll need to create this
            explanation=explanation,
            output_path="test_premium.mp4"
        )
        print(f"Premium video created: {output_path}")
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 