"""
Download and prepare avatar image from Unsplash
"""

import requests
from PIL import Image, ImageDraw, ImageFont
import os
from io import BytesIO

def download_avatar():
    """Download avatar image from Unsplash and prepare it."""
    
    # Unsplash URL for the avatar
    url = "https://images.unsplash.com/photo-1728577740843-5f29c7586afe?q=80&w=1480&auto=format&fit=crop&ixlib=rb-4.1.0&ixid=M3wxMjA3fDB8MHxwaG90by1wYWdlfHx8fGVufDB8fHx8fA%3D%3D"
    
    try:
        print("Downloading avatar image...")
        response = requests.get(url, timeout=30)
        
        if response.status_code == 200:
            # Open the image
            img = Image.open(BytesIO(response.content))
            
            # Convert to RGBA if needed
            if img.mode != 'RGBA':
                img = img.convert('RGBA')
            
            # Resize to a reasonable size for avatar
            avatar_size = 300
            img = img.resize((avatar_size, avatar_size), Image.Resampling.LANCZOS)
            
            # Create a circular mask to remove background
            mask = Image.new('L', (avatar_size, avatar_size), 0)
            mask_draw = ImageDraw.Draw(mask)
            mask_draw.ellipse([0, 0, avatar_size, avatar_size], fill=255)
            
            # Apply the mask
            img.putalpha(mask)
            
            # Save the processed avatar
            img.save("avatar.png", "PNG")
            print("✅ Avatar saved as 'avatar.png'")
            
            # Also save a smaller version for the video
            small_avatar = img.resize((120, 120), Image.Resampling.LANCZOS)
            small_avatar.save("avatar_small.png", "PNG")
            print("✅ Small avatar saved as 'avatar_small.png'")
            
            return True
            
        else:
            print(f"❌ Failed to download image. Status code: {response.status_code}")
            return False
            
    except Exception as e:
        print(f"❌ Error downloading avatar: {e}")
        return False

def create_fallback_avatar():
    """Create a simple fallback avatar if download fails."""
    try:
        # Create a simple avatar with initials
        size = 300
        img = Image.new('RGBA', (size, size), (0, 0, 0, 0))
        draw = ImageDraw.Draw(img)
        
        # Create circular background
        draw.ellipse([0, 0, size, size], fill=(100, 150, 255, 255))
        
        # Add text
        try:
            font = ImageFont.truetype("/System/Library/Fonts/Arial.ttf", 120)
        except:
            font = ImageFont.load_default()
        
        text = "AI"
        bbox = draw.textbbox((0, 0), text, font=font)
        text_width = bbox[2] - bbox[0]
        text_height = bbox[3] - bbox[1]
        
        x = (size - text_width) // 2
        y = (size - text_height) // 2
        
        draw.text((x, y), text, fill=(255, 255, 255, 255), font=font)
        
        # Save
        img.save("avatar.png", "PNG")
        print("✅ Fallback avatar created as 'avatar.png'")
        
        # Small version
        small_avatar = img.resize((120, 120), Image.Resampling.LANCZOS)
        small_avatar.save("avatar_small.png", "PNG")
        print("✅ Small fallback avatar created as 'avatar_small.png'")
        
        return True
        
    except Exception as e:
        print(f"❌ Error creating fallback avatar: {e}")
        return False

if __name__ == "__main__":
    print("🎭 Avatar Downloader")
    print("=" * 30)
    
    # Try to download the avatar
    if download_avatar():
        print("🎉 Avatar downloaded successfully!")
    else:
        print("⚠️  Download failed, creating fallback avatar...")
        create_fallback_avatar()
    
    print("\n📁 Files created:")
    if os.path.exists("avatar.png"):
        print("  ✅ avatar.png")
    if os.path.exists("avatar_small.png"):
        print("  ✅ avatar_small.png")
    
    print("\n🎬 The avatar renderer will now use these images!") 