import requests
import os
import webbrowser
from datetime import datetime
from decouple import config
from pathlib import Path

def generate_image(prompt):
    """
    Generate an image using Hugging Face's Stable Diffusion API
    """
    try:
       
        images_dir = Path("generated_images")
        images_dir.mkdir(exist_ok=True)

        api_token = config('HUGGING_FACE_TOKEN')
        if not api_token:
            return "Error: Hugging Face API token not found in .env file"

        API_URL = "https://api-inference.huggingface.co/models/stabilityai/stable-diffusion-xl-base-1.0"
        headers = {
            "Authorization": f"Bearer {api_token}"
        }

        payload = {
            "inputs": prompt
        }

        print("Generating image... This might take a few seconds.")
        response = requests.post(API_URL, headers=headers, json=payload)

        if response.status_code == 200:
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            image_path = images_dir / f"image_{timestamp}.png"

            with open(image_path, "wb") as f:
                f.write(response.content)

            abs_path = str(image_path.absolute())

            def open_image():
                try:
                    if os.name == 'nt':  
                        os.startfile(abs_path)
                    elif os.name == 'posix':  
                        webbrowser.open(f'file://{abs_path}')
                except Exception as e:
                    print(f"Note: Could not automatically open image: {e}")

            import threading
            threading.Thread(target=open_image).start()

            return "Image generated successfully", f"Image generated and saved as {abs_path}"

        elif response.status_code == 401:
            return "Error: Invalid API token", "Error: Invalid API token. Please check your Hugging Face API token."
        
        elif response.status_code == 429:
            return "Too many requests", "Too many requests. Please wait a moment and try again."
        
        elif response.status_code == 503:
            return "Model is currently loading", "Model is currently loading. Please try again in a few minutes."
        
        else:
            return f"Error generating image", f"Error: API returned status code {response.status_code}"

    except Exception as e:
        return "Error generating image", f"An unexpected error occurred: {str(e)}"

if __name__ == "__main__":
    test_prompt = "a beautiful sunset over mountains"
    print(generate_image(test_prompt))