import urllib.request
import json

class PyPIHandler:
    def __init__(self):
        self.base_url = "https://pypi.org/pypi/"

    def package_exists(self, package_name):
        try:
            url = f"{self.base_url}{package_name}/json"
            with urllib.request.urlopen(url) as response:
                if response.getcode() == 200:
                    return True
        except urllib.error.HTTPError as e:
            if e.code == 404:
                return False
            print(f"[ ! ] API PyPI Error: {e}")
        except Exception as e:
            print(f"[ ! ] Network error {e}")
        return False

    def get_package_info(self, package_name):
        try:
            url = f"{self.base_url}{package_name}/json"
            with urllib.request.urlopen(url) as response:
                data = json.loads(response.read().decode())
                return {
                    "version": data['info']['version'],
                    "summary": data['info']['summary']
                }
        except Exception:
            return None
