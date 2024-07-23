#!/usr/bin/env python3
import os
import urllib.parse
import requests
from core.banner import info, success, warn, error

def download(url, destination=None):
    response = requests.get(url, stream=True, timeout=15)
    response.raise_for_status()
    if not destination:
        parsed = urllib.parse.urlparse(url)
        destination = os.path.basename(parsed.path) or 'downloaded_file'
    total_bytes = 0
    with open(destination, 'wb') as f:
        for chunk in response.iter_content(chunk_size=8192):
            if chunk:
                f.write(chunk)
                total_bytes += len(chunk)
    return (destination, total_bytes)

def run(args):
    url = args.url
    if not url:
        error('Remote URL (-u / --url) is required.')
        return 1
    info(f'Downloading remote resource from: {url}')
    try:
        dest, size = download(url, args.output)
        success(f"File successfully saved to '{dest}' ({size:,} bytes).")
        return 0
    except Exception as e:
        error(f'Download failed: {e}')
        return 1
