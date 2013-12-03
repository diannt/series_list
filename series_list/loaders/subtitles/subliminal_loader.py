from functools import partial
import requests
from BeautifulSoup import BeautifulSoup
from babelfish import Language
from subliminal.api import save_subtitles
import subliminal
from ...models import Subtitle
from ...settings import config
from .. import library
from ..base import return_if_timeout, similarity
from .base import SubtitlesLoader


@library.subtitles
class SubliminalLoader(SubtitlesLoader):
    """Subliminal loader with subtitleseeker checker"""

    def _get_search_page_url(self, name):
        """Get search page url"""
        return u'http://www.subtitleseeker.com/search/TV_EPISODES/{}'.format(
            name,
        )

    def _fetch_search_page(self, name):
        """Fetch search page"""
        return requests.get(
            self._get_search_page_url(name), timeout=config.subtitle_timeout,
        ).content

    def _get_episode_url(self, html, name):
        """Get episode url"""
        soup = BeautifulSoup(html)
        boxes = soup.findAll('div', {'class': 'boxRowsInner'})
        matcher = partial(similarity, second=name)
        max_match = max(boxes, key=lambda box: matcher(
            box.find('a', {
                'class': 'blue',
            }).text,
        ))
        url = max_match.find('a', {'class': 'red'})['href']
        return u'{}English/'.format(url)

    def _fetch_episode(self, url):
        """Fetch episode page"""
        return requests.get(url).content

    def _check_subtitles_exists(self, html):
        """Check subtitles exists"""
        soup = BeautifulSoup(html)
        if soup.find('div', {'class': 'boxRowsInner'}):
            return True
        else:
            return False

    @return_if_timeout(None)
    def get_subtitle_url(self, name):
        """Always return ok"""
        html = self._fetch_search_page(name)
        try:
            episode_url = self._get_episode_url(html, name)
        except (AttributeError, ValueError):
            return None
        episode_html = self._fetch_episode(episode_url)
        if self._check_subtitles_exists(episode_html):
            return Subtitle(
                name=name,
                wait_for_file=True,
            )
        else:
            return None

    def download(self, model):
        """Download subtitles using subliminal"""
        video = subliminal.scan_video(model.series.path)
        subtitles = subliminal.download_best_subtitles(
            {video}, {Language('eng')},
        )
        save_subtitles(subtitles, True, config.download_path)
