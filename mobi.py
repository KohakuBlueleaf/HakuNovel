from mobinovel.api import get_list_of_epub
from ctfile.api import download_file
from config import config

import os
import asyncio


async def main():
    bname = input('book name in url: ')
    
    path = os.path.join(config["download_folder"], bname)
    if not os.path.isdir(path):
        os.makedirs(path)
        
    links = await get_list_of_epub(bname)
    for i in links[12:]:
        while True:
            try:
                name, raw = await download_file(i, '6195')
                break
            except Exception as e:
                raise e
                pass
        with open(os.path.join(path, name), 'wb') as f:
            f.write(raw)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(main())