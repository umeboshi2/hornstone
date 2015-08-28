import hashlib

def chunks(l, n):
    """ Yield successive n-sized chunks from l.
    """
    for i in xrange(0, len(l), n):
        yield l[i:i+n]

def get_sha256sum_orig(fileobj):
    s = hashlib.new('sha256')
    while True:
        block = fileobj.read(4096)
        if not block:
            break
        s.update(block)
    return s.hexdigest()

def get_sha256sum(fileobj):
    s = hashlib.new('sha256')
    block = fileobj.read(4096)
    while block:
        s.update(block)
        block = fileobj.read(4096)
    return s.hexdigest()

def remove_trailing_slash(pathname):
    while pathname.endswith('/'):
        pathname = pathname[:-1]
    return pathname
