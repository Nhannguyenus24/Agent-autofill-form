import os
import sys
import zipfile
import requests
import subprocess
import json
from pathlib import Path


def get_chrome_version():
    """Lấy phiên bản Chrome đang cài"""
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
    
    print("⚠️  Không thể tự động phát hiện phiên bản Chrome")
    version = input("Nhập phiên bản Chrome của bạn (VD: 119.0.6045.105): ")
    return version


def get_chromedriver_download_url(chrome_version):
    """Lấy URL download ChromeDriver phù hợp"""
    try:
        # Lấy major version (VD: 119 từ 119.0.6045.105)
        major_version = chrome_version.split('.')[0]
        
        # API mới của Chrome for Testing
        api_url = "https://googlechromelabs.github.io/chrome-for-testing/known-good-versions-with-downloads.json"
        
        print(f"🔍 Đang tìm ChromeDriver cho Chrome version {chrome_version}...")
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
        
        # Nếu không tìm thấy, thử version mới nhất
        print(f"⚠️  Không tìm thấy ChromeDriver cho version {major_version}, thử version mới nhất...")
        latest = data['versions'][-1]
        downloads = latest.get('downloads', {}).get('chromedriver', [])
        for download in downloads:
            if download['platform'] == 'win64':
                return download['url'], latest['version']
        
        raise Exception("Không tìm thấy ChromeDriver phù hợp")
        
    except Exception as e:
        print(f"❌ Lỗi: {e}")
        return None, None


def download_chromedriver(url, version):
    """Tải ChromeDriver"""
    try:
        print(f"📥 Đang tải ChromeDriver {version}...")
        
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
                        print(f"\r⏳ Đang tải: {percent:.1f}%", end='')
        
        print("\n✅ Tải xuống hoàn tất!")
        return zip_path
        
    except Exception as e:
        print(f"\n❌ Lỗi khi tải: {e}")
        return None


def extract_chromedriver(zip_path):
    """Giải nén ChromeDriver"""
    try:
        print("📦 Đang giải nén...")
        
        with zipfile.ZipFile(zip_path, 'r') as zip_ref:
            # Tìm file chromedriver.exe trong zip
            for file in zip_ref.namelist():
                if file.endswith('chromedriver.exe'):
                    # Giải nén trực tiếp vào thư mục hiện tại
                    with zip_ref.open(file) as source:
                        with open('chromedriver.exe', 'wb') as target:
                            target.write(source.read())
                    print("✅ Giải nén hoàn tất!")
                    return True
        
        print("❌ Không tìm thấy chromedriver.exe trong file zip")
        return False
        
    except Exception as e:
        print(f"❌ Lỗi khi giải nén: {e}")
        return False
    finally:
        # Xóa file zip tạm
        if os.path.exists(zip_path):
            os.remove(zip_path)


def update_config():
    """Cập nhật file config.json"""
    try:
        config_path = "config.json"
        
        if os.path.exists(config_path):
            with open(config_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
            
            config['chromedriver_path'] = 'chromedriver.exe'
            
            with open(config_path, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            print("✅ Đã cập nhật config.json")
        else:
            print("⚠️  Không tìm thấy config.json")
            
    except Exception as e:
        print(f"⚠️  Lỗi khi cập nhật config: {e}")


def main():
    print("=" * 60)
    print("🚀 SCRIPT TỰ ĐỘNG TẢI CHROMEDRIVER")
    print("=" * 60)
    print()
    
    # Kiểm tra Chrome version
    chrome_version = get_chrome_version()
    print(f"✓ Phiên bản Chrome: {chrome_version}")
    print()
    
    # Lấy URL download
    url, driver_version = get_chromedriver_download_url(chrome_version)
    
    if not url:
        print("❌ Không thể tìm URL download. Vui lòng tải thủ công từ:")
        print("   https://googlechromelabs.github.io/chrome-for-testing/")
        return
    
    print(f"✓ Tìm thấy ChromeDriver version: {driver_version}")
    print()
    
    # Tải ChromeDriver
    zip_path = download_chromedriver(url, driver_version)
    
    if not zip_path:
        return
    
    # Giải nén
    if extract_chromedriver(zip_path):
        # Cập nhật config
        update_config()
        
        print()
        print("=" * 60)
        print("🎉 HOÀN TẤT!")
        print("=" * 60)
        print("✅ ChromeDriver đã được cài đặt tại: chromedriver.exe")
        print("✅ config.json đã được cập nhật")
        print()
        print("Bạn có thể chạy chương trình chính:")
        print("   python main.py")
    else:
        print("❌ Cài đặt thất bại")


if __name__ == "__main__":
    main()
