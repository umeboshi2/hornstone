import pickle
import json
import uuid
from pathlib import Path
from bs4 import BeautifulSoup
from ..util import json_serial

# https://github.com/jmcarp/robobrowser/issues/96
# workaround issue with a monkeypatch
import werkzeug
werkzeug.cached_property = werkzeug.utils.cached_property
import robobrowser  # noqa:E402


def make_uuid_from_url(url):
    return uuid.uuid5(uuid.NAMESPACE_URL, url)


def load_json(filename):
    return json.load(open(filename, 'rb'))


def load_pickle(filename):
    return pickle.load(open(filename, 'rb'), encoding='utf8')


def dump_json(data, fileobj):
    json.dump(data, fileobj)


def dump_pickle(data, fileobj):
    pickle.dump(data, fileobj)


LOADERS = dict(json=load_json, pickle=load_pickle)
MODULES = dict(json=json, pickle=pickle)


class BaseCollector(object):
    def __init__(self):
        self.browser = robobrowser.RoboBrowser(parser='lxml')
        self.url = None
        self.response = None
        self.pageinfo = None
        self.content = ''
        self.soup = None

    def _make_soup(self, content):
        return BeautifulSoup(content, 'lxml')

    def retrieve_page(self, url=None):
        if url is None:
            if self.url is None:
                raise RuntimeError("No url set.")
            url = self.url
        else:
            self.url = url
        self.response = self.browser.open(url)
        # self.info = self.browser.response.headers
        self.info = dict()
        for key in self.browser.response.headers:
            self.info[key.lower()] = self.browser.response.headers[key]
        self.content = self.browser.response.content
        self.soup = self.browser.parsed

    def set_url(self, url):
        self.url = url
        self.response = None
        self.pageinfo = None
        self.content = ''
        self.soup = None


class CacheCollector(BaseCollector):
    def __init__(self, cachedir='cache', format='pickle'):
        super(CacheCollector, self).__init__()
        self.cachedir = Path(cachedir)
        if not self.cachedir.exists():
            self.cachedir.mkdir(parents=True)
        self.format = format

    def filename(self, url):
        filename = '{}.{}'.format(make_uuid_from_url(url), self.format)
        return self.cachedir / filename

    def _load_json(self, filename):
        return json.load(filename.open('r'))

    def _load_pickle(self, filename):
        return pickle.load(filename.open('rb'))

    def get_from_cache(self, url):
        filename = self.filename(url)
        if filename.exists():
            if self.format == 'json':
                return self._load_json(filename)
            elif self.format == 'pickle':
                return self._load_pickle(filename)
            else:
                raise RuntimeError('bad format: {}'.format(self.format))
        else:
            return None

    def _dump_json(self, data, filename):
        with filename.open('w') as outfile:
            json.dump(data, outfile, default=json_serial)

    def _dump_pickle(self, data, filename):
        with filename.open('wb') as outfile:
            pickle.dump(data, outfile)

    def save_to_cache(self, url):
        self.retrieve_page(url)
        data = dict(info=self.info, content=self.content, url=self.url)
        filename = self.filename(url)
        if self.format == 'json':
            self._dump_json(data, filename)
        elif self.format == 'pickle':
            self._dump_pickle(data, filename)
        else:
            raise RuntimeError("unknown format {}".format(self.format))
