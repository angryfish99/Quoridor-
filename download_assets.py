import urllib.request
import os
import ssl

def download_assets():
    if not os.path.exists('assets'):
        os.makedirs('assets')
    
    # Bypass SSL errors for simple scripts if certificates are messy on some environments
    context = ssl._create_unverified_context()

    assets = {
        # High quality Wood Texture from Wikimedia Commons (CC BY-SA 3.0)
        "wood_texture.jpg": "https://upload.wikimedia.org/wikipedia/commons/thumb/e/e0/Wood_Floor_Texture.jpg/800px-Wood_Floor_Texture.jpg",
        
        # Chess Pawn (White) - we will colorize it for Red/Blue
        "pawn.png": "https://upload.wikimedia.org/wikipedia/commons/thumb/4/45/Chess_plt45.svg/480px-Chess_plt45.svg.png" 
    }
    
    headers = {'User-Agent': 'Mozilla/5.0'}

    for filename, url in assets.items():
        print(f"Downloading {filename}...")
        try:
            req = urllib.request.Request(url, headers=headers)
            with urllib.request.urlopen(req, context=context) as response:
                with open(f'assets/{filename}', 'wb') as f:
                    f.write(response.read())
            print(f"Successfully downloaded assets/{filename}")
        except Exception as e:
            print(f"Failed to download {filename}: {e}")

if __name__ == "__main__":
    download_assets()
