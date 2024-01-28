import requests
import zipfile
import os
import subprocess
import shutil

url = 'https://github.com/ZerBea/hcxtools/archive/refs/tags/6.2.5.zip'
download_path = '/tmp/hcxtools-6.2.5.zip'
extracted_folder = '/tmp/hcxtools_extraction/'
os.makedirs(extracted_folder, exist_ok=True)

try:
    subprocess.run(['sudo', 'apt', '-y', 'install', 'libcurl4-openssl-dev'], check=True)
    response = requests.get(url)
    response.raise_for_status()
    with open(download_path, 'wb') as f:
        f.write(response.content)
    with zipfile.ZipFile(download_path, 'r') as zip_ref:
        zip_ref.extractall(extracted_folder)
    os.chdir(os.path.join(extracted_folder, 'hcxtools-6.2.5'))
    subprocess.run(['make'], check=True)
    subprocess.run(['sudo', 'make', 'install'], check=True)
except requests.RequestException as e:
    print(f"Request Exception: {e}")
except zipfile.BadZipFile as e:
    print(f"Bad Zip File Exception: {e}")
except subprocess.CalledProcessError as e:
    print(f"Called Process Error: {e}")
finally:
    if os.path.exists(download_path):
        os.remove(download_path)
    if os.path.exists(extracted_folder):
        shutil.rmtree(extracted_folder)
