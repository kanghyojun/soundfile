from soundfile import CheapMP3


def test_file_len():
    with CheapMP3('./tests/assets/loststar.mp3') as o:
        assert 10908970 == o.file_len


def test_read():
    with CheapMP3('./tests/assets/loststar.mp3') as o:
        l = o.read_file()
        assert 63 == len(o.frame_gains)
        assert 0 == o.frame_gains


def test_2read():
    with CheapMP3('./tests/assets/loststar.mp3') as o:
        l = o.read_file()
        assert 0 < o.num_frames
        assert 66 == len(o.frame_gains)
