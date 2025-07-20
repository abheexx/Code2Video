#!/usr/bin/env python3

"""
Subtitle and Emoji Overlay System for Code2Vid
Enhances videos with synchronized subtitles and emoji overlays.
"""

import os
import json
import math
import re
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import subprocess

try:
    from PIL import Image, ImageDraw, ImageFont
    PIL_AVAILABLE = True
except ImportError:
    PIL_AVAILABLE = False


class SubtitleOverlay:
    """Handles subtitle generation and emoji overlays."""
    
    def __init__(self):
        """Initialize the subtitle overlay system."""
        # Keyword to emoji mapping
        self.keyword_emoji_map = {
            # Programming concepts
            'function': '⚙️',
            'def': '⚙️',
            'return': '↩️',
            'if': '❓',
            'else': '🔄',
            'for': '🔄',
            'while': '🔄',
            'loop': '🔄',
            'array': '📊',
            'list': '📋',
            'dictionary': '📚',
            'variable': '📝',
            'print': '🖨️',
            'input': '⌨️',
            'output': '📤',
            'swap': '🔄',
            'sort': '📊',
            'search': '🔍',
            'find': '🔍',
            'calculate': '🧮',
            'compute': '💻',
            'algorithm': '🧠',
            'recursion': '🔄',
            'iteration': '🔄',
            'condition': '❓',
            'boolean': '✅',
            'true': '✅',
            'false': '❌',
            'null': '🚫',
            'error': '⚠️',
            'exception': '🚨',
            'try': '🛡️',
            'catch': '🎯',
            'finally': '🏁',
            
            # Mathematical concepts
            'add': '➕',
            'subtract': '➖',
            'multiply': '✖️',
            'divide': '➗',
            'sum': '📊',
            'total': '📊',
            'count': '🔢',
            'number': '🔢',
            'value': '💎',
            'result': '🎯',
            'answer': '💡',
            'solution': '💡',
            'formula': '📐',
            'equation': '📐',
            'math': '🧮',
            'calculate': '🧮',
            'factorial': '🔢',
            'fibonacci': '🐚',
            'prime': '🔢',
            'even': '🔢',
            'odd': '🔢',
            
            # Data structures
            'stack': '📚',
            'queue': '📋',
            'tree': '🌳',
            'graph': '🕸️',
            'node': '🔗',
            'pointer': '👆',
            'reference': '🔗',
            'object': '📦',
            'class': '🏗️',
            'method': '⚙️',
            'property': '📋',
            'attribute': '🏷️',
            
            # Actions and processes
            'create': '✨',
            'build': '🏗️',
            'construct': '🔨',
            'initialize': '🚀',
            'setup': '⚙️',
            'configure': '🔧',
            'process': '⚙️',
            'execute': '▶️',
            'run': '🏃',
            'start': '🚀',
            'stop': '⏹️',
            'pause': '⏸️',
            'continue': '▶️',
            'finish': '🏁',
            'complete': '✅',
            'done': '✅',
            'success': '🎉',
            'fail': '💥',
            'break': '💔',
            'continue': '🔄',
            
            # Common words
            'now': '⏰',
            'next': '➡️',
            'then': '➡️',
            'first': '1️⃣',
            'second': '2️⃣',
            'third': '3️⃣',
            'last': '🔚',
            'begin': '🚀',
            'end': '🏁',
            'check': '✅',
            'verify': '🔍',
            'test': '🧪',
            'debug': '🐛',
            'fix': '🔧',
            'solve': '💡',
            'understand': '🧠',
            'learn': '📚',
            'explain': '💬',
            'show': '👁️',
            'display': '📺',
            'see': '👁️',
            'look': '👁️',
            'watch': '👁️',
            'observe': '👁️',
            'notice': '👁️',
            'remember': '🧠',
            'forget': '🧠',
            'think': '🤔',
            'know': '💡',
            'guess': '🤔',
            'assume': '🤔',
            'suppose': '🤔',
            'imagine': '🤔',
            'consider': '🤔',
            'decide': '🤔',
            'choose': '🤔',
            'select': '🤔',
            'pick': '🤔',
            'want': '💭',
            'need': '💭',
            'must': '💭',
            'should': '💭',
            'could': '💭',
            'would': '💭',
            'can': '💭',
            'will': '💭',
            'may': '💭',
            'might': '💭',
            'shall': '💭',
        }
        
        # Emoji overlay positions and animations
        self.emoji_positions = [
            (100, 100), (200, 150), (300, 200), (400, 250),
            (500, 300), (600, 350), (700, 400), (800, 450),
            (900, 500), (1000, 550), (1100, 600), (1200, 650)
        ]
        self.current_position = 0
    
    def process_narration(self, narration_text: str) -> List[Dict[str, Any]]:
        """
        Process narration text and add emojis based on keywords.
        
        Args:
            narration_text: The narration text to process
            
        Returns:
            List of subtitle segments with emojis and timing
        """
        # Split narration into sentences
        sentences = re.split(r'[.!?]+', narration_text)
        sentences = [s.strip() for s in sentences if s.strip()]
        
        subtitle_segments = []
        current_time = 0.0
        
        for sentence in sentences:
            # Add emojis to the sentence
            enhanced_sentence = self._add_emojis_to_sentence(sentence)
            
            # Estimate duration (roughly 2.5 words per second)
            word_count = len(sentence.split())
            duration = max(1.0, word_count / 2.5)
            
            # Find keywords for emoji overlays
            keywords = self._find_keywords(sentence)
            
            subtitle_segments.append({
                'text': enhanced_sentence,
                'original_text': sentence,
                'start_time': current_time,
                'duration': duration,
                'end_time': current_time + duration,
                'keywords': keywords,
                'emojis': [self.keyword_emoji_map.get(kw.lower(), '') for kw in keywords]
            })
            
            current_time += duration
        
        return subtitle_segments
    
    def _add_emojis_to_sentence(self, sentence: str) -> str:
        """Add emojis to a sentence based on keywords."""
        words = sentence.split()
        enhanced_words = []
        
        for word in words:
            # Clean the word (remove punctuation)
            clean_word = re.sub(r'[^\w]', '', word.lower())
            
            if clean_word in self.keyword_emoji_map:
                emoji = self.keyword_emoji_map[clean_word]
                enhanced_words.append(f"{word} {emoji}")
            else:
                enhanced_words.append(word)
        
        return ' '.join(enhanced_words)
    
    def _find_keywords(self, sentence: str) -> List[str]:
        """Find keywords in a sentence for emoji overlays."""
        words = sentence.split()
        keywords = []
        
        for word in words:
            clean_word = re.sub(r'[^\w]', '', word.lower())
            if clean_word in self.keyword_emoji_map:
                keywords.append(clean_word)
        
        return keywords
    
    def create_subtitle_frame(self, subtitle_segment: Dict[str, Any], 
                            width: int, height: int, time: float) -> Optional[Image.Image]:
        """
        Create a subtitle frame for a given time.
        
        Args:
            subtitle_segment: The subtitle segment data
            width: Frame width
            height: Frame height
            time: Current time in video
            
        Returns:
            PIL Image with subtitle overlay, or None if not needed
        """
        if not PIL_AVAILABLE:
            return None
        
        # Check if we should show this subtitle
        if not (subtitle_segment['start_time'] <= time <= subtitle_segment['end_time']):
            return None
        
        # Calculate fade-in/fade-out
        fade_duration = 0.3
        time_in_segment = time - subtitle_segment['start_time']
        
        if time_in_segment < fade_duration:
            alpha = time_in_segment / fade_duration
        elif time_in_segment > subtitle_segment['duration'] - fade_duration:
            alpha = (subtitle_segment['duration'] - time_in_segment) / fade_duration
        else:
            alpha = 1.0
        
        # Create subtitle image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 32)
        except:
            font = ImageFont.load_default()
        
        # Wrap text
        text = subtitle_segment['text']
        words = text.split()
        lines = []
        current_line = ""
        
        for word in words:
            test_line = current_line + " " + word if current_line else word
            bbox = draw.textbbox((0, 0), test_line, font=font)
            if bbox[2] - bbox[0] < width - 100:
                current_line = test_line
            else:
                if current_line:
                    lines.append(current_line)
                current_line = word
        if current_line:
            lines.append(current_line)
        
        # Draw subtitle background
        subtitle_y = height - 150
        line_height = 40
        
        for i, line in enumerate(lines):
            bbox = draw.textbbox((0, 0), line, font=font)
            line_width = bbox[2] - bbox[0]
            line_x = (width - line_width) // 2
            
            # Draw background rectangle
            bg_rect = [
                line_x - 20, subtitle_y + i * line_height - 10,
                line_x + line_width + 20, subtitle_y + i * line_height + 30
            ]
            bg_color = (0, 0, 0, int(180 * alpha))
            draw.rectangle(bg_rect, fill=bg_color)
            
            # Draw text
            text_color = (255, 255, 255, int(255 * alpha))
            draw.text((line_x, subtitle_y + i * line_height), line, fill=text_color, font=font)
        
        return img
    
    def create_emoji_overlay(self, subtitle_segment: Dict[str, Any], 
                           width: int, height: int, time: float) -> Optional[Image.Image]:
        """
        Create emoji overlay for a given time.
        
        Args:
            subtitle_segment: The subtitle segment data
            width: Frame width
            height: Frame height
            time: Current time in video
            
        Returns:
            PIL Image with emoji overlay, or None if not needed
        """
        if not PIL_AVAILABLE:
            return None
        
        # Check if we should show emoji overlays
        if not (subtitle_segment['start_time'] <= time <= subtitle_segment['end_time']):
            return None
        
        # Calculate animation timing
        time_in_segment = time - subtitle_segment['start_time']
        animation_duration = 1.0
        
        if time_in_segment > animation_duration:
            return None
        
        # Create emoji overlay image
        img = Image.new('RGBA', (width, height), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 48)
        except:
            font = ImageFont.load_default()
        
        # Animate emojis
        for i, emoji in enumerate(subtitle_segment['emojis']):
            if not emoji:
                continue
            
            # Calculate position and animation
            base_x, base_y = self.emoji_positions[(self.current_position + i) % len(self.emoji_positions)]
            
            # Bounce animation
            bounce = math.sin(time_in_segment * 8) * 10
            scale = 0.5 + 0.5 * math.sin(time_in_segment * 4)
            
            # Calculate alpha (fade in)
            alpha = min(1.0, time_in_segment / 0.3)
            
            # Draw emoji with effects
            emoji_x = int(base_x * scale)
            emoji_y = int(base_y + bounce)
            
            # Draw glow effect
            glow_alpha = int(50 * alpha)
            for offset in range(1, 4):
                glow_color = (255, 255, 255, glow_alpha // offset)
                draw.text((emoji_x + offset, emoji_y + offset), emoji, fill=glow_color, font=font)
            
            # Draw main emoji
            emoji_color = (255, 255, 255, int(255 * alpha))
            draw.text((emoji_x, emoji_y), emoji, fill=emoji_color, font=font)
        
        return img
    
    def get_next_position(self):
        """Get next emoji position."""
        self.current_position = (self.current_position + 1) % len(self.emoji_positions)
        return self.current_position


def main():
    """Test the subtitle overlay system."""
    overlay = SubtitleOverlay()
    
    # Test narration
    test_narration = """
    Now we create a function to calculate the factorial. 
    First, we check if the number is less than or equal to one. 
    If it is, we return one as the base case. 
    Otherwise, we multiply the number by the factorial of n minus one. 
    This is a recursive algorithm that calls itself until it reaches the base case.
    """
    
    # Process narration
    segments = overlay.process_narration(test_narration)
    
    print("📝 Processed Subtitle Segments:")
    print("=" * 50)
    
    for i, segment in enumerate(segments):
        print(f"\nSegment {i+1}:")
        print(f"Text: {segment['text']}")
        print(f"Keywords: {segment['keywords']}")
        print(f"Emojis: {segment['emojis']}")
        print(f"Timing: {segment['start_time']:.1f}s - {segment['end_time']:.1f}s")
        print("-" * 30)


if __name__ == "__main__":
    main() 