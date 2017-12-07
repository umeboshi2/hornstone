import os
import uuid as UUID

from unipath.path import Path as path

from hornstone.base import get_sha256sum_string

FILE_EXTENSIONS = ['jpg', 'png', 'gif']


class ImageRepo(object):
    def __init__(self, repo_path):
        self.repo_path = path(repo_path)

    def _get_top_bottom(self, uuid):
        h = uuid.hex
        return tuple(h.split(h[2:-2]))

    def _repo_dir(self, checksum):
        top, bottom = self._get_top_bottom(checksum)
        return os.path.join(self.repo_path, top, bottom)

    def relname(self, checksum, ext):
        # top, bottom = self._get_top_bottom(checksum)
        # return os.path.join(top, bottom, checksum)
        return '%s.%s' % (checksum, ext)

    def filename(self, checksum, ext):
        # dirname = self._repo_dir(checksum)
        # return os.path.join(dirname, checksum)
        return os.path.join(self.repo_path, '%s.%s' % (checksum, ext))

    def file_exists(self, checksum, ext):
        filename = self.filename(checksum, ext)
        return os.path.isfile(filename)

    def get_checksum_content(self, content):
        return get_sha256sum_string(content)

    def import_content(self, content, ext):
        checksum = self.get_checksum_content(content)
        filename = self.filename(checksum, ext)
        if os.path.isfile(filename):
            raise RuntimeError("File already exists %s" % checksum)
        with open(filename, 'wb') as outfile:
            outfile.write(content)

    def open(self, checksum, ext, mode='rb'):
        filename = self.filename(checksum, ext)
        return open(filename, mode)

    def delete(self, checksum, ext):
        if self.file_exists(checksum, ext):
            os.remove(self.filename(checksum, ext))

    def delete_all(self):
        for basename in os.listdir(self.repo_path):
            filename = os.path.join(self.repo_path, basename)
            if os.path.isfile(filename):
                os.remove(filename)


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
        return open(filename, mode)
