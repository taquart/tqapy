# fsf class and global routines for handling FSF files
import struct
import numpy as np
import datetime
import matplotlib.pyplot as plt

# The Fsf class aims to provide an easy interface to handle FSF files in Python. The class reads and decompose
# FSF file into three dictionary-style elements. The header data contains basic header information in a form of
# dictionary array. Channels is a list of channels dictionaries containing channel information. Finally, the
# waveform is a list of numpy arrays.

# The idea for developing the class is to provide parallel interface in a form of a class, and in the form of
# external routines for full flexibility in module usage. This means the the module routine plotmap(.) has its
# counterpart in Fsf.plotmap(.)


class Fsf:
    def __init__(self, filename):
        self.header, self.channels, self.waveforms = read(filename)
        self.filename = filename

    def getmarkertime(self, channel, markername, return_time="relative"):
        return getmarkertime(self.header, self.channels, channel, markername, return_time)

    def plotmap(self, ploteq=True):
        plotmap(self.header, self.channels, ploteq)

    def plot(self, channelrange="all"):
        plot(self.channels, self.waveforms, channelrange)


def plot(channels, waveforms, channelrange="all"):
    """plot seismograms """
    if type(channelrange) == str:
        channelrange = list(range(channels.__len__()))

    n_plots = channelrange.__len__()
    fig, axs = plt.subplots(n_plots, 1)
    k = 0
    for ch in channelrange:
        axs[k].plot(waveforms[ch])
        label_y = channels[ch]['name']+':'+channels[ch]['component']
        axs[k].set(ylabel=label_y, yticks=[])
        k = k + 1
    plt.show()


def plotmap(header, channels, ploteq=True):
    """plot map with event and station positions"""
    x = [d['x'] for d in channels if 'x' in d]
    y = [d['y'] for d in channels if 'y' in d]

    fig, ax = plt.subplots()
    ax.scatter(x, y, marker='^', color='black')
    if ploteq:
        ax.scatter(header['x'], header['y'], marker='o', color='r')
    ax.set(xlabel='x', ylabel='y', title='map view')
    ax.grid()
    fig.tight_layout()
    plt.show()


def getmarkertime(header, channels, channel, markername, return_time="relative"):
    """get marker relative time, absolute time or marker position from a specific channel"""

    try:
        k = channels[channel]['markertype'].index(markername)
    except ValueError:
        return

    if return_time is 'relative':
        return channels[channel]['markertime'][k]
    elif return_time is 'absolute':
        return header['dt']+datetime.timedelta(seconds=channels[channel]['markertime'][k])
    elif return_time is 'index':
        return round(channels[channel]['markertime'][k] * channels[channel]['sr'])
    else:
        pass  # TODO: do exception here?


def read(filename):
    """read FSF file format version 1.1 or 1.3"""

    with open(filename, 'rb') as fid:

        # read header information
        fid.read(13)  # skip header information
        version = str(struct.unpack('3s', fid.read(3))[0], 'utf-8')  # version number
        tlen = struct.unpack('i', fid.read(4))[0]
        filename = str(fid.read(tlen), 'utf-8')  # filename
        channelcount = struct.unpack('i', fid.read(4))[0]  # number of channels
        coordinates = struct.unpack('3d', fid.read(8*3))   # coordinates
        dtt = struct.unpack('7i', fid.read(7*4))   # date and time  day month year hour minute second milisecond

        if version is '1.3':
            coord_geographic = struct.unpack('ddd', fid.read(8*3))
        else:
            coord_geographic = (0.0, 0.0, 0.0)

        dt = datetime.datetime(dtt[2], dtt[1], dtt[0], dtt[3], dtt[4], dtt[5], dtt[6] * 1000)

        header = {'filename': filename, 'version': version, 'channels': channelcount, 'x': coordinates[0],
                  'y': coordinates[1], 'z': coordinates[2],
                  'year': dtt[2], 'month': dtt[1], 'day': dtt[0], 'hour': dtt[3], 'minute': dtt[4], 'second': dtt[5],
                  'milisecond': dtt[6], 'longitude': coord_geographic[0], 'latitude': coord_geographic[1],
                  'depth': coord_geographic[2], 'dt': dt}

        # read channel information
        channels = []
        for ch in range(channelcount):
            tlen = struct.unpack('i', fid.read(4))[0]
            name = str(fid.read(tlen), 'utf-8')
            ident = struct.unpack('i', fid.read(4))[0]
            tlen = struct.unpack('i', fid.read(4))[0]
            component = str(fid.read(tlen), 'utf-8')
            coordinates = struct.unpack('3d', fid.read(8 * 3))  # coordinates
            recounter = struct.unpack('d', fid.read(8))[0]
            length = struct.unpack('i', fid.read(4))[0]
            tlen = struct.unpack('i', fid.read(4))[0]
            datatype = str(fid.read(tlen), 'utf-8')
            active = struct.unpack('i', fid.read(4))[0]
            gain_sens_damp = struct.unpack('3d', fid.read(8 * 3))
            sr = struct.unpack('i', fid.read(4))[0]

            if version == '1.1' or version == '1.3':
                markertype = list(struct.unpack('50i', fid.read(50 * 4)))
                markertime = list(struct.unpack('50d', fid.read(50 * 8)))
            else:
                markertype = [0, ] * 50
                markertime = [0.0, ] * 50

            if version is '1.3':
                coord_geographic = struct.unpack('ddd', fid.read(8*3))
            else:
                coord_geographic = (0.0, 0.0, 0.0)

            channel = {'name': name, 'ident': ident, 'component': component, 'x': coordinates[0], 'y': coordinates[1],
                       'z': coordinates[2], 'calibration_constant': recounter, 'length': length,
                       'datatype': datatype, 'active': active, 'gain': gain_sens_damp[0],
                       'sensitivity': gain_sens_damp[1], 'damping': gain_sens_damp[2], 'sr': sr,
                       'markertype': markertype, 'markertime': markertime, 'longitude': coord_geographic[0],
                       'latitude': coord_geographic[1], 'depth': coord_geographic[2], 'dt': dt}
            channels.append(channel)

        # read waveform information
        waveforms = []
        for ch in range(channelcount):
            datatype = channels[ch]['datatype']
            length = channels[ch]['length']
            # TODO: FSF datatype string may not fully match Python datatype. Need to be ultimately replaced
            waveform = np.fromfile(fid, dtype=datatype, count=length)
            waveforms.append(waveform)

        fid.close()

        return header, channels, waveforms
