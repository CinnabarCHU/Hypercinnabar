"""Fetch optional orbital tables used by the pinned Acycle GUI."""
import argparse
from hashlib import sha256
from io import BytesIO
from pathlib import Path
import os
from tempfile import NamedTemporaryFile
from urllib.request import urlopen

from scipy.io import savemat
import numpy as np

HERE = Path(__file__).resolve().parent
ZEEBE = 'https://www.soest.hawaii.edu/oceanography/faculty/zeebe_files/Astro/'
NOAA = 'https://www.ncei.noaa.gov/pub/data/paleo/climate_forcing/orbital_variations/insolation/orbit91'


def get(url, digest):
    with urlopen(url, timeout=60) as stream:
        raw = stream.read()
    if sha256(raw).hexdigest() != digest:
        raise ValueError(f'Published source bytes differ from the verified table: {url}')
    return raw


def put(path, raw):
    with NamedTemporaryFile(dir=path.parent, delete=False) as tmp:
        staged = Path(tmp.name)
        try:
            tmp.write(raw)
            tmp.close()
            os.replace(staged,path)
        finally:
            staged.unlink(missing_ok=True)


def fetch(destination):
    destination.mkdir(parents=True,exist_ok=True)
    for record in (HERE / 'orbits.sha256').read_text().splitlines():
        digest, name = record.split()
        target = destination / name
        if target.is_file() and sha256(target.read_bytes()).hexdigest() == digest:
            raw = target.read_bytes()
        else:
            if target.exists():
                raise FileExistsError(f'{target} contains different data')
            raw = get(NOAA if name=='orbit91' else ZEEBE+name, digest)
            put(target,raw)
        if name == 'orbit91':
            orbit = np.loadtxt(BytesIO(raw),skiprows=2)
            assert orbit.shape==(5001,9) and orbit[0,1]==.017236 and orbit[-1,0]==-5000
            # insoML.m lines 57–67 consume the unmodified table under the variable Orbit.
            product = destination / 'BergerLoutre1991.mat'
            if product.exists():
                from scipy.io import loadmat
                if not np.array_equal(loadmat(product).get('Orbit'),orbit):
                    raise FileExistsError(f'{product} contains different data')
            else:
                output=BytesIO()
                savemat(output,{'Orbit':orbit},do_compression=True)
                put(product,output.getvalue())
        print(name, digest)


if __name__ == '__main__':
    parser=argparse.ArgumentParser(description=__doc__)
    parser.add_argument('directory',type=Path)
    fetch(parser.parse_args().directory)
