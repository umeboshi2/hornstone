import os
import uuid as UUID

#from useless.base.path import path
from unipath.path import Path as path
from unipath import FILES, DIRS, LINKS

FILE_EXTENSIONS = ['jpg', 'png', 'gif']

class UrlRepo(object):
    def __init__(self, repo_path):
        self.repo_path = path(repo_path)
        
    def get_uuid(self, url):
        return UUID.uuid5(UUID.NAMESPACE_URL, bytes(url))

    def _get_top_bottom(self, uuid):
        h = uuid.hex
        return tuple(h.split(h[2:-2]))
    
    def _repos_dir(self, url, uuid=None):
        if uuid is None:
            uuid = self.get_uuid(url)
        top, bottom = self._get_top_bottom(uuid)
        return os.path.join(self.repo_path, top, bottom)

    def _basename(self, url, uuid):
        for e in FILE_EXTENSIONS:
            if url.endswith('.%s' % e):
                return '%s.%s' % (uuid.hex, e)
        return uuid.hex

    def _repos_name(self, url):
        uuid = self.get_uuid(url)
        dirname = self._repos_dir(url, uuid)
        basename = self._basename(url, uuid)
        return os.path.join(dirname, basename)
    
    def relname(self, url):
        uuid = self.get_uuid(url)
        top, bottom = self._get_top_bottom(uuid)
        return os.path.join(top, bottom, self._basename(url, uuid))

    def file_exists(self, url):
        return os.path.isfile(self._repos_name(url))
    
    def filename(self, url):
        return self._repos_name(url)

    def open_file(self, url, mode='rb'):
        filename = self._repos_name(url)
        dirname = os.path.dirname(filename)
        if not os.path.isdir(dirname):
            os.makedirs(dirname)
        return file(filename, mode)
        
        
