from tqa import fsf

# read FSF file into a class object fsf
# alternative but obsolete code would be: head, channel, waveform = fsf.read('s0001585.fsf')

# read the FSF file and instantiate the fsf object. This will create an object with header, channel and waveform
# structures inside of the class.
fsffile = fsf.Fsf('s0001585.fsf')

# plot stations
fsffile.plotmap()

# get P-wave marker position.
p_marker_relative = fsffile.getmarkertime(0, 1)
print('p-wave marker time', p_marker_relative)

# one can get the marker index...
p_marker_index = fsffile.getmarkertime(0, 1, 'index')
print('p-wave marker time', p_marker_index)

# ...as well as marker absolute time.
p_marker_absolute = fsffile.getmarkertime(0, 1, 'absolute')
print('p-wave marker time', p_marker_absolute)




# fig, axs = plt.subplots(3, 1)
# axs[0].plot(waveform[0])
# axs[1].plot(waveform[1])
# axs[2].plot(waveform[2])
# plt.show()
