import requests
from bs4 import BeautifulSoup

def get_movie_info(url_receive):
    headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36'
    }
    data = requests.get(url_receive, headers=headers)
    soup = BeautifulSoup(data.text, 'html.parser')
    title = soup.select_one('meta[property="og:title"]')['content']
    image = soup.select_one('div.cm_info_box > div.detail_info > a > img')['src']
    desc = soup.select_one('div.cm_info_box > div.detail_info > div > span').get_text()
    
    return title, image, desc