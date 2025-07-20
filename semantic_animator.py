"""
Semantic Animator - Auto-triggers relevant animations based on narration keywords
Builds intelligent animation overlay system that listens to narrated text and inserts matching animation clips.
"""

import os
import json
import re
import subprocess
import tempfile
from typing import Dict, Any, List, Optional, Tuple
from pathlib import Path
import numpy as np
from PIL import Image, ImageDraw, ImageFont
import math

class SemanticAnimator:
    """Intelligent animation overlay system based on narration keywords."""
    
    def __init__(self, width: int = 1280, height: int = 720, fps: int = 24):
        self.width = width
        self.height = height
        self.fps = fps
        
        # Animation settings
        self.animation_duration = 2.0  # Default animation duration
        self.animation_size = 200  # Size of animation overlays
        
        # Keyword-to-animation mapping
        self.animation_mappings = {
            # Programming concepts
            'function': {
                'keywords': ['function', 'def ', 'method', 'call', 'invoke'],
                'animation': 'function_call',
                'emoji': '🔧',
                'color': (255, 100, 100)
            },
            'loop': {
                'keywords': ['loop', 'for ', 'while ', 'iterate', 'repeat'],
                'animation': 'loop_spin',
                'emoji': '🔄',
                'color': (100, 255, 100)
            },
            'condition': {
                'keywords': ['if ', 'else', 'condition', 'check', 'compare'],
                'animation': 'condition_check',
                'emoji': '🤔',
                'color': (100, 100, 255)
            },
            'recursion': {
                'keywords': ['recursion', 'recursive', 'call itself', 'base case'],
                'animation': 'recursion_tree',
                'emoji': '🌳',
                'color': (255, 200, 100)
            },
            'array': {
                'keywords': ['array', 'list', 'element', 'index', 'position'],
                'animation': 'array_highlight',
                'emoji': '📊',
                'color': (200, 100, 255)
            },
            'swap': {
                'keywords': ['swap', 'exchange', 'switch', 'interchange'],
                'animation': 'swap_values',
                'emoji': '🔄',
                'color': (255, 150, 50)
            },
            'sort': {
                'keywords': ['sort', 'order', 'arrange', 'bubble', 'quick'],
                'animation': 'sort_animation',
                'emoji': '📈',
                'color': (100, 255, 200)
            },
            'search': {
                'keywords': ['search', 'find', 'lookup', 'binary', 'linear'],
                'animation': 'search_scan',
                'emoji': '🔍',
                'color': (255, 100, 200)
            },
            'stack': {
                'keywords': ['stack', 'push', 'pop', 'LIFO', 'last in'],
                'animation': 'stack_push_pop',
                'emoji': '📚',
                'color': (150, 255, 100)
            },
            'queue': {
                'keywords': ['queue', 'enqueue', 'dequeue', 'FIFO', 'first in'],
                'animation': 'queue_flow',
                'emoji': '🚶',
                'color': (100, 150, 255)
            },
            'pointer': {
                'keywords': ['pointer', 'reference', 'address', 'memory'],
                'animation': 'pointer_move',
                'emoji': '👆',
                'color': (255, 255, 100)
            },
            'error': {
                'keywords': ['error', 'exception', 'bug', 'crash', 'fail'],
                'animation': 'error_shake',
                'emoji': '💥',
                'color': (255, 50, 50)
            },
            'success': {
                'keywords': ['success', 'correct', 'working', 'solved', 'complete'],
                'animation': 'success_check',
                'emoji': '✅',
                'color': (50, 255, 50)
            }
        }
        
        # Animation positions
        self.animation_positions = [
            (self.width - 250, 100),   # Top right
            (self.width - 250, 300),   # Middle right
            (self.width - 250, 500),   # Bottom right
            (100, 100),                # Top left
            (100, 300),                # Middle left
            (100, 500),                # Bottom left
            (self.width // 2 - 100, 100),  # Top center
            (self.width // 2 - 100, 500),  # Bottom center
        ]
        
    def analyze_narration(self, narration_text: str, duration: float) -> List[Dict[str, Any]]:
        """Analyze narration text and find animation triggers."""
        triggers = []
        
        if not narration_text:
            return triggers
        
        # Split narration into time segments
        words = narration_text.split()
        total_words = len(words)
        
        # Create time segments
        segment_duration = duration / max(1, total_words // 10)  # One segment per 10 words
        
        for i, word_group in enumerate([words[j:j+10] for j in range(0, total_words, 10)]):
            segment_text = " ".join(word_group)
            start_time = i * segment_duration
            
            # Check for animation triggers
            for anim_type, anim_data in self.animation_mappings.items():
                for keyword in anim_data['keywords']:
                    if keyword.lower() in segment_text.lower():
                        triggers.append({
                            'type': anim_type,
                            'start_time': start_time,
                            'duration': self.animation_duration,
                            'text': segment_text,
                            'keyword': keyword,
                            'emoji': anim_data['emoji'],
                            'color': anim_data['color']
                        })
                        break  # Only trigger once per segment
        
        return triggers
    
    def create_animation_overlay(self, trigger: Dict[str, Any], time: float) -> Optional[Image.Image]:
        """Create animation overlay based on trigger type."""
        anim_type = trigger['type']
        anim_start = trigger['start_time']
        anim_duration = trigger['duration']
        
        # Check if animation should be active
        if time < anim_start or time > anim_start + anim_duration:
            return None
        
        # Calculate animation progress
        progress = (time - anim_start) / anim_duration
        
        # Create animation based on type
        if anim_type == 'function_call':
            return self._create_function_call_animation(trigger, progress)
        elif anim_type == 'loop_spin':
            return self._create_loop_spin_animation(trigger, progress)
        elif anim_type == 'condition_check':
            return self._create_condition_check_animation(trigger, progress)
        elif anim_type == 'recursion_tree':
            return self._create_recursion_tree_animation(trigger, progress)
        elif anim_type == 'array_highlight':
            return self._create_array_highlight_animation(trigger, progress)
        elif anim_type == 'swap_values':
            return self._create_swap_values_animation(trigger, progress)
        elif anim_type == 'sort_animation':
            return self._create_sort_animation(trigger, progress)
        elif anim_type == 'search_scan':
            return self._create_search_scan_animation(trigger, progress)
        elif anim_type == 'stack_push_pop':
            return self._create_stack_animation(trigger, progress)
        elif anim_type == 'queue_flow':
            return self._create_queue_animation(trigger, progress)
        elif anim_type == 'pointer_move':
            return self._create_pointer_animation(trigger, progress)
        elif anim_type == 'error_shake':
            return self._create_error_animation(trigger, progress)
        elif anim_type == 'success_check':
            return self._create_success_animation(trigger, progress)
        
        return None
    
    def _create_function_call_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create function call animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Animated function call
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Function box
        box_size = 80
        box_x = center_x - box_size // 2
        box_y = center_y - box_size // 2
        
        # Animated color
        color = trigger['color']
        alpha = int(255 * (1 - abs(progress - 0.5) * 2))
        fill_color = (*color, alpha)
        
        draw.rectangle([box_x, box_y, box_x + box_size, box_y + box_size], 
                      fill=fill_color, outline=(255, 255, 255), width=2)
        
        # Function text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        text = "f()"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_x = center_x - text_width // 2
        text_y = center_y - 8
        
        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        
        # Call arrow
        arrow_length = 40
        arrow_x = center_x + box_size // 2 + 10
        arrow_y = center_y
        
        if progress < 0.5:
            # Arrow growing
            current_length = int(arrow_length * (progress * 2))
            draw.line([arrow_x, arrow_y, arrow_x + current_length, arrow_y], 
                     fill=(255, 255, 255), width=3)
        else:
            # Arrow shrinking
            current_length = int(arrow_length * ((1 - progress) * 2))
            draw.line([arrow_x, arrow_y, arrow_x + current_length, arrow_y], 
                     fill=(255, 255, 255), width=3)
        
        return img
    
    def _create_loop_spin_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create loop spin animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Rotating arrow
        radius = 50
        angle = progress * 2 * math.pi * 2  # Two full rotations
        
        # Arrow points
        start_x = center_x + radius * math.cos(angle)
        start_y = center_y + radius * math.sin(angle)
        end_x = center_x + radius * math.cos(angle + 0.3)
        end_y = center_y + radius * math.sin(angle + 0.3)
        
        # Draw arrow
        color = trigger['color']
        alpha = int(255 * (0.5 + 0.5 * math.sin(progress * math.pi * 4)))
        arrow_color = (*color, alpha)
        
        draw.line([start_x, start_y, end_x, end_y], fill=arrow_color, width=4)
        
        # Arrowhead
        head_size = 8
        head_angle = angle + 0.3
        head_x1 = end_x - head_size * math.cos(head_angle - 0.3)
        head_y1 = end_y - head_size * math.sin(head_angle - 0.3)
        head_x2 = end_x - head_size * math.cos(head_angle + 0.3)
        head_y2 = end_y - head_size * math.sin(head_angle + 0.3)
        
        draw.line([end_x, end_y, head_x1, head_y1], fill=arrow_color, width=3)
        draw.line([end_x, end_y, head_x2, head_y2], fill=arrow_color, width=3)
        
        return img
    
    def _create_condition_check_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create condition check animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Decision diamond
        diamond_size = 60
        diamond_points = [
            (center_x, center_y - diamond_size // 2),
            (center_x + diamond_size // 2, center_y),
            (center_x, center_y + diamond_size // 2),
            (center_x - diamond_size // 2, center_y)
        ]
        
        color = trigger['color']
        alpha = int(255 * (0.7 + 0.3 * math.sin(progress * math.pi * 3)))
        fill_color = (*color, alpha)
        
        draw.polygon(diamond_points, fill=fill_color, outline=(255, 255, 255), width=2)
        
        # Question mark
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 24)
        except:
            font = ImageFont.load_default()
        
        text = "?"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        text_x = center_x - text_width // 2
        text_y = center_y - text_height // 2
        
        draw.text((text_x, text_y), text, fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_recursion_tree_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create recursion tree animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Growing tree structure
        max_depth = 3
        current_depth = int(progress * max_depth)
        
        color = trigger['color']
        
        for depth in range(current_depth + 1):
            nodes_at_depth = 2 ** depth
            y_pos = center_y - 80 + depth * 40
            
            for i in range(nodes_at_depth):
                x_pos = center_x - (nodes_at_depth - 1) * 20 // 2 + i * 40
                
                # Node
                node_size = 20 - depth * 3
                alpha = int(255 * (0.5 + 0.5 * progress))
                node_color = (*color, alpha)
                
                draw.ellipse([x_pos - node_size, y_pos - node_size, 
                            x_pos + node_size, y_pos + node_size], 
                           fill=node_color, outline=(255, 255, 255), width=1)
                
                # Connection lines
                if depth > 0:
                    parent_i = i // 2
                    parent_y = y_pos - 40
                    parent_x = center_x - (2 ** (depth - 1) - 1) * 20 // 2 + parent_i * 40
                    
                    line_alpha = int(255 * progress)
                    draw.line([parent_x, parent_y, x_pos, y_pos], 
                             fill=(255, 255, 255, line_alpha), width=2)
        
        return img
    
    def _create_array_highlight_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create array highlight animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Array boxes
        array_size = 5
        box_width = 30
        box_height = 25
        start_x = center_x - (array_size * box_width) // 2
        start_y = center_y - box_height // 2
        
        color = trigger['color']
        
        for i in range(array_size):
            x = start_x + i * box_width
            y = start_y
            
            # Highlight current element
            if i == int(progress * array_size):
                alpha = int(255 * (0.7 + 0.3 * math.sin(progress * math.pi * 4)))
                fill_color = (*color, alpha)
                draw.rectangle([x, y, x + box_width - 2, y + box_height], 
                              fill=fill_color, outline=(255, 255, 255), width=2)
            else:
                draw.rectangle([x, y, x + box_width - 2, y + box_height], 
                              fill=(50, 50, 50, 100), outline=(100, 100, 100), width=1)
            
            # Element value
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            value = str(i + 1)
            bbox = draw.textbbox((0, 0), value, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (box_width - text_width) // 2
            text_y = y + (box_height - 12) // 2
            
            draw.text((text_x, text_y), value, fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_swap_values_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create swap values animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Two boxes to swap
        box_size = 40
        box1_x = center_x - 60
        box2_x = center_x + 60
        box_y = center_y - box_size // 2
        
        color = trigger['color']
        
        if progress < 0.5:
            # First half: boxes moving up
            move_distance = int(30 * (progress * 2))
            box1_y = box_y - move_distance
            box2_y = box_y - move_distance
        else:
            # Second half: boxes moving down and across
            move_distance = int(30 * ((1 - progress) * 2))
            cross_distance = int(120 * ((progress - 0.5) * 2))
            box1_y = box_y - move_distance
            box2_y = box_y - move_distance
            box1_x = center_x - 60 + cross_distance
            box2_x = center_x + 60 - cross_distance
        
        # Draw boxes
        alpha = int(255 * (0.7 + 0.3 * math.sin(progress * math.pi * 2)))
        fill_color = (*color, alpha)
        
        draw.rectangle([box1_x, box1_y, box1_x + box_size, box1_y + box_size], 
                      fill=fill_color, outline=(255, 255, 255), width=2)
        draw.rectangle([box2_x, box2_y, box2_x + box_size, box2_y + box_size], 
                      fill=fill_color, outline=(255, 255, 255), width=2)
        
        # Box values
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 16)
        except:
            font = ImageFont.load_default()
        
        draw.text((box1_x + 10, box1_y + 10), "A", fill=(255, 255, 255), font=font)
        draw.text((box2_x + 10, box2_y + 10), "B", fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_sort_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create sort animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Array of numbers to sort
        numbers = [5, 2, 8, 1, 9, 3]
        box_width = 25
        box_height = 30
        start_x = center_x - (len(numbers) * box_width) // 2
        start_y = center_y - box_height // 2
        
        color = trigger['color']
        
        # Animate sorting
        current_step = int(progress * len(numbers))
        
        for i, num in enumerate(numbers):
            x = start_x + i * box_width
            y = start_y
            
            # Highlight current element being processed
            if i == current_step:
                alpha = int(255 * (0.7 + 0.3 * math.sin(progress * math.pi * 4)))
                fill_color = (*color, alpha)
            else:
                fill_color = (50, 50, 50, 150)
            
            draw.rectangle([x, y, x + box_width - 2, y + box_height], 
                          fill=fill_color, outline=(255, 255, 255), width=1)
            
            # Number
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            value = str(num)
            bbox = draw.textbbox((0, 0), value, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (box_width - text_width) // 2
            text_y = y + (box_height - 12) // 2
            
            draw.text((text_x, text_y), value, fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_search_scan_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create search scan animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Search array
        numbers = [3, 7, 2, 9, 5, 1, 8, 4]
        box_width = 20
        box_height = 25
        start_x = center_x - (len(numbers) * box_width) // 2
        start_y = center_y - box_height // 2
        
        color = trigger['color']
        
        # Scanning effect
        scan_position = int(progress * len(numbers))
        
        for i, num in enumerate(numbers):
            x = start_x + i * box_width
            y = start_y
            
            # Highlight scanned elements
            if i <= scan_position:
                alpha = int(255 * (0.5 + 0.5 * math.sin(progress * math.pi * 3)))
                fill_color = (*color, alpha)
            else:
                fill_color = (50, 50, 50, 100)
            
            draw.rectangle([x, y, x + box_width - 2, y + box_height], 
                          fill=fill_color, outline=(255, 255, 255), width=1)
            
            # Number
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
            except:
                font = ImageFont.load_default()
            
            value = str(num)
            bbox = draw.textbbox((0, 0), value, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (box_width - text_width) // 2
            text_y = y + (box_height - 10) // 2
            
            draw.text((text_x, text_y), value, fill=(255, 255, 255), font=font)
        
        # Search pointer
        if scan_position < len(numbers):
            pointer_x = start_x + scan_position * box_width + box_width // 2
            pointer_y = start_y - 10
            
            draw.polygon([(pointer_x, pointer_y), (pointer_x - 5, pointer_y - 10), 
                         (pointer_x + 5, pointer_y - 10)], fill=(255, 255, 0))
        
        return img
    
    def _create_stack_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create stack push/pop animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Stack container
        stack_width = 60
        stack_height = 120
        stack_x = center_x - stack_width // 2
        stack_y = center_y + 20
        
        draw.rectangle([stack_x, stack_y, stack_x + stack_width, stack_y + stack_height], 
                      fill=(50, 50, 50, 100), outline=(255, 255, 255), width=2)
        
        # Stack elements
        elements = ['A', 'B', 'C', 'D']
        element_height = 25
        color = trigger['color']
        
        if progress < 0.5:
            # Push animation
            num_elements = int(progress * 2 * len(elements))
        else:
            # Pop animation
            num_elements = int((1 - progress) * 2 * len(elements))
        
        for i in range(min(num_elements, len(elements))):
            element_y = stack_y + stack_height - (i + 1) * element_height
            element_x = stack_x + 5
            
            alpha = int(255 * (0.7 + 0.3 * math.sin(progress * math.pi * 2)))
            fill_color = (*color, alpha)
            
            draw.rectangle([element_x, element_y, element_x + stack_width - 10, element_y + element_height - 2], 
                          fill=fill_color, outline=(255, 255, 255), width=1)
            
            # Element label
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
            except:
                font = ImageFont.load_default()
            
            draw.text((element_x + 5, element_y + 5), elements[i], fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_queue_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create queue flow animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Queue container
        queue_width = 120
        queue_height = 40
        queue_x = center_x - queue_width // 2
        queue_y = center_y
        
        draw.rectangle([queue_x, queue_y, queue_x + queue_width, queue_y + queue_height], 
                      fill=(50, 50, 50, 100), outline=(255, 255, 255), width=2)
        
        # Queue elements
        elements = ['1', '2', '3', '4']
        element_width = 25
        color = trigger['color']
        
        # Animate elements moving through queue
        offset = int(progress * (queue_width - element_width))
        
        for i, element in enumerate(elements):
            element_x = queue_x + 5 + i * element_width - offset
            element_y = queue_y + 5
            
            if element_x >= queue_x and element_x <= queue_x + queue_width - element_width:
                alpha = int(255 * (0.7 + 0.3 * math.sin(progress * math.pi * 2)))
                fill_color = (*color, alpha)
                
                draw.rectangle([element_x, element_y, element_x + element_width - 2, element_y + 30], 
                              fill=fill_color, outline=(255, 255, 255), width=1)
                
                # Element label
                try:
                    font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 12)
                except:
                    font = ImageFont.load_default()
                
                draw.text((element_x + 5, element_y + 8), element, fill=(255, 255, 255), font=font)
        
        return img
    
    def _create_pointer_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create pointer move animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Memory cells
        cell_size = 30
        num_cells = 5
        start_x = center_x - (num_cells * cell_size) // 2
        start_y = center_y - cell_size // 2
        
        color = trigger['color']
        
        # Draw memory cells
        for i in range(num_cells):
            x = start_x + i * cell_size
            y = start_y
            
            draw.rectangle([x, y, x + cell_size - 2, y + cell_size], 
                          fill=(50, 50, 50, 100), outline=(100, 100, 100), width=1)
            
            # Cell address
            try:
                font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 10)
            except:
                font = ImageFont.load_default()
            
            addr = f"0x{i:02X}"
            bbox = draw.textbbox((0, 0), addr, font=font)
            text_width = bbox[2] - bbox[0]
            text_x = x + (cell_size - text_width) // 2
            text_y = y + 5
            
            draw.text((text_x, text_y), addr, fill=(200, 200, 200), font=font)
        
        # Moving pointer
        pointer_pos = int(progress * num_cells)
        pointer_x = start_x + pointer_pos * cell_size + cell_size // 2
        pointer_y = start_y - 15
        
        # Pointer arrow
        alpha = int(255 * (0.7 + 0.3 * math.sin(progress * math.pi * 3)))
        pointer_color = (*color, alpha)
        
        draw.polygon([(pointer_x, pointer_y), (pointer_x - 8, pointer_y - 15), 
                     (pointer_x + 8, pointer_y - 15)], fill=pointer_color)
        
        return img
    
    def _create_error_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create error shake animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Shaking effect
        shake_offset = int(5 * math.sin(progress * math.pi * 8))
        
        # Error symbol
        symbol_size = 60
        symbol_x = center_x - symbol_size // 2 + shake_offset
        symbol_y = center_y - symbol_size // 2
        
        color = trigger['color']
        alpha = int(255 * (0.8 + 0.2 * math.sin(progress * math.pi * 4)))
        fill_color = (*color, alpha)
        
        # X symbol
        line_width = 8
        draw.line([symbol_x, symbol_y, symbol_x + symbol_size, symbol_y + symbol_size], 
                 fill=fill_color, width=line_width)
        draw.line([symbol_x + symbol_size, symbol_y, symbol_x, symbol_y + symbol_size], 
                 fill=fill_color, width=line_width)
        
        return img
    
    def _create_success_animation(self, trigger: Dict[str, Any], progress: float) -> Image.Image:
        """Create success check animation."""
        img = Image.new('RGBA', (self.animation_size, self.animation_size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        center_x = self.animation_size // 2
        center_y = self.animation_size // 2
        
        # Checkmark
        check_size = 60
        check_x = center_x - check_size // 2
        check_y = center_y - check_size // 2
        
        color = trigger['color']
        alpha = int(255 * (0.8 + 0.2 * math.sin(progress * math.pi * 2)))
        fill_color = (*color, alpha)
        
        # Animated checkmark drawing
        if progress > 0.3:
            # Draw checkmark
            line_width = 8
            start_x = check_x + 15
            start_y = check_y + check_size // 2
            mid_x = check_x + check_size // 2
            mid_y = check_y + check_size - 15
            end_x = check_x + check_size - 15
            end_y = check_y + 15
            
            # First part of checkmark
            if progress > 0.5:
                draw.line([start_x, start_y, mid_x, mid_y], fill=fill_color, width=line_width)
            
            # Second part of checkmark
            if progress > 0.7:
                draw.line([mid_x, mid_y, end_x, end_y], fill=fill_color, width=line_width)
        
        return img
    
    def apply_animations_to_frame(self, base_frame: Image.Image, triggers: List[Dict[str, Any]], 
                                time: float) -> Image.Image:
        """Apply animation overlays to a base frame."""
        result_frame = base_frame.copy()
        
        # Apply each active animation
        for i, trigger in enumerate(triggers):
            animation = self.create_animation_overlay(trigger, time)
            if animation:
                # Position animation
                pos_index = i % len(self.animation_positions)
                pos_x, pos_y = self.animation_positions[pos_index]
                
                # Paste animation onto frame
                result_frame.paste(animation, (pos_x, pos_y), animation)
        
        return result_frame


def main():
    """Test the semantic animator."""
    animator = SemanticAnimator()
    
    # Test narration
    test_narration = "Let's look at this function that uses recursion to calculate factorial. First, we check the base case, then we call the function recursively. The function will swap values and iterate through the array."
    
    # Analyze narration
    triggers = animator.analyze_narration(test_narration, 10.0)
    
    print("🎬 Semantic Animator Test")
    print("=" * 40)
    print(f"📝 Narration: {test_narration}")
    print(f"🎯 Found {len(triggers)} animation triggers:")
    
    for trigger in triggers:
        print(f"  • {trigger['type']} at {trigger['start_time']:.1f}s: '{trigger['keyword']}'")
    
    print("\n✨ Animation types available:")
    for anim_type in animator.animation_mappings.keys():
        print(f"  • {anim_type}")


if __name__ == "__main__":
    main() 