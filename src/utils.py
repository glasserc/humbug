import hashlib

BLOCKSIZE = 50*1024*1024
def md5_file(filename):
    hash = hashlib.md5()
    f = file(filename)
    while True:
        s = f.read(BLOCKSIZE)
        if s == '':
            break
        hash.update(s)

    return hash.hexdigest()
