import os
import sys
import zipfile
import requests
import subprocess
import json
from pathlib import Path


def get_chrome_version():
    """Get installed Chrome version"""
    try:
        # Thử lệnh Windows
        result = subprocess.run(
            ['reg', 'query', 'HKEY_CURRENT_USER\\Software\\Google\\Chrome\\BLBeacon', '/v', 'version'],
            capture_output=True,
            text=True
        )
        if result.returncode == 0:
            version = result.stdout.split()[-1]
            return version
    except:
        pass
    
    try:
        # Thử đọc từ file
        chrome_path = r"C:\Program Files\Google\Chrome\Application\chrome.exe"
        if os.path.exists(chrome_path):
            result = subprocess.run(
                [chrome_path, '--version'],
                capture_output=True,
                text=True
            )
            version = result.stdout.strip().split()[-1]
            return version
    except:
        pass
    
    print("⚠️  Unable to auto-detect Chrome version")
    version = input("Enter your Chrome version (e.g., 119.0.6045.105): ")
    return version


def get_chromedriver_download_url(chrome_version):
    """Get appropriate ChromeDriver download URL"""
    try:
        # Get major version (e.g., 119 from 119.0.6045.105)
        major_version = chrome_version.split('.')[0]
        
        # Chrome for Testing API
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        
        print(f"🔍 Finding ChromeDriver for Chrome version {chrome_version}...")
        response = requests.get(api_url, timeout=10)
        response.raise_for_status()
        
        data = response.json()
        
        # Tìm version phù hợp
        for version_info in reversed(data['versions']):
            if version_info['version'].startswith(major_version):
                downloads = version_info.get('downloads', {}).get('chromedriver', [])
                for download in downloads:
                    if download['platform'] == 'win64':
                        return download['url'], version_info['version']
        
        # If not found, try latest version
        print(f"⚠️  ChromeDriver not found for version {major_version}, trying latest...")
        latest = data['versions'][-1]
        downloads = latest.get('downloads', {}).get('chromedriver', [])
        for download in downloads:
            if download['platform'] == 'win64':
                return download['url'], latest['version']
        
        raise Exception("No suitable ChromeDriver found")
        
    except Exception as e:
        print(f"❌ Error: {e}")
        return None, None


def download_chromedriver(url, version):
    """Download ChromeDriver"""
    try:
        print(f"📥 Downloading ChromeDriver {version}...")
        
        response = requests.get(url, stream=True, timeout=30)
        response.raise_for_status()
        
        zip_path = "chromedriver_temp.zip"
        total_size = int(response.headers.get('content-length', 0))
        
        with open(zip_path, 'wb') as f:
            downloaded = 0
            for chunk in response.iter_content(chunk_size=8192):
                if chunk:
                    f.write(chunk)
                    downloaded += len(chunk)
                    if total_size > 0:
                        percent = (downloaded / total_size) * 100
                        print(f"\r⏳ Downloading: {percent:.1f}%", end='')
        
        print("\n✅ Download complete!")
        return zip_path
        
    except Exception as e:
        print(f"\n❌ Download error: {e}")
        return None


def extract_chromedriver(zip_path):
    """Extract ChromeDriver"""
    try:
        print("📦 Extracting...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Find chromedriver.exe in zip
            for file in zip_ref.namelist():
                if file.endswith('chromedriver.exe'):
                    # Extract directly to current directory
                    with zip_ref.open(file) as source:
                        with open('chromedriver.exe', 'wb') as target:
                            target.write(source.read())
                    print("✅ Extraction complete!")
                    return True
        
        print("❌ chromedriver.exe not found in zip file")
        return False
        
    except Exception as e:
        print(f"❌ Extraction error: {e}")
        return False
    finally:
        # Delete temporary zip file
        if os.path.exists(zip_path):
            os.remove(zip_path)


def update_config():
    """Update config.json file"""
    try:
        config_path = "config.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config['chromedriver_path'] = 'chromedriver.exe'
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ config.json updated")
        else:
            print("⚠️  config.json not found")
            
    except Exception as e:
        print(f"⚠️  Error updating config: {e}")


def main():
    print("=" * 60)
    print("🚀 AUTOMATED CHROMEDRIVER DOWNLOAD SCRIPT")
    print("=" * 60)
    print()
    
    # Check Chrome version
    chrome_version = get_chrome_version()
    print(f"✓ Chrome version: {chrome_version}")
    print()
    
    # Get download URL
    url, driver_version = get_chromedriver_download_url(chrome_version)
    
    if not url:
        print("❌ Unable to find download URL. Please download manually from:")
        print("   https://googlechromelabs.github.io/chrome-for-testing/")
        return
    
    print(f"✓ Found ChromeDriver version: {driver_version}")
    print()
    
    # Download ChromeDriver
    zip_path = download_chromedriver(url, driver_version)
    
    if not zip_path:
        return
    
    # Extract
    if extract_chromedriver(zip_path):
        # Update config
        update_config()
        
        print()
        print("=" * 60)
        print("🎉 COMPLETE!")
        print("=" * 60)
        print("✅ ChromeDriver installed at: chromedriver.exe")
        print("✅ config.json updated")
        print()
        print("You can now run the main program:")
        print("   python main.py")
    else:
        print("❌ Installation failed")


if __name__ == "__main__":
    main()
