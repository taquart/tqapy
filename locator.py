from tqa import fsf


def get_phasedata(fsffile, markertypes):
    phases = []
    for i, ch in enumerate(fsffile.channels):
        for mtype in markertypes:
            mtime = fsffile.getmarkertime(i, mtype)
            if mtime is not None:
                phase = {'name': ch["name"], 'component': ch["component"], 'x': ch["x"], 'y': ch["y"],
                         'z': ch["z"], 'type': mtype, 'time': mtime}
                phases.append(phase)
    return phases
