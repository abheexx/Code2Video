#!/usr/bin/env python3
"""
Offline Typewriter Demo - No OpenAI API Required
Creates a typewriter-style video with pre-written explanations
"""

import os
import sys
from text_to_speech import TextToSpeech
from typewriter_avatar_renderer import TypewriterAvatarRenderer

def create_offline_typewriter_demo():
    """Create a typewriter video without needing OpenAI API"""
    
    # Pre-written explanation for binary search
    sample_explanation = {
        'title': 'Binary Search Algorithm Explained',
        'narration': '''Welcome to this explanation of the binary search algorithm! Binary search is one of the most efficient ways to find an element in a sorted array. 

Let's break down how it works step by step. First, we start with two pointers: left at the beginning and right at the end of our array. 

Next, we calculate the middle point between left and right. We compare the middle element with our target value. 

If the middle element equals our target, we found it! If the target is smaller than the middle element, we search the left half by moving the right pointer. 

If the target is larger, we search the right half by moving the left pointer. We repeat this process until we find the target or determine it doesn't exist. 

This algorithm is incredibly efficient with a time complexity of O(log n), making it much faster than linear search for large datasets.'''
    }
    
    # Sample code
    sample_code = '''def binary_search(arr, target):
    """
    Performs binary search on a sorted array.
    Returns the index of target if found, -1 otherwise.
    """
    left = 0
    right = len(arr) - 1
    
    while left <= right:
        # Find the middle point
        mid = (left + right) // 2
        
        # Check if target is at mid
        if arr[mid] == target:
            return mid
        
        # If target is smaller, search left half
        elif arr[mid] > target:
            right = mid - 1
        
        # If target is larger, search right half
        else:
            left = mid + 1
    
    return -1  # Target not found

# Test the binary search function
sorted_numbers = [1, 3, 5, 7, 9, 11, 13, 15, 17, 19]
target = 7

result = binary_search(sorted_numbers, target)

if result != -1:
    print(f"Target {target} found at index {result}")
else:
    print(f"Target {target} not found in the array")'''
    
    try:
        print("🎬 Creating Offline Typewriter Demo")
        print("=" * 50)
        print("✅ No OpenAI API required!")
        print("✅ Using pre-written explanations")
        print("✅ Perfect audio synchronization")
        print("✅ Character-by-character animation")
        
        # Step 1: Generate speech
        print("\n🔊 Generating audio...")
        tts = TextToSpeech(engine="pyttsx3")
        audio_file = "offline_demo_audio.wav"
        tts.generate_speech(sample_explanation['narration'], audio_file)
        print(f"✅ Audio saved: {audio_file}")
        
        # Step 2: Create typewriter video
        print("\n🎥 Creating typewriter video...")
        renderer = TypewriterAvatarRenderer(1280, 720, 24)
        video_file = renderer.create_video(
            audio_file, 
            sample_explanation['narration'], 
            "offline_typewriter_demo.mp4"
        )
        
        print(f"✅ Video created: {video_file}")
        print(f"📁 File size: {os.path.getsize(video_file) / (1024*1024):.1f} MB")
        
        print("\n🎉 SUCCESS! Your typewriter demo is ready!")
        print("📺 Features demonstrated:")
        print("  ✅ 3 lines displayed at a time")
        print("  ✅ Character-by-character typing animation")
        print("  ✅ Bold highlighting of spoken words")
        print("  ✅ Perfect audio synchronization")
        print("  ✅ Smooth fade effects between lines")
        print("  ✅ Professional HD video output")
        
        return True
        
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
        return False

def create_quick_test_video():
    """Create a simple test video for immediate results"""
    
    simple_text = "Hello! This is a quick test of our typewriter system. Watch as each character appears in perfect sync with the audio. The currently spoken words are highlighted in bold. This demonstrates our advanced character-by-character animation with precise timing."
    
    try:
        print("⚡ Quick Typewriter Test")
        print("=" * 30)
        
        # Generate audio
        tts = TextToSpeech(engine="pyttsx3")
        audio_file = "quick_test_audio.wav"
        tts.generate_speech(simple_text, audio_file)
        
        # Create video
        renderer = TypewriterAvatarRenderer(1280, 720, 24)
        video_file = renderer.create_video(audio_file, simple_text, "quick_typewriter_test.mp4")
        
        print(f"✅ Quick test video created: {video_file}")
        return True
        
    except Exception as e:
        print(f"❌ Quick test failed: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Offline Typewriter Demo - No API Required!")
    print("=" * 60)
    
    choice = input("\nChoose option:\n1. Full demo with binary search explanation\n2. Quick test video\n\nEnter choice (1 or 2): ").strip()
    
    if choice == "1":
        if create_offline_typewriter_demo():
            print("\n🎊 Demo completed successfully!")
            print("💡 Open 'offline_typewriter_demo.mp4' to see the results!")
        else:
            print("\n💡 Demo failed. Try the quick test instead.")
    elif choice == "2":
        if create_quick_test_video():
            print("\n🎊 Quick test completed!")
            print("💡 Open 'quick_typewriter_test.mp4' to see the results!")
        else:
            print("\n💡 Quick test failed.")
    else:
        print("Invalid choice. Please run again and select 1 or 2.") 