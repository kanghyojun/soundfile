from soundfile import CheapMP3


def test_file_len():
    o = CheapMP3('/Users/admire/Desktop/goback.mp3')
    assert 11340329 == o.file_len


def test_read():
    with CheapMP3('/Users/admire/Desktop/goback.mp3') as o:
        print(dir(o.file))
        o.read_file()
        assert False
