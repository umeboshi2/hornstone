import hashlib

def get_sha256sum(fileobj):
    s = hashlib.new('sha256')
    while True:
        block = fileobj.read(4096)
        if not block:
            break
        s.update(block)
    return s.hexdigest()

def remove_trailing_slash(pathname):
    while pathname.endswith('/'):
        pathname = pathname[:-1]
    return pathname
