import time
import libtorrent
from .. import const


class DownloadHandler(object):
    """Download handler"""

    def __init__(self, session, handle):
        self._session = session
        self._handle = handle

    @property
    def finished(self):
        """Is finished"""
        return self._handle.status().state == libtorrent.torrent_status.seeding

    @property
    def percent(self):
        """Downloading percent"""
        return self._handle.status().progress * 100

    def remove(self):
        """Remove torrent"""
        self._session.remove_torrent(self._handle)


class DownloadSeries(object):
    """Download series"""

    def download(self, episode):
        """Download episode"""
        session = libtorrent.session()
        handle = libtorrent.add_magnet_uri(
            session, episode.magnet, {
                'save_path': const.DOWNLOAD_PATH,
            }
        )
        while not handle.has_metadata():
            time.sleep(0.5)
        handle.rename_file(0, episode.file_name)
        return DownloadHandler(session, handle)