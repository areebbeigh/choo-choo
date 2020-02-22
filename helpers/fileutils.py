import tempfile

def tmpfile(data=None, suffix=None):
    """Returns a tempfile.NamedTemporaryFile with given data and suffix."""
    rv = tempfile.NamedTemporaryFile(suffix=suffix)
    if data:
        rv.write(bytes(data, 'utf-8'))
        rv.file.flush()
    return rv
