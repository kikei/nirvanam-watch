from zipfile import ZipFile
from tempfile import NamedTemporaryFile

def get_manifest_json():
    return """{{
    "version": "1.0.0",
    "manifest_version": 2,
    "name": "Chrome Proxy",
    "permissions": [
        "proxy",
        "tabs",
        "unlimitedStorage",
        "storage",
        "<all_urls>",
        "webRequest",
        "webRequestBlocking"
    ],
    "background": {{
        "scripts": ["background.js"]
    }},
    "minimum_chrome_version":"22.0.0"
}}""".format()

def get_background_js(host, port, username, password):
    return """var config = {{
  mode: "fixed_servers",
  rules: {{
    singleProxy: {{
      scheme: "http",
      host: "{host}",
      port: {port}
    }},
    bypassList: []
  }}
}};

chrome.proxy.settings.set({{value: config, scope: "regular"}}, function() {{}});

function callbackFn(details) {{
    return {{
        authCredentials: {{
            username: "{username}",
            password: "{password}"
        }}
    }};
}}

chrome.webRequest.onAuthRequired.addListener(
        callbackFn,
        {{urls: ["<all_urls>"]}},
        ['blocking']
);""".format(host=host, port=port, username=username, password=password)

class ChromeProxy:
    def __init__(self, host, port, username, password):
        self.host = host
        self.port = port
        self.username = username
        self.password = password

    def generate_extension(self, extpath):
        with ZipFile(extpath, 'w') as zip:
            zip.writestr("manifest.json", get_manifest_json())
            zip.writestr("background.js",
                         get_background_js(host=self.host,
                                           port=self.port,
                                           username=self.username,
                                           password=self.password))

    
