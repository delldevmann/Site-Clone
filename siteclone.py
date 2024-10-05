import requests
from bs4 import BeautifulSoup
import os
import re
from urllib.parse import urljoin
import argparse
import time

# Set the directory where cloned files will be saved
SAVE_DIR = "cloned_website"

# Create the save directory if it doesn't exist
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Function to clean and create valid filenames
def clean_filename(url):
    return re.sub(r'[^a-zA-Z0-9]', '_', url)[:100]

# Function to download a file (like an image or stylesheet)
def download_file(url, save_path):
    try:
        if url.startswith("data:"):
            # Skip downloading data URIs
            return
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers, stream=True)
        if response.status_code == 200:
            with open(save_path, 'wb') as file:
                for chunk in response.iter_content(1024):
                    file.write(chunk)
        else:
            print(f"Failed to download file from {url}")
    except Exception as e:
        print(f"Error downloading {url}: {e}")

# Function to clone the HTML page and related resources
def clone_website(url):
    try:
        headers = {
            "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36"
        }
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            soup = BeautifulSoup(response.content, "html.parser")
            
            # Update links for resources (images, styles, etc.)
            for tag in soup.find_all(['link', 'img', 'script']):
                if tag.has_attr('href'):
                    resource_url = tag['href']
                elif tag.has_attr('src'):
                    resource_url = tag['src']
                else:
                    continue
                
                # Ensure that the URL is complete and valid
                resource_url = urljoin(url, resource_url)
                
                # Skip data URIs
                if resource_url.startswith("data:"):
                    continue
                
                resource_filename = clean_filename(resource_url)
                resource_save_path = os.path.join(SAVE_DIR, resource_filename)

                # Download and save the resource
                download_file(resource_url, resource_save_path)
                time.sleep(0.1)  # Add delay to avoid overwhelming the server
                
                # Update the resource link to the local path
                if tag.has_attr('href'):
                    tag['href'] = resource_filename
                elif tag.has_attr('src'):
                    tag['src'] = resource_filename
            
            # Save the HTML content
            html_filename = clean_filename(url) + ".html"
            html_path = os.path.join(SAVE_DIR, html_filename)
            with open(html_path, "w", encoding="utf-8") as file:
                file.write(str(soup))
            print(f"Page cloned: {html_path}")
        else:
            print(f"Failed to fetch page from {url}")
    except Exception as e:
        print(f"Error cloning website: {e}")

# Main function to handle command-line arguments
def main():
    parser = argparse.ArgumentParser(description="Clone a website's HTML and related resources.")
    parser.add_argument('url', type=str, help="The URL of the website to clone.")
    args = parser.parse_args()

    # Clone the target website
    clone_website(args.url)

if __name__ == "__main__":
    main()
