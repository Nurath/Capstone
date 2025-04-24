import internetarchive
import requests
import os

def download_manual_from_archive(keyword, save_dir="manuals"):
    results = internetarchive.search_items(f'{keyword} AND mediatype:texts')
    for result in results:
        identifier = result['identifier']
        item = internetarchive.get_item(identifier)
        files = item.files

        for file in files:
            name = file['name']
            if name.endswith('.pdf'):
                url = f'https://archive.org/download/{identifier}/{name}'
                os.makedirs(save_dir, exist_ok=True)
                filepath = os.path.join(save_dir, name)

                with requests.get(url, stream=True) as r:
                    r.raise_for_status()
                    with open(filepath, 'wb') as f:
                        for chunk in r.iter_content(chunk_size=8192):
                            f.write(chunk)
                return filepath  # Return path to downloaded PDF
    return None