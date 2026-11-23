"""Check a standalone export when an interface uses two new shared method files."""
import sys
import tempfile
from pathlib import Path
from unittest.mock import patch

sys.path.insert(0,str(Path(__file__).resolve().parents[2]))
from migration import export_method


def check_method_directory_export(root):
    base = root/'upstream/acycle'
    packages = root/'matlab/+acmethods'
    fixture = {
        'code/method/acFixtureOuter.m': 'function x=acFixtureOuter(x), x=acFixtureInner(x); end',
        'code/method/acFixtureInner.m': 'function x=acFixtureInner(x), x=x+1; end',
        'code/method/acFixtureUnused.m': 'function x=acFixtureUnused(x), end',
        'matlab/+acmethods/+Test/analyzer.m': 'function x=analyzer(x), x=acFixtureOuter(x); end',
        'matlab/+acmaster/+Test/analyzer.m': 'function x=analyzer(x), x=acFixtureOuter(x); end',
        'matlab/logger.m': '', 'LICENSE': '', 'migration/recovered.tsv': '',
        'upstream/acycle/README.md': '', 'upstream/master/README.md': '',
        'upstream/master/ac.m': '', 'upstream/master/data/La04.mat': '',
        'upstream/master/code/seriesanalysis/acycleSamplingIsUneven.m': '',
    }
    for name, contents in fixture.items():
        path = root/name
        path.parent.mkdir(parents=True,exist_ok=True)
        path.write_text(contents,encoding='utf-8')
    with patch.multiple(export_method,ROOT=root,PACKAGES=packages,BASE=base,HIST=root/'upstream/recovered/code'):
        for version in ('guide','master'):
            out = root/('export-'+version)
            export_method.export(['Test'],out,version)
            for name in ('acFixtureOuter.m','acFixtureInner.m'):
                assert (out/'code/method'/name).read_bytes() == (root/'code/method'/name).read_bytes()
            assert (out/'code/method/acFixtureUnused.m').exists() == (version=='master')
            assert "'code/method'" in (out/'setup_method.m').read_text()


if __name__ == '__main__':
    with tempfile.TemporaryDirectory() as directory:
        check_method_directory_export(Path(directory))
    print('Verified code/method export for GUIDE and master.')
