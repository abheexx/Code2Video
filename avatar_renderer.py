"""
Avatar Video Renderer - Animated avatar with speech bubble
Creates engaging videos with an animated avatar that explains code in a speech bubble.
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
from PIL import Image, ImageDraw, ImageFont
from io import BytesIO

class AvatarVideoRenderer:
    """Video renderer with animated avatar and speech bubble."""
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        
        # Avatar settings - moved left for better layout
        self.avatar_size = 140
        self.avatar_x = 50  # Further left to make room for speech bubble
        self.avatar_y = 170  # Slightly lower for better alignment
        
        # Speech bubble settings
        self.bubble_padding = 20
        self.bubble_margin = 30
        
        # Emojis for avatar expressions
        self.avatar_expressions = {
            'happy': '😊',
            'thinking': '🤔',
            'explaining': '💬',
            'excited': '😄',
            'surprised': '😲',
            'confident': '😎'
        }
        
        # Code explanation phrases
        self.explanation_phrases = [
            "Let me explain this code step by step!",
            "Here's what's happening in this function:",
            "This is a really interesting piece of code!",
            "Let's break down what this does:",
            "I'll walk you through this logic:",
            "This is how the algorithm works:",
            "Let me show you the key parts:",
            "Here's the breakdown of this code:"
        ]
        
    def create_animated_video(self, code: str, audio_path: str, explanation: Dict[str, Any],
                            output_path: str = "avatar_video.mp4", narration_text: str = None) -> str:
        """Create a video with animated avatar and speech bubble."""
        
        # Get audio duration
        duration = self._get_audio_duration(audio_path)
        
        # Use narration text from explanation if not provided
        if not narration_text:
            narration_text = explanation.get('narration_script', '')
        
        # Calculate frame count
        total_frames = min(60, int(duration * self.fps))
        frame_duration = duration / total_frames
        
        # Create frames with avatar and speech bubble
        frames = self._create_avatar_frames(code, explanation, total_frames, duration, narration_text)
        
        # Apply semantic animations
        try:
            from semantic_animator import SemanticAnimator
            animator = SemanticAnimator(self.width, self.height, self.fps)
            triggers = animator.analyze_narration(narration_text, duration)
            
            # Apply animations to each frame
            for i, frame in enumerate(frames):
                time = i * frame_duration
                frame = animator.apply_animations_to_frame(frame, triggers, time)
                frames[i] = frame
                
        except Exception as e:
            print(f"Semantic animations failed: {e}")
        
        # Save frames with compression
        frame_dir = tempfile.mkdtemp()
        frame_paths = []
        
        for i, frame in enumerate(frames):
            frame_path = os.path.join(frame_dir, f"frame_{i:03d}.jpg")
            frame.save(frame_path, 'JPEG', quality=70, optimize=True)
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
            return 10.0
    
    def _create_avatar_frames(self, code: str, explanation: Dict[str, Any], 
                            total_frames: int, duration: float, narration_text: str = None) -> List[Image.Image]:
        """Create frames with animated avatar and speech bubble."""
        frames = []
        
        # Split narration into segments for speech bubble
        speech_segments = self._split_narration_into_segments(narration_text, duration)
        
        for i in range(total_frames):
            progress = i / (total_frames - 1)
            time = progress * duration
            
            # Create frame with avatar and speech bubble
            frame = self._create_avatar_frame(code, explanation, progress, time, speech_segments)
            frames.append(frame)
        
        return frames
    
    def _split_narration_into_segments(self, narration_text: str, duration: float) -> List[Dict[str, Any]]:
        """Split narration text into timed segments for speech bubble with better audio sync."""
        if not narration_text:
            # Generate default segments based on explanation
            segments = [
                {"text": "Hi! I'm your AI assistant! 👋", "start": 0, "duration": 2},
                {"text": "Let me explain this code step by step! 💻", "start": 2, "duration": 2},
                {"text": "This is really interesting code! 🤔", "start": 4, "duration": 2},
                {"text": "Let me break it down for you! ✨", "start": 6, "duration": 2},
                {"text": "That's how it works! 🎉", "start": 8, "duration": 2}
            ]
        else:
            # Much better segmentation for audio sync
            words = narration_text.split()
            total_words = len(words)
            
            # Create smaller, more frequent segments for better sync
            # Estimate words per second (average speaking rate is ~150 words per minute)
            words_per_second = 2.5  # Conservative estimate
            estimated_duration = total_words / words_per_second
            
            # Adjust if estimated duration is very different from actual
            if abs(estimated_duration - duration) > 2:
                words_per_second = total_words / duration
            
            # Create segments every 1-1.5 seconds for better sync
            segment_duration = 1.2  # seconds per segment
            words_per_segment = max(2, int(words_per_second * segment_duration))
            
            segments = []
            current_time = 0
            
            for i in range(0, total_words, words_per_segment):
                segment_words = words[i:i + words_per_segment]
                segment_text = " ".join(segment_words)
                
                # Calculate actual timing based on word count and speaking rate
                segment_word_count = len(segment_words)
                actual_duration = segment_word_count / words_per_second
                
                segments.append({
                    "text": segment_text,
                    "start": current_time,
                    "duration": actual_duration
                })
                
                current_time += actual_duration
                
                # Stop if we've exceeded the audio duration
                if current_time >= duration:
                    break
            
            # Adjust the last segment to fit exactly within duration
            if segments and segments[-1]['start'] + segments[-1]['duration'] > duration:
                segments[-1]['duration'] = duration - segments[-1]['start']
        
        return segments
    
    def _create_avatar_frame(self, code: str, explanation: Dict[str, Any], 
                           progress: float, time: float, speech_segments: List[Dict[str, Any]]) -> Image.Image:
        """Create a single frame with avatar and speech bubble."""
        # Use consistent light background color
        img = Image.new('RGB', (self.width, self.height), color=(240, 240, 240))
        draw = ImageDraw.Draw(img)
        
        # Draw background
        self._draw_background(draw, progress, time)
        
        # Draw code area
        self._draw_code_area(draw, code, progress, time, speech_segments)
        
        # Draw avatar
        self._draw_avatar(draw, progress, time)
        
        # Draw karaoke-style text (no bubble box)
        self._draw_karaoke_text(draw, speech_segments, time)
        
        # Draw title
        self._draw_title(draw, explanation, progress, time)
        
        return img
    
    def _draw_background(self, draw: ImageDraw.Draw, progress: float, time: float):
        """Draw animated background."""
        # Use consistent light background - no gradient
        for y in range(0, self.height, 3):
            color = 245  # Consistent light gray
            draw.line([(0, y), (self.width, y)], fill=(color, color, color))
    
    def _draw_code_area(self, draw: ImageDraw.Draw, code: str, progress: float, time: float, speech_segments: List[Dict[str, Any]] = None):
        """Draw code area on the right side with proper text wrapping."""
        code_x = self.width // 2 + 30
        code_y = 100
        code_width = self.width - code_x - 30
        code_height = self.height - 150
        
        # Code background with light background for better contrast
        draw.rectangle([code_x, code_y, code_x + code_width, code_y + code_height], 
                      fill=(240, 240, 240), outline=(100, 100, 100), width=2)  # Light background for dark text
        
        # Code title - more interesting fonts
        try:
            # Try modern fonts first
            font_small = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 20)
            font_code = ImageFont.truetype("/System/Library/Fonts/Menlo.ttc", 18)
        except:
            try:
                # Fallback to other fonts
                font_small = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 20)
                font_code = ImageFont.truetype("/System/Library/Fonts/Courier.ttc", 18)
            except:
                font_small = ImageFont.load_default()
                font_code = ImageFont.load_default()
        
        draw.text((code_x + 10, code_y + 10), "📝 Code:", fill=(50, 50, 50), font=font_small)  # Dark title on light background
        
        # Code lines - appear one at a time synchronized with audio
        lines = code.strip().split('\n')
        y_pos = code_y + 40
        
        # Smart line timing based on speech segments
        if speech_segments and len(speech_segments) > 0:
            # Find current speech segment
            current_segment_index = 0
            for i, segment in enumerate(speech_segments):
                if segment['start'] <= time <= segment['start'] + segment['duration']:
                    current_segment_index = i
                    break
            
            # Show lines based on speech progress
            total_segments = len(speech_segments)
            lines_per_segment = max(1, len(lines) // total_segments)
            total_lines_to_show = min(len(lines), (current_segment_index + 1) * lines_per_segment)
        else:
            # Fallback: show one line every 1.5 seconds
            lines_per_second = 0.67  # One line every 1.5 seconds
            total_lines_to_show = min(len(lines), int(time * lines_per_second) + 1)
        
        for i, line in enumerate(lines[:12]):
            # Only show lines that should appear by current time
            if i < total_lines_to_show:
                # Line number with better contrast
                line_num = f"{i+1:2d} "
                draw.text((code_x + 10, y_pos), line_num, fill=(100, 100, 100), font=font_code)
                
                # Code line with proper wrapping to fit in box
                max_code_width = code_width - 80  # Leave space for line numbers and margins
                wrapped_line = self._wrap_code_line(line, font_code, max_code_width)
                
                line_x = code_x + 10 + len(line_num) * 8
                for wrapped_part in wrapped_line:
                    draw.text((line_x, y_pos), wrapped_part, fill=(20, 20, 20), font=font_code)
                    y_pos += 20  # Smaller spacing for wrapped lines
                
                y_pos += 5  # Extra space between logical lines
            else:
                y_pos += 25  # Keep spacing for lines not yet shown
    
    def _wrap_code_line(self, line: str, font, max_width: int) -> List[str]:
        """Wrap a code line to fit within specified width."""
        words = line.split(' ')
        wrapped_lines = []
        current_line = ""
        
        for word in words:
            # Test if adding this word would exceed width
            test_line = current_line + (" " if current_line else "") + word
            bbox = ImageDraw.Draw(Image.new('RGB', (1, 1))).textbbox((0, 0), test_line, font=font)
            test_width = bbox[2] - bbox[0]
            
            if test_width <= max_width:
                current_line = test_line
            else:
                # If current line has content, add it and start new line
                if current_line:
                    wrapped_lines.append(current_line)
                    current_line = word
                else:
                    # Word itself is too long, force break
                    wrapped_lines.append(word)
                    current_line = ""
        
        # Add remaining line
        if current_line:
            wrapped_lines.append(current_line)
        
        return wrapped_lines if wrapped_lines else [line]

    def _draw_avatar(self, draw: ImageDraw.Draw, progress: float, time: float):
        """Draw animated avatar."""
        # Avatar center position
        avatar_center_x = self.avatar_x + self.avatar_size // 2
        avatar_center_y = self.avatar_y + self.avatar_size // 2
        
        # Static avatar position (no floating)
        avatar_y = self.avatar_y
        
        # Try to load custom avatar image
        avatar_img = self._load_avatar_image()
        
        if avatar_img:
            # Use custom avatar image
            # Resize image to fit avatar size
            avatar_img = avatar_img.resize((self.avatar_size, self.avatar_size), Image.Resampling.LANCZOS)
            
            # Create circular mask
            mask = Image.new('L', (self.avatar_size, self.avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, self.avatar_size, self.avatar_size], fill=255)
            
            # Apply mask to create circular avatar
            avatar_img.putalpha(mask)
            
            # Paste avatar onto main image
            img = draw._image
            img.paste(avatar_img, (self.avatar_x, int(avatar_y)), avatar_img)
            
            # Add subtle border
            draw.ellipse([self.avatar_x, avatar_y, 
                         self.avatar_x + self.avatar_size, avatar_y + self.avatar_size], 
                        outline=(255, 255, 255), width=3)
        else:
            # Fallback to emoji avatar - more interesting font
            try:
                # Try modern fonts for emoji
                font_avatar = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 80)
            except:
                try:
                    # Fallback to other fonts
                    font_avatar = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 80)
                except:
                    font_avatar = ImageFont.load_default()
            
            # Avatar circle
            draw.ellipse([self.avatar_x, avatar_y, 
                         self.avatar_x + self.avatar_size, avatar_y + self.avatar_size], 
                        fill=(100, 150, 255), outline=(255, 255, 255), width=3)
            
            # Avatar expression (changes based on time)
            if time < 2:
                expression = self.avatar_expressions['happy']
            elif time < 4:
                expression = self.avatar_expressions['explaining']
            elif time < 6:
                expression = self.avatar_expressions['thinking']
            elif time < 8:
                expression = self.avatar_expressions['excited']
            else:
                expression = self.avatar_expressions['confident']
            
            # Draw avatar emoji
            bbox = draw.textbbox((0, 0), expression, font=font_avatar)
            emoji_width = bbox[2] - bbox[0]
            emoji_height = bbox[3] - bbox[1]
            
            emoji_x = avatar_center_x - emoji_width // 2
            emoji_y = avatar_center_y - emoji_height // 2
            
            draw.text((emoji_x, emoji_y), expression, fill=(255, 255, 255), font=font_avatar)
        
        # Avatar name - more interesting font and dark color
        try:
            # Try modern fonts for avatar name
            font_name = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 16)
        except:
            try:
                # Fallback to other fonts
                font_name = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
            except:
                font_name = ImageFont.load_default()
        
        name = "AI Assistant"
        name_bbox = draw.textbbox((0, 0), name, font=font_name)
        name_width = name_bbox[2] - name_bbox[0]
        name_x = avatar_center_x - name_width // 2
        name_y = avatar_y + self.avatar_size + 10
        
        # Dark color for better visibility on light background
        draw.text((name_x, name_y), name, fill=(50, 50, 50), font=font_name)
    
    def _draw_karaoke_text(self, draw: ImageDraw.Draw, speech_segments: List[Dict[str, Any]], time: float):
        """Draw karaoke-style text with 3 lines, typewriter effect, and current word highlighting."""
        # Find current speech segment
        current_segment = None
        for segment in speech_segments:
            if segment['start'] <= time <= segment['start'] + segment['duration']:
                current_segment = segment
                break
        
        if not current_segment:
            current_segment = {"text": "Hello! I'm here to help! 👋", "start": 0, "duration": 1}
        
        # Speech bubble position - beside avatar like reading
        bubble_width = 380
        bubble_height = 120
        code_area_start = self.width // 2 + 30  # Where code area starts
        
        # Position bubble to the right of avatar (like reading direction)
        bubble_x = self.avatar_x + self.avatar_size + 20  # Right of avatar
        bubble_y = self.avatar_y + 10  # Aligned with avatar's upper area
        
        # Ensure bubble doesn't interfere with code area
        if bubble_x + bubble_width > code_area_start - 20:
            bubble_width = code_area_start - bubble_x - 20  # Adjust width to fit
            if bubble_width < 300:  # If too narrow, place below instead
                bubble_x = self.avatar_x - 20
                bubble_y = self.avatar_y + self.avatar_size + 20
                bubble_width = 380
        
        # Draw speech bubble background
        self._draw_speech_bubble(draw, bubble_x, bubble_y, bubble_width, bubble_height, self.avatar_x + self.avatar_size//2)
        
        # Text position inside the bubble
        text_x = bubble_x + 20  # Margin inside bubble
        text_y = bubble_y + 20  # Margin inside bubble
        
        # Font for karaoke text - larger size for better visibility
        try:
            font_karaoke = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 24)
        except:
            try:
                font_karaoke = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
            except:
                font_karaoke = ImageFont.load_default()
        
        # Collect words from 4 segments (current + next 3) for 4 lines
        all_words = []
        current_segment_index = 0
        
        # Find current segment index
        for i, segment in enumerate(speech_segments):
            if segment['start'] <= time <= segment['start'] + segment['duration']:
                current_segment_index = i
                break
        
        # Add current and next 3 segments for 4 lines
        for i in range(4):
            if current_segment_index + i < len(speech_segments):
                segment = speech_segments[current_segment_index + i]
                all_words.extend(segment['text'].split())
        
        # Simple, slow word progression based on total time
        # Each word stays visible for a fixed duration regardless of segments
        word_duration = 4.5  # 4.5 seconds per word for ultra slow, readable pace
        current_word_position = int(time / word_duration)
        
        # Ensure we don't exceed available words
        current_word_position = max(0, min(current_word_position, len(all_words) - 1))
        
        # Debug output for timing verification
        print(f"Time: {time:.1f}s, Word Duration: {word_duration}s, Current Word: {current_word_position}/{len(all_words)}")
        
        # Typewriter effect: show all words but highlight current one
        words_to_show = len(all_words)  # Show all words for typewriter effect
        
        # Draw 4 lines with typewriter and karaoke effect
        current_x = text_x
        current_y = text_y
        max_width = bubble_width - 40  # Fit inside bubble with margins
        
        line_words = []
        line_x = current_x
        line_count = 0
        word_index = 0
        
        for i, word in enumerate(all_words):
            # Show all words for typewriter effect
                
            # Test if word fits on current line
            test_line = " ".join(line_words + [word])
            bbox = draw.textbbox((0, 0), test_line, font=font_karaoke)
            line_width = bbox[2] - bbox[0]
            
            if line_width > max_width and line_words:
                # Draw current line with karaoke highlighting
                self._draw_karaoke_line_v2(draw, line_words, line_x, current_y, word_index, current_word_position, font_karaoke)
                
                # Start new line
                line_words = [word]
                current_y += 32  # Increased line spacing for larger font (24px)
                line_x = text_x
                line_count += 1
                word_index += len(line_words) - 1
                
                # Only show 4 lines
                if line_count >= 4:
                    break
            else:
                line_words.append(word)
        
        # Draw the last line if we haven't reached 4 lines
        if line_words and line_count < 4:
            self._draw_karaoke_line_v2(draw, line_words, line_x, current_y, word_index, current_word_position, font_karaoke)
    
    def _draw_speech_bubble(self, draw: ImageDraw.Draw, x: int, y: int, width: int, height: int, avatar_center_x: int):
        """Draw a speech bubble background with tail pointing to avatar."""
        # Main bubble rectangle with rounded corners
        bubble_color = (255, 255, 255, 240)  # White with more opacity
        border_color = (80, 80, 80)  # Darker border for better definition
        
        # Draw main bubble body
        draw.rounded_rectangle([x, y, x + width, y + height], 
                              radius=12, fill=bubble_color, outline=border_color, width=2)
        
        # Draw speech bubble tail pointing to avatar
        # Determine tail direction based on bubble position
        if x > avatar_center_x:  # Bubble is to the right of avatar
            # Tail points left to avatar (reading direction)
            tail_y = y + height//2  # Middle of bubble height
            tail_points = [
                (x, tail_y - 12),           # Top of tail base
                (x - 15, tail_y),           # Point toward avatar
                (x, tail_y + 12)            # Bottom of tail base
            ]
        else:  # Bubble is below avatar (fallback position)
            # Tail points upward to avatar
            tail_center_x = avatar_center_x
            if tail_center_x < x + 20:
                tail_center_x = x + 20
            elif tail_center_x > x + width - 20:
                tail_center_x = x + width - 20
            
            tail_points = [
                (tail_center_x - 15, y),    # Left side of tail base
                (tail_center_x, y - 15),    # Point toward avatar (upward)
                (tail_center_x + 15, y)     # Right side of tail base
            ]
        
        draw.polygon(tail_points, fill=bubble_color, outline=border_color)

    def _draw_karaoke_line_v2(self, draw: ImageDraw.Draw, words: List[str], x: int, y: int, 
                             start_word_index: int, current_word_position: int, font):
        """Draw a line of text with true karaoke highlighting - only current word is bold."""
        current_x = x
        
        for i, word in enumerate(words):
            word_index = start_word_index + i
            
            # Only the current word being spoken is bold
            if word_index == current_word_position:
                # Current word - bold and dark for contrast against white bubble
                try:
                    bold_font = ImageFont.truetype("/System/Library/Fonts/Helvetica-Bold.ttc", 24)
                except:
                    try:
                        bold_font = ImageFont.truetype("/System/Library/Fonts/Arial-Bold.ttf", 24)
                    except:
                        bold_font = font  # Fallback to normal font
                
                color = (0, 0, 0)  # Pure black for maximum contrast
                draw.text((current_x, y), word, fill=color, font=bold_font)
            elif word_index < current_word_position:
                # Previously spoken words - normal font, dark color for contrast
                color = (40, 40, 40)  # Dark color for good contrast against white
                draw.text((current_x, y), word, fill=color, font=font)
            else:
                # Future words - normal font, medium gray for contrast
                color = (120, 120, 120)  # Medium gray for better visibility on white
                draw.text((current_x, y), word, fill=color, font=font)
            
            # Move to next word position
            bbox = draw.textbbox((0, 0), word, font=font)
            word_width = bbox[2] - bbox[0]
            current_x += word_width + 5  # 5px space between words
    
    def _draw_title(self, draw: ImageDraw.Draw, explanation: Dict[str, Any], progress: float, time: float):
        """Draw animated title."""
        try:
            # Try modern fonts for title
            font_title = ImageFont.truetype("/System/Library/Fonts/Helvetica.ttc", 36)
        except:
            try:
                # Fallback to other fonts
                font_title = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 36)
            except:
                font_title = ImageFont.load_default()
        
        title = explanation.get('title', 'Code Explanation with AI Assistant')
        
        # Static title position
        title_y = 30
        
        bbox = draw.textbbox((0, 0), title, font=font_title)
        title_width = bbox[2] - bbox[0]
        title_x = (self.width - title_width) // 2
        
        # Main title with consistent dark color for light background - no shadow
        draw.text((title_x, title_y), title, fill=(50, 50, 50), font=font_title)
    
    def _load_avatar_image(self) -> Optional[Image.Image]:
        """Load custom avatar image from various sources."""
        try:
            # Try to load from local file first
            avatar_paths = [
                "avatar_small.png",  # Prefer the small version for video
                "avatar.png",
                "avatar.jpg", 
                "avatar.jpeg",
                "custom_avatar.png",
                "ai_avatar.png"
            ]
            
            for path in avatar_paths:
                if os.path.exists(path):
                    img = Image.open(path)
                    # Remove background if it's a PNG with transparency
                    if img.mode == 'RGBA':
                        return img
                    else:
                        # Convert to RGBA
                        return img.convert('RGBA')
            
            # Try to download from URL if provided
            avatar_url = os.getenv('AVATAR_URL')
            if avatar_url:
                import requests
                response = requests.get(avatar_url, timeout=10)
                if response.status_code == 200:
                    img = Image.open(BytesIO(response.content))
                    if img.mode == 'RGBA':
                        return img
                    else:
                        return img.convert('RGBA')
            
            return None
            
        except Exception as e:
            print(f"Could not load avatar image: {e}")
            return None
    
    def _create_video_from_frames(self, frame_paths: List[str], audio_path: str, 
                                output_path: str, duration: float, frame_duration: float):
        """Create video from frames using ffmpeg."""
        
        # Create frame list file
        frame_list = tempfile.NamedTemporaryFile(mode='w', suffix='.txt', delete=False)
        for frame_path in frame_paths:
            frame_list.write(f"file '{frame_path}'\n")
            frame_list.write(f"duration {frame_duration}\n")
        frame_list.close()
        
        # Use ffmpeg with compression
        cmd = [
            'ffmpeg', '-y',
            '-f', 'concat',
            '-safe', '0',
            '-i', frame_list.name,
            '-i', audio_path,
            '-c:v', 'libx264',
            '-preset', 'ultrafast',
            '-crf', '28',
            '-c:a', 'aac',
            '-b:a', '128k',
            '-pix_fmt', 'yuv420p',
            '-shortest',
            output_path
        ]
        
        subprocess.run(cmd, check=True)
        
        # Cleanup
        os.unlink(frame_list.name)


def main():
    """Test the avatar renderer."""
    example_code = """
def fibonacci(n):
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

print(fibonacci(10))
"""
    
    example_explanation = {
        "title": "Fibonacci Function Explained",
        "overview": "A recursive function that calculates Fibonacci numbers efficiently",
        "key_takeaways": ["Recursion is powerful", "Base cases are important"]
    }
    
    example_narration = "Hi! I'm your AI assistant! Let me explain this Fibonacci function step by step. This is a recursive function that calls itself to calculate Fibonacci numbers. The base case is when n is 0 or 1, and then it recursively adds the previous two numbers. It's a beautiful example of recursion in action!"
    
    renderer = AvatarVideoRenderer()
    
    # Test with dummy audio
    silent_audio = "silent.wav"
    subprocess.run([
        'ffmpeg', '-y', '-f', 'lavfi', '-i', 'anullsrc=channel_layout=stereo:sample_rate=44100',
        '-t', '8', silent_audio
    ])
    
    output_path = renderer.create_animated_video(
        example_code, silent_audio, example_explanation, "avatar_test.mp4", example_narration
    )
    
    print(f"Avatar video created: {output_path}")
    
    # Cleanup
    os.remove(silent_audio)


if __name__ == "__main__":
    main() 