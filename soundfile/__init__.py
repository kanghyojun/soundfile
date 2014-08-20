import os

from array import array


class CheapMP3(object):

    BITRATES_MPEG1_L3 = [
        0, 32, 40, 48, 56, 64, 80, 96,
        112, 128, 160, 192, 224, 256, 320, 0
    ]

    BITRATES_MPEG2_L3 = [
        0, 8, 16, 24, 32, 40, 48, 56,
        64, 80, 96, 112, 128, 144, 160, 0
    ]

    SAMPLERATES_MPEG1_L3 = [44100, 48000, 32000, 0]

    SAMPLERATES_MPEG2_L3 = [22050, 24000, 16000, 0]

    channels = 0

    sample_rate = 0

    bitrate_sum = 0

    num_frames = 0

    frame_offsets = array('i')

    frame_lens = array('f')

    frame_gains = array('i')

    min_gain = 0

    max_gain = 0

    avg_bitrate = 0

    def __init__(self, filename):
        self.file = open(filename, 'rb')
        self.file_len = os.path.getsize(filename)


    def grow(self, name, size):
        i = 0
        while i < size:
            getattr(self, name, []).append(0)
            i += 1


    def read_file(self):
        pos = 0
        s = 12
        offset = 0
        self.max_frames = 64
        self.grow('frame_offsets', self.max_frames)
        self.grow('frame_lens', self.max_frames)
        self.grow('frame_gains', self.max_frames)
        buffer_ = bytearray(12)
        while pos < self.file_len - 12:
            buffer_ = bytearray(self.file.read(12))
            buffer_offset = 0
            if len(buffer_) < 12:
                break
            while buffer_offset < 12 and buffer_[buffer_offset] != 0xFF:
                buffer_offset = buffer_offset + 1

            if buffer_offset > 0:
                i = 0
                while i < 12 - buffer_offset:
                    buffer_[i] = buffer_[buffer_offset + i]
                    i += 1
                pos += buffer_offset
                offset = 12 - buffer_offset
                big += 1
                self.file.seek(int(pos))
                continue

            mpg_version = 0
            if buffer_[1] == 0xFA or buffer_[1] == 0xFB:
                mpg_version = 1
            elif buffer_[1] == 0xF2 or buffer_[1] == 0xF3:
                mpg_version = 2
            else:
                buffer_offset = 1
                while i < 12 - buffer_offset:
                    buffer_[i] = buffer_[buffer_offset + i]
                    i += 1
                pos += buffer_offset
                offset = 12 - buffer_offset
                continue

            if mpg_version == 1:
                bit_rate = self.BITRATES_MPEG1_L3[(buffer_[2] & 0xF0) >> 4]
                sample_rate = self.SAMPLERATES_MPEG1_L3[(buffer_[2] & 0x0C) >> 2]
            else:
                bit_rate = self.BITRATES_MPEG2_L3[(buffer_[2] & 0xF0) >> 4]
                sample_rate = self.SAMPLERATES_MPEG2_L3[(buffer_[2] & 0x0C) >> 2]

            if bit_rate == 0 or sample_rate == 0:
                buffer_offset = 2
                while i < 12 - buffer_offset:
                    buffer_[i] = buffer_[buffer_offset + i]
                    i += 1
                pos += buffer_offset
                offset = 12 - buffer_offset
                continue

            self.sample_rate = sample_rate
            padding = (buffer_[2] & 2) >> 1
            frame_len = 144 * bit_rate * 1000 / sample_rate + padding
            chan = buffer_[3] & 0xC0
            gain = 0
            if chan == 0xC0:
                self.channels = 1
                if mpg_version == 1:
                    gain = (((buffer_[10] & 0x01) << 7) +
                            ((buffer_[11] & 0xFE) >> 1))
                else:
                    gain = (((buffer_[9] & 0x03) << 6) +
                            ((buffer_[10] & 0xFC) >> 2))
            else:
                self.channels = 2;
                if mpg_version == 1:
                    gain = (((buffer_[9]  & 0x7F) << 1) +
                            ((buffer_[10] & 0x80) >> 7))

            self.bitrate_sum += bit_rate
            pos = int(pos)
            self.frame_offsets[self.num_frames] = pos
            self.frame_lens[self.num_frames] = frame_len
            self.frame_gains[self.num_frames] = gain
            if gain < self.min_gain:
                self.min_gain = gain
            if gain > self.max_gain:
                self.max_gain = gain

            self.num_frames = self.num_frames + 1
            if self.num_frames == self.max_frames:
                self.avg_bitrate = self.bitrate_sum / self.num_frames
                guess = (self.file_len / self.avg_bitrate) * sample_rate
                total_frame_guess = guess / 144000
                new_max_frames = total_frame_guess * 1.1
                if new_max_frames < self.max_frames * 2:
                    new_max_frames = self.max_frames * 2
                size = new_max_frames - self.num_frames
                self.grow('frame_offsets', size)
                self.grow('frame_lens', size)
                self.grow('frame_gains', size)

            self.file.read(int(frame_len) - 12)
            pos += frame_len
            offset = 0


    def __enter__(self):
        return self


    def __exit__(self, type, value, traceback):
        self.file.close()
