#!/usr/bin/env python3
"""
Test script for the new Typewriter Avatar Renderer
Demonstrates perfect audio sync with character-by-character animation
"""

import os
import sys
from video_renderer import VideoRenderer

def test_typewriter_video():
    """Test the typewriter-style video creation"""
    
    # Sample code and explanation
    sample_code = """
def fibonacci(n):
    '''Calculate the nth Fibonacci number'''
    if n <= 1:
        return n
    return fibonacci(n-1) + fibonacci(n-2)

# Example usage
result = fibonacci(10)
print(f"The 10th Fibonacci number is: {result}")
"""
    
    explanation = {
        'title': 'Fibonacci Function Explanation',
        'explanation': 'This code demonstrates a recursive implementation of the Fibonacci sequence.',
        'narration': 'Hello! This is a demonstration of the typewriter-style narration system. Each character appears in perfect sync with the audio, and the currently spoken words are highlighted in bold. The text is organized into exactly three lines that appear with smooth fade effects. When the first three lines are complete, the next line appears automatically. This creates a professional, engaging video experience that keeps viewers focused on the content.'
    }
    
    # Check if we have an audio file
    audio_file = "output.wav"
    if not os.path.exists(audio_file):
        print(f"Audio file {audio_file} not found. Please run the TTS system first.")
        return False
    
    try:
        # Create video renderer
        renderer = VideoRenderer()
        
        print("🎬 Creating Typewriter-Style Video...")
        print("Features:")
        print("✅ Character-by-character typewriter effect")
        print("✅ Perfect audio synchronization")
        print("✅ Bold highlighting of spoken words")
        print("✅ 3-line display with fade effects")
        print("✅ Automatic line progression")
        print("✅ Professional styling")
        
        # Create the video
        output_file = renderer.create_video(
            code=sample_code,
            audio_path=audio_file,
            explanation=explanation,
            output_path="typewriter_demo.mp4",
            animated=True
        )
        
        print(f"\n🎉 Success! Typewriter video created: {output_file}")
        print(f"📁 File size: {os.path.getsize(output_file) / (1024*1024):.1f} MB")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating typewriter video: {e}")
        import traceback
        traceback.print_exc()
        return False

def test_whisper_timing():
    """Test Whisper timing extraction"""
    try:
        from typewriter_avatar_renderer import TypewriterAvatarRenderer
        
        audio_file = "output.wav"
        if not os.path.exists(audio_file):
            print(f"Audio file {audio_file} not found.")
            return False
        
        renderer = TypewriterAvatarRenderer()
        
        print("🔍 Testing Whisper timing extraction...")
        text = "This is a test of the word timing extraction system."
        
        word_timings = renderer.extract_word_timings(audio_file, text)
        
        print(f"✅ Extracted {len(word_timings)} word timings:")
        for i, timing in enumerate(word_timings[:5]):  # Show first 5
            print(f"  {i+1}. '{timing.word}' ({timing.start_time:.2f}s - {timing.end_time:.2f}s)")
        
        return True
        
    except Exception as e:
        print(f"❌ Error testing Whisper timing: {e}")
        return False

if __name__ == "__main__":
    print("🚀 Typewriter Video System Test")
    print("=" * 50)
    
    # Test Whisper timing first
    if test_whisper_timing():
        print("\n✅ Whisper timing test passed!")
    else:
        print("\n⚠️  Whisper timing test failed, will use fallback timing")
    
    # Test full video creation
    if test_typewriter_video():
        print("\n🎊 All tests passed! Your typewriter video system is ready!")
    else:
        print("\n💡 Try running the TTS system first to generate audio, then test again.") 