from urllib import urlencode
from BeautifulSoup import BeautifulSoup
import requests
from ...settings import config
from ..base import return_if_timeout
from .. import library
from .base import PostersLoader


@library.posters
class IMDBPosterLoader(PostersLoader):
    """IMDb poster loader"""
    default_poster = 'http://ia.media-imdb.com/images/G/01/imdb/'\
        'images/nopicture/32x44/film-3119741174._V379391527_.png'
    cache = {}

    def _get_url(self, name):
        """Get url for fetching"""
        return 'http://www.imdb.com/find?{}'.format(
            urlencode({'q': name, 's': 'all'}),
        )

    def _fetch_html(self, name):
        """Fetch html"""
        return requests.get(
            self._get_url(name), timeout=config.poster_timeout,
        ).content

    def _parse_html(self, html):
        """Extract image from html"""
        soup = BeautifulSoup(html)
        return soup.find('td', {'class': 'primary_photo'}).find('img')['src']

    @return_if_timeout(default_poster)
    def get_poster(self, name):
        """Get poster"""
        html = self._fetch_html(name)
        try:
            return self._parse_html(html)
        except AttributeError:
            return self.default_poster

    def _fetch_poster_data(self, url):
        """Fetch poster data"""
        if not url in self.cache:
            self.cache[url] = requests.get(
                url, timeout=config.poster_timeout,
            ).content
        return self.cache[url]

    @return_if_timeout('get_default_poster_data', is_method=True)
    def get_poster_data(self, name):
        """Get poster data"""
        url = self.get_poster(name)
        return self._fetch_poster_data(url)

    def get_default_poster_data(self):
        """Get default poster data"""
        return self._fetch_poster_data(self.default_poster)