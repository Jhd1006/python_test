import pytest

from utils import get_movie_info

def test_get_movie_info():
    test_url = "https://movie.naver.com/movie/bi/mi/basic.nhn?code=185293"
    title, image, desc = get_movie_info(test_url)
    print(title)
    print(image)
    print(desc)
    assert title == "내일의 기억 : 네이버 검색"