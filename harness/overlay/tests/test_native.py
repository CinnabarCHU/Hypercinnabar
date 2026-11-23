"""Native transport contracts. No test fabricates MATLAB numerical results."""
import hashlib
import importlib.util
import json
import os
from pathlib import Path

import pytest

from acycle_deepseek import native, tools

ROOT = Path(__file__).resolve().parents[1]
L = lambda value: {'kind': 'literal', 'value': value}
ENTRY = 'code/seriesanalysis/depthtotime.m'


def plan(**overrides):
    return {'steps': [{'id': 'convert', 'entrypoint': ENTRY,
                       'arguments': [L([1, 2]), L([[1, 0], [2, 10]])], 'nargout': 2}], **overrides}


def test_catalog_complete_and_parseable():
    data = native.catalog()
    assert data['summary']['files'] == 337
    assert len({e['id'] for e in data['entries']}) == 337
    assert len(data['menus']) == 115
    assert sum(data['summary']['interfaces'].values()) == 337
    ids = {e['id'] for e in data['entries']}
    for entry in data['entries']:
        assert len(entry['sha256']) == 64
        assert set(entry['dependencies']) <= ids
        assert entry['interface'] in {'call', 'gui', 'script', 'owner_only'}
        assert entry['validation'].endswith('not run in this fork')


def test_catalog_matches_pinned_checkout_when_available():
    source = os.environ.get('ACYCLE_TEST_SOURCE')
    if not source:
        pytest.skip('Set ACYCLE_TEST_SOURCE for source inventory parity, no MATLAB required')
    spec = importlib.util.spec_from_file_location('catalog_builder', ROOT / 'scripts/build_native_catalog.py')
    builder = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(builder)
    assert builder.build(source) == native.catalog()


def test_documented_examples_have_valid_transport_contracts():
    examples = sorted((ROOT / 'examples/native').glob('*.json'))
    assert len(examples) == 13
    for path in examples:
        native.validate_plan(json.loads(path.read_text()))


def test_catalog_discovery_and_pagination(tmp_path):
    first = tools.dispatch('acycle_catalog', {'limit': 3}, tmp_path)
    second = tools.dispatch('acycle_catalog', {'offset': first['next_offset'], 'limit': 3}, tmp_path)
    assert first['total_matches'] == 337
    assert set(e['id'] for e in first['entries']).isdisjoint(e['id'] for e in second['entries'])
    detail = tools.dispatch('acycle_catalog', {'entrypoint': ENTRY}, tmp_path)
    assert detail['entry']['inputs'] == ['depth', 'agemodel']
    assert not detail['runtime_validated']
    assert tools.dispatch('acycle_catalog', {'view': 'menus', 'query': 'EMD'}, tmp_path)['total_matches']


def test_new_tools_shared_by_cli_mcp_and_harness(tmp_path):
    from acycle_deepseek.mcp import handle
    names = {s['function']['name'] for s in tools.tool_schemas()}
    assert {'acycle_catalog', 'acycle_native'} <= names
    response = handle({'id': 1, 'method': 'tools/list'}, tmp_path)
    assert names == {t['name'] for t in response['result']['tools']}


@pytest.mark.parametrize('changes', [
    {'steps': []}, {'steps': 'not a list'}, {'seed': True}, {'seed': -1}, {'seed': 2**32},
    {'inputs': {'bad-name': 'file.csv'}}, {'inputs': {'good': 5}},
    {'steps': [{'id': 'x', 'entrypoint': 'system', 'arguments': [L('echo bad')]}]},
    {'steps': [{'id': 'x', 'entrypoint': 'code/package/undatable/private/udrun.m'}]},
    {'steps': [{'id': 'x', 'entrypoint': ENTRY, 'nargout': 3}]},
    {'steps': [{'id': 'x', 'entrypoint': ENTRY, 'nargout': True}]},
    {'steps': [{'id': 'x', 'entrypoint': ENTRY, 'arguments': [L(1), L(2), L(3)]}]},
    {'steps': [{'id': 'x', 'entrypoint': ENTRY, 'arguments': [1]}]},
    {'steps': [{'id': 'x', 'entrypoint': ENTRY, 'arguments': [{'kind': 'ref', 'step': 'later'}]}]},
    {'steps': [{'id': 'hn_hidden', 'entrypoint': ENTRY}]},
    {'steps': [{'id': 'x', 'entrypoint': ENTRY, 'unknown': True}]},
    {'steps': [{'id': 'x', 'entrypoint': 'code/misc/GETac_pwd.m'}]},
    {'steps': [{'id': 'x', 'action': 'script', 'entrypoint': ENTRY}]},
    {'steps': [{'id': 'x', 'action': 'ui_set', 'target': L(1), 'properties': {'Callback': L('bad')}}]},
    {'steps': [{'id': 'x', 'action': 'ui_invoke', 'target': L(1), 'callback': 'UserData'}]},
    {'dialogs': [{'name': 'inputdlg', 'outputs': [{'kind': 'ref', 'step': 'convert'}]}]},
])
def test_bad_plans_fail_before_matlab(changes):
    with pytest.raises((ValueError, TypeError)):
        native.validate_plan(plan(**changes))


@pytest.mark.parametrize('descriptor', [
    {'kind': 'array', 'data': [1, 2], 'shape': [3, 1]},
    {'kind': 'array', 'data': [1], 'shape': [1]},
    {'kind': 'array', 'data': ['NaN'], 'shape': [1, 1], 'dtype': 'int32'},
    {'kind': 'array', 'data': [float('nan')], 'shape': [1, 1]},
    {'kind': 'literal', 'value': float('inf')},
    {'kind': 'input', 'name': 'unknown'},
    {'kind': 'output_path', 'path': '../escape.csv'},
    {'kind': 'output_path', 'path': '/absolute.csv'},
    {'kind': 'output_path', 'path': 'C:\\escape.csv'},
    {'kind': 'struct', 'fields': {'evil;code': L(1)}},
    {'kind': 'function', 'entrypoint': 'eval'},
])
def test_bad_value_descriptors(descriptor):
    p = plan()
    p['steps'][0]['arguments'] = [descriptor]
    with pytest.raises((ValueError, TypeError)):
        native.validate_plan(p)


def test_matrix_cell_struct_complex_and_result_chaining():
    p = plan(inputs={'proxy': 'proxy.csv'})
    p['steps'][0]['arguments'] = [
        {'kind': 'input', 'name': 'proxy', 'columns': [1]},
        {'kind': 'array', 'data': [1, 2, 0, 10], 'shape': [2, 2]}]
    p['steps'].append({'id': 'filter', 'entrypoint': 'code/seriesanalysis/rhoAR1.m',
                       'arguments': [{'kind': 'ref', 'step': 'convert', 'output': 1}], 'nargout': 1})
    native.validate_plan(p)
    entries = {e['id']: e for e in native.catalog()['entries']}
    native.validate_value({'kind': 'struct', 'fields': {'options': {'kind': 'cell', 'items': [
        {'kind': 'complex', 'real': L(1), 'imag': L(2)},
        {'kind': 'array', 'data': ['NaN', 'Inf', '-Inf'], 'shape': [3, 1]}]}}}, entries, {}, {})


def test_script_workspace_is_explicit_and_names_are_checked():
    p = {'steps': [{'id': 'script', 'action': 'script', 'entrypoint': 'code/misc/GETac_pwd.m',
                    'workspace': {}, 'outputs': ['ac_pwd']}]}
    native.validate_plan(p)
    p['steps'][0]['outputs'] = ["x); system('bad')"]
    with pytest.raises(ValueError):
        native.validate_plan(p)


def test_gui_original_callbacks_and_declared_dialogs():
    p = {'steps': [
        {'id': 'launch', 'entrypoint': 'code/guicode/AC.m', 'nargout': 1},
        {'id': 'inspect', 'action': 'ui_inspect', 'target': {'kind': 'ref', 'step': 'launch'}},
        {'id': 'invoke', 'action': 'ui_invoke', 'target': {
            'kind': 'ui', 'owner': {'kind': 'ref', 'step': 'launch'}, 'tag': 'menu_detrend'}}],
        'dialogs': [{'name': 'inputdlg', 'outputs': [{'kind': 'cell', 'items': [L('0.35')]}]}]}
    native.validate_plan(p)


@pytest.fixture
def transport(tmp_path, monkeypatch):
    upstream = tmp_path / 'upstream'; upstream.mkdir()
    source = upstream / 'identity.m'; source.write_text('function y=identity(x)\ny=x;\nend\n')
    data = {'revision': 'pinned', 'entries': [{'id': 'identity.m', 'name': 'identity', 'kind': 'function',
             'visibility': 'public', 'inputs': ['x'], 'outputs': ['y'],
             'sha256': hashlib.sha256(source.read_bytes()).hexdigest()}]}
    monkeypatch.setattr(native, 'catalog', lambda: data)
    monkeypatch.setenv('ACYCLE_ROOT', str(upstream))
    monkeypatch.setenv('ACYCLE_BACKEND', 'local')
    workspace = tmp_path / 'workspace'; workspace.mkdir()
    (workspace / 'original.csv').write_text('1,2\n3,4\n')
    calls = []
    def execute(request):
        calls.append(request)
        output = Path(request['output_dir']) / 'analysis.mat'
        output.write_bytes(b'transport stub, not a MATLAB result')
        return {'status': 'completed', 'artifacts': {'analysis_mat': str(output)}, 'summary': {}}
    monkeypatch.setattr(tools, '_execute', execute)
    args = {'inputs': {'data': 'original.csv'}, 'steps': [
        {'id': 'test', 'entrypoint': 'identity.m', 'arguments': [{'kind': 'input', 'name': 'data'}]}]}
    return workspace, upstream, args, calls


def test_native_run_freezes_all_inputs_and_indexes_artifacts(transport):
    workspace, _, args, calls = transport
    result = tools.dispatch('acycle_native', args, workspace)
    assert result['status'] == 'completed'
    assert calls[0]['operation'] == 'native'
    frozen = Path(result['inputs']['data']['path'])
    (workspace / 'original.csv').write_text('changed')
    assert frozen.read_text() == '1,2\n3,4\n'
    assert result['artifact_sha256']['analysis_mat']
    assert tools.dispatch('acycle_get_run', {'run_id': result['run_id']}, workspace) == result


def test_source_drift_rejected_before_execution(transport):
    workspace, upstream, args, calls = transport
    (upstream / 'identity.m').write_text('changed')
    with pytest.raises(ValueError, match='source mismatch'):
        tools.dispatch('acycle_native', args, workspace)
    assert not calls
    assert not (workspace / '.acycle').exists()


def test_remote_native_is_explicitly_unavailable(transport, monkeypatch):
    workspace, _, args, calls = transport
    monkeypatch.setenv('ACYCLE_BACKEND', 'github')
    with pytest.raises(ValueError, match='local MATLAB'):
        tools.dispatch('acycle_native', args, workspace)
    assert not calls


def test_input_escape_rejected_before_creating_run(transport, tmp_path):
    workspace, _, args, calls = transport
    outside = tmp_path / 'outside.csv'; outside.write_text('outside')
    (workspace / 'link.csv').symlink_to(outside)
    args['inputs']['data'] = 'link.csv'
    with pytest.raises(ValueError, match='inside workspace'):
        tools.dispatch('acycle_native', args, workspace)
    assert not calls


def test_failure_retains_immutable_diagnostics(transport, monkeypatch):
    workspace, _, args, _ = transport
    def fail(request):
        (Path(request['output_dir']) / 'native-progress.json').write_text('{"completed_steps": []}')
        raise RuntimeError('deliberate transport failure')
    monkeypatch.setattr(tools, '_execute', fail)
    with pytest.raises(tools.RunError) as caught:
        tools.dispatch('acycle_native', args, workspace)
    record = tools.dispatch('acycle_get_run', {'run_id': caught.value.record['run_id']}, workspace)
    assert record['status'] == 'failed'
    assert 'native-progress.json' in record['diagnostics']
    assert Path(record['inputs']['data']['path']).is_file()
