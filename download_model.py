import os
import sys
import requests
from tqdm import tqdm

def download_file(url, destination):
    """
    Download a file from a URL to a local destination with progress bar
    """
    if os.path.exists(destination):
        print(f"File {destination} already exists. Skipping download.")
        return

    try:
        response = requests.get(url, stream=True)
        response.raise_for_status()
        
        # Get file size for progress bar
        total_size = int(response.headers.get('content-length', 0))
        block_size = 1024  # 1 Kibibyte
        
        print(f"Downloading {destination}...")
        
        with open(destination, 'wb') as file, tqdm(
                desc=destination,
                total=total_size,
                unit='iB',
                unit_scale=True,
                unit_divisor=1024,
        ) as bar:
            for data in response.iter_content(block_size):
                file.write(data)
                bar.update(len(data))
                
        print(f"Downloaded {destination} successfully.")
    except Exception as e:
        print(f"Error downloading file: {e}")
        if os.path.exists(destination):
            os.remove(destination)
        sys.exit(1)

if __name__ == "__main__":
    # Replace this URL with the actual URL of your model file
    MODEL_URL = "https://example.com/models/ruropebert_clf1.pth"  # Замените эту ссылку на актуальную
    MODEL_DESTINATION = "ruropebert_clf1.pth"
    
    download_file(MODEL_URL, MODEL_DESTINATION)
    
    print("\nModel downloaded. You can now run the API with:")
    print("uvicorn api:app --reload") 