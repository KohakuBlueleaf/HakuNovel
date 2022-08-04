from bs4 import BeautifulSoup as Soup
import asyncio

from utils import aio_get

API = 'https://www.mobinovels.com/{}/'


async def get_list_of_epub(bname: str) -> list[str]:
    '''Get epub link from mobi website'''
    data, _ = await aio_get(API.format(bname))
    soup = Soup(bytes.decode(data), features="html.parser")
    links = [
        row.find_all('a')[-1]['href'].split('?')[0]
        for row in soup.find('table').find_all('tr') 
        if row.find('a')
    ]
    
    return [str(i).split('/')[-1] for i in links]


async def main():
    bname = 'so-im-a-spider-so-what'
    links = await get_list_of_epub(bname)
    print(links)


if __name__ == '__main__':
    asyncio.new_event_loop().run_until_complete(main())