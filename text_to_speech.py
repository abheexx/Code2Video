"""
Code2Vid - Text-to-Speech Module
Converts text explanations to audio using various TTS engines.
"""

import os
import tempfile
from typing import Optional, Union
from pathlib import Path
import requests
import json

# Try to import TTS libraries (some might not be available)
try:
    import pyttsx3
    PYTTSX3_AVAILABLE = True
except (ImportError, NameError):
    PYTTSX3_AVAILABLE = False

try:
    from elevenlabs import client
    import elevenlabs
    ELEVENLABS_AVAILABLE = True
except (ImportError, NameError):
    ELEVENLABS_AVAILABLE = False


class TextToSpeech:
    """Handles text-to-speech conversion using multiple engines."""
    
    def __init__(self, engine: str = "elevenlabs", api_key: Optional[str] = None):
        """
        Initialize the TTS engine.
        
        Args:
            engine: TTS engine to use ('elevenlabs', 'pyttsx3', 'bark')
            api_key: API key for the selected engine
        """
        self.engine = engine.lower()
        self.api_key = api_key
        
        if self.engine == "elevenlabs":
            if not ELEVENLABS_AVAILABLE:
                raise ImportError("ElevenLabs not available. Install with: pip install elevenlabs")
            if not self.api_key:
                self.api_key = os.getenv("ELEVENLABS_API_KEY")
            if not self.api_key:
                raise ValueError("ElevenLabs API key required. Set ELEVENLABS_API_KEY environment variable.")
            # Create ElevenLabs client
            self.elevenlabs_client = client.ElevenLabs(api_key=self.api_key)
            
        elif self.engine == "pyttsx3":
            if not PYTTSX3_AVAILABLE:
                raise ImportError("pyttsx3 not available. Install with: pip install pyttsx3")
            try:
                # Try different initialization methods for macOS
                drivers_to_try = [None, 'nsss', 'espeak']
                self.tts_engine = None
                
                for driver in drivers_to_try:
                    try:
                        if driver:
                            self.tts_engine = pyttsx3.init(driverName=driver)
                        else:
                            self.tts_engine = pyttsx3.init()
                        break  # If successful, break out of the loop
                    except Exception as driver_error:
                        print(f"Driver {driver} failed: {driver_error}")
                        continue
                
                if self.tts_engine is None:
                    # Fallback to system TTS using say command on macOS
                    self.use_system_tts = True
                    print("pyttsx3 failed, using macOS system TTS as fallback")
                    
            except Exception as e:
                # On macOS, pyttsx3 often fails due to objc issues
                if "objc" in str(e).lower():
                    # Fallback to system TTS using say command on macOS
                    self.use_system_tts = True
                    print("pyttsx3 failed due to objc issues, using macOS system TTS as fallback")
                else:
                    raise ImportError(f"pyttsx3 initialization failed: {e}")
            
        else:
            raise ValueError(f"Unsupported TTS engine: {engine}. Supported: elevenlabs, pyttsx3")
    
    def generate_speech(self, text: str, output_path: str = "narration.wav", 
                       voice: str = "default", speed: float = 1.0) -> str:
        """
        Generate speech from text.
        
        Args:
            text: Text to convert to speech
            output_path: Path to save the audio file
            voice: Voice to use (engine-specific)
            speed: Speech speed multiplier
            
        Returns:
            Path to the generated audio file
        """
        
        if self.engine == "elevenlabs":
            return self._generate_elevenlabs(text, output_path, voice, speed)
        elif self.engine == "pyttsx3":
            return self._generate_pyttsx3(text, output_path, voice, speed)
        else:
            raise ValueError(f"Unsupported engine: {self.engine}")
    
    def _generate_elevenlabs(self, text: str, output_path: str, voice: str, speed: float) -> str:
        """Generate speech using ElevenLabs."""
        try:
            # Available voices for ElevenLabs
            available_voices = {
                "default": "21m00Tcm4TlvDq8ikWAM",  # Rachel
                "male": "pNInz6obpgDQGcFmaJgB",     # Adam
                "female": "21m00Tcm4TlvDq8ikWAM",   # Rachel
                "british": "AZnzlk1XvdvUeBnXmlld",  # Domi
                "deep": "VR6AewLTigWG4xSOukaG"      # Josh
            }
            
            voice_id = available_voices.get(voice, available_voices["default"])
            
            # Generate audio using the new client-based API
            audio_stream = self.elevenlabs_client.text_to_speech.convert(
                voice_id=voice_id,
                text=text,
                model_id="eleven_monolingual_v1"
            )
            
            # Save to file - handle the generator response
            with open(output_path, 'wb') as f:
                for chunk in audio_stream:
                    f.write(chunk)
            
            return output_path
            
        except Exception as e:
            raise Exception(f"ElevenLabs TTS failed: {str(e)}")
    
    def _generate_pyttsx3(self, text: str, output_path: str, voice: str, speed: float) -> str:
        """Generate speech using pyttsx3 or system TTS fallback."""
        try:
            # Check if we should use system TTS fallback
            if hasattr(self, 'use_system_tts') and self.use_system_tts:
                return self._generate_system_tts(text, output_path, voice, speed)
            
            # Use pyttsx3 if available
            if hasattr(self, 'tts_engine') and self.tts_engine:
                # Configure the engine for slower, more natural speech
                self.tts_engine.setProperty('rate', int(150 * speed))  # Slower speed (was 200)
                self.tts_engine.setProperty('volume', 0.9)  # Volume
                
                # Set voice if specified
                if voice != "default":
                    voices = self.tts_engine.getProperty('voices')
                    for v in voices:
                        if voice.lower() in v.name.lower():
                            self.tts_engine.setProperty('voice', v.id)
                            break
                
                # Generate and save
                self.tts_engine.save_to_file(text, output_path)
                self.tts_engine.runAndWait()
                
                return output_path
            else:
                # Fallback to system TTS
                return self._generate_system_tts(text, output_path, voice, speed)
            
        except Exception as e:
            # Fallback to system TTS if pyttsx3 fails
            try:
                return self._generate_system_tts(text, output_path, voice, speed)
            except Exception as fallback_error:
                raise Exception(f"Both pyttsx3 and system TTS failed: {str(e)} -> {str(fallback_error)}")
    
    def _generate_system_tts(self, text: str, output_path: str, voice: str, speed: float) -> str:
        """Generate speech using macOS system TTS (say command)."""
        try:
            import subprocess
            import platform
            import os
            
            if platform.system() == "Darwin":  # macOS
                # Create temporary AIFF file
                temp_aiff = output_path.replace('.wav', '.aiff')
                
                # Use the 'say' command on macOS with AIFF format and slower rate
                # Rate 150 is slower than default 200 for more natural speech
                rate = max(80, int(150 * speed))  # Ensure minimum readable rate
                cmd = ['say', '-r', str(rate), '-o', temp_aiff, text]
                subprocess.run(cmd, check=True, capture_output=True)
                
                # Convert AIFF to WAV using ffmpeg if available
                try:
                    convert_cmd = ['ffmpeg', '-i', temp_aiff, '-acodec', 'pcm_s16le', '-ar', '22050', output_path, '-y']
                    subprocess.run(convert_cmd, check=True, capture_output=True)
                    # Clean up temp file
                    os.remove(temp_aiff)
                except (subprocess.CalledProcessError, FileNotFoundError):
                    # If ffmpeg fails, try using sox instead
                    try:
                        convert_cmd = ['sox', temp_aiff, output_path]
                        subprocess.run(convert_cmd, check=True, capture_output=True)
                        os.remove(temp_aiff)
                    except (subprocess.CalledProcessError, FileNotFoundError):
                        # If both fail, try to install ffmpeg and retry
                        print("ffmpeg and sox not found. Trying to install ffmpeg...")
                        try:
                            # Try to install ffmpeg using homebrew
                            subprocess.run(['brew', 'install', 'ffmpeg'], check=True, capture_output=True)
                            # Retry ffmpeg conversion
                            convert_cmd = ['ffmpeg', '-i', temp_aiff, '-acodec', 'pcm_s16le', '-ar', '22050', output_path, '-y']
                            subprocess.run(convert_cmd, check=True, capture_output=True)
                            os.remove(temp_aiff)
                        except (subprocess.CalledProcessError, FileNotFoundError):
                            # If all else fails, just use the AIFF file and let MoviePy handle it
                            print("Using AIFF file directly - MoviePy should handle it")
                            os.rename(temp_aiff, output_path.replace('.wav', '.aiff'))
                            return output_path.replace('.wav', '.aiff')
                
                return output_path
            else:
                raise Exception("System TTS only supported on macOS")
                
        except Exception as e:
            raise Exception(f"System TTS failed: {str(e)}")
    
    def get_available_voices(self) -> list:
        """Get list of available voices for the current engine."""
        if self.engine == "elevenlabs":
            return ["default", "male", "female", "british", "deep"]
        elif self.engine == "pyttsx3":
            if PYTTSX3_AVAILABLE:
                voices = self.tts_engine.getProperty('voices')
                return [v.name for v in voices]
            return []
        return []
    
    def estimate_duration(self, text: str, words_per_minute: int = 150) -> float:
        """
        Estimate the duration of the generated speech.
        
        Args:
            text: Text to estimate duration for
            words_per_minute: Average speaking rate
            
        Returns:
            Estimated duration in seconds
        """
        word_count = len(text.split())
        duration_minutes = word_count / words_per_minute
        return duration_minutes * 60


class AudioProcessor:
    """Handles audio processing and optimization."""
    
    @staticmethod
    def add_silence(audio_path: str, silence_duration: float = 0.5) -> str:
        """
        Add silence to the beginning and end of an audio file.
        
        Args:
            audio_path: Path to the audio file
            silence_duration: Duration of silence to add (seconds)
            
        Returns:
            Path to the processed audio file
        """
        try:
            from moviepy.editor import AudioFileClip, concatenate_audioclips
            
            # Load the audio
            audio = AudioFileClip(audio_path)
            
            # Create silence clips
            from moviepy.audio.AudioClip import AudioClip
            silence = AudioClip(lambda t: 0, duration=silence_duration)
            
            # Concatenate: silence + audio + silence
            final_audio = concatenate_audioclips([silence, audio, silence])
            
            # Save the result
            output_path = audio_path.replace('.wav', '_with_silence.wav')
            final_audio.write_audiofile(output_path)
            
            return output_path
            
        except ImportError:
            print("moviepy not available for audio processing")
            return audio_path
        except Exception as e:
            print(f"Audio processing failed: {e}")
            return audio_path


def main():
    """Example usage of the TextToSpeech module."""
    
    example_text = """
    Welcome to our code explanation! Today we're looking at a simple Python function that calculates the Fibonacci sequence.
    This function uses recursion to solve a classic mathematical problem.
    """
    
    try:
        # Try ElevenLabs first (if API key is available)
        if os.getenv("ELEVENLABS_API_KEY"):
            print("Using ElevenLabs TTS...")
            tts = TextToSpeech(engine="elevenlabs")
            audio_path = tts.generate_speech(example_text, "narration_elevenlabs.wav", voice="default")
            print(f"Audio saved to: {audio_path}")
            
            # Estimate duration
            duration = tts.estimate_duration(example_text)
            print(f"Estimated duration: {duration:.2f} seconds")
            
        else:
            print("Using pyttsx3 TTS (ElevenLabs API key not found)...")
            tts = TextToSpeech(engine="pyttsx3")
            audio_path = tts.generate_speech(example_text, "narration_pyttsx3.wav", voice="default")
            print(f"Audio saved to: {audio_path}")
            
            # Show available voices
            voices = tts.get_available_voices()
            print(f"Available voices: {voices}")
            
    except Exception as e:
        print(f"Error: {e}")


if __name__ == "__main__":
    main() 