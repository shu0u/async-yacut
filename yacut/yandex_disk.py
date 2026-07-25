import asyncio
import urllib.parse

import aiohttp
import requests

from . import app

DISK_TOKEN = app.config['DISK_TOKEN']
API_HOST = 'https://cloud-api.yandex.net/'
API_VERSION = 'v1'

REQUEST_UPLOAD_URL = f'{API_HOST}{API_VERSION}/disk/resources/upload'
DOWNLOAD_LINK_URL = f'{API_HOST}{API_VERSION}/disk/resources/download'

AUTH_HEADERS = {'Authorization': f'OAuth {DISK_TOKEN}'}


async def get_upload_url(session, filename):
    params = {
        'path': 'app:/' + filename,
        'overwrite': 'True',
    }
    async with session.get(
        REQUEST_UPLOAD_URL,
        headers=AUTH_HEADERS,
        params=params,
    ) as response:
        data = await response.json()
        return data['href']


async def upload_to_disk(session, upload_url, file_data):
    async with session.put(upload_url, data=file_data) as response:
        location = response.headers.get('Location', '')
        location = urllib.parse.unquote(location)
        location = location.replace('/disk', '')
        return location


async def get_download_url(session, path):
    params = {'path': path}
    async with session.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params=params,
    ) as response:
        data = await response.json()
        return data.get('href', '')


async def upload_file_and_get_link(session, filename, file_data):
    upload_url = await get_upload_url(session, filename)
    path = await upload_to_disk(session, upload_url, file_data)
    if not path:
        path = f'/Приложения/Uploader/{filename}'
    download_url = await get_download_url(session, path)
    return filename, path, download_url


async def async_upload_files_to_disk(files):
    results = []
    if files is not None:
        async with aiohttp.ClientSession() as session:
            tasks = []
            for file in files:
                file_data = file.read()
                tasks.append(
                    asyncio.ensure_future(
                        upload_file_and_get_link(
                            session, file.filename, file_data
                        )
                    )
                )
            results = await asyncio.gather(*tasks)
    return results


def get_download_url_sync(path):
    response = requests.get(
        DOWNLOAD_LINK_URL,
        headers=AUTH_HEADERS,
        params={'path': path},
    )
    data = response.json()
    return data.get('href', '')
