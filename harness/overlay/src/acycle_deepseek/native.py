"""Full-source discovery and a typed, immutable MATLAB job transport.

This is a native API, not a new scientific implementation or a MATLAB sandbox.
GUI operations remain GUI operations, even when driven programmatically.
"""
from __future__ import annotations

from collections import Counter
from datetime import datetime, timezone
import hashlib
import json
import math
import os
from pathlib import Path
import re
import shutil
import uuid

IDENT = re.compile(r'[A-Za-z][A-Za-z0-9_]{0,62}\Z')
DTYPES = {'double', 'single', 'logical', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'int64', 'uint64'}
CALLBACKS = {'Callback', 'ButtonPushedFcn', 'ValueChangedFcn', 'ValueChangingFcn',
             'SelectionChangedFcn', 'CellEditCallback', 'CellSelectionCallback',
             'MenuSelectedFcn', 'ClickedCallback', 'CloseRequestFcn', 'ButtonDownFcn'}


def catalog():
    from .tools import _matlab_dir
    return json.loads((_matlab_dir() / 'native_catalog.json').read_text(encoding='utf-8'))


def discover(args):
    data = catalog()
    if 'query' in args and not isinstance(args['query'], str):
        raise ValueError('query must be a string')
    if 'entrypoint' in args:
        entry = next((e for e in data['entries'] if e['id'] == args['entrypoint']), None)
        if entry is None:
            raise ValueError('Unknown exact catalog entrypoint; use acycle_catalog to discover its path')
        return {'revision': data['revision'], 'entry': entry,
                'runtime_validated': False, 'native_contract': 'docs/NATIVE_API.md'}
    query = args.get('query', '').casefold()
    if args.get('view', 'entries') == 'menus':
        entries = [e for e in data['menus'] if query in json.dumps(e, ensure_ascii=False).casefold()]
    else:
        entries = [e for e in data['entries'] if
                   query in (e['id'] + '\n' + e['help']).casefold()
                   and (not args.get('role') or e['role'] == args['role'])
                   and (not args.get('interface') or e['interface'] == args['interface'])]
        fields = ('id', 'name', 'kind', 'role', 'interface', 'signature', 'effects')
        entries = [{k: e[k] for k in fields} for e in entries]
    offset, limit = args.get('offset', 0), args.get('limit', 25)
    if type(offset) is not int or offset < 0 or type(limit) is not int or not 1 <= limit <= 100:
        raise ValueError('offset must be nonnegative; limit must be 1..100')
    return {'revision': data['revision'], 'summary': data['summary'], 'runtime_validated': False,
            'total_matches': len(entries), 'offset': offset, 'entries': entries[offset:offset+limit],
            'next_offset': offset+limit if offset+limit < len(entries) else None,
            'note': 'Coverage is source/API coverage, not proof of headless GUI parity or scientific validation.'}


def _keys(obj, required=(), optional=()):
    if not isinstance(obj, dict) or set(obj) - set(required) - set(optional) or set(required) - set(obj):
        raise ValueError(f'Expected keys {tuple(required)} and optional keys {tuple(optional)}')


def _identifier(name):
    if not isinstance(name, str) or not IDENT.fullmatch(name) or name.startswith('hn_'):
        raise ValueError(f'Invalid or reserved MATLAB identifier: {name!r}')


def _finite_json(value):
    # MATLAB JSON cannot represent NaN/Inf without an explicit array descriptor.
    json.dumps(value, allow_nan=False)


def validate_value(value, entries, available, inputs, depth=0):
    if depth > 30:
        raise ValueError('Value nesting exceeds 30 levels')
    if not isinstance(value, dict) or 'kind' not in value:
        raise ValueError('Every native argument must be a typed value descriptor')
    kind = value['kind']
    if kind == 'literal':
        _keys(value, ('kind', 'value'))
        _finite_json(value['value'])
    elif kind == 'array':
        _keys(value, ('kind', 'data', 'shape'), ('dtype',))
        shape = value['shape']
        if not isinstance(shape, list) or not 2 <= len(shape) <= 8 or any(type(n) is not int or n < 0 for n in shape):
            raise ValueError('array.shape requires 2..8 nonnegative integer dimensions')
        if not isinstance(value['data'], list) or math.prod(shape) != len(value['data']) or len(value['data']) > 1000000:
            raise ValueError('Array data length must match shape and be <= 1000000; use an input file for larger data')
        if value.get('dtype', 'double') not in DTYPES:
            raise ValueError('Unsupported MATLAB array dtype')
        for item in value['data']:
            if isinstance(item, str):
                if item not in {'NaN', 'Inf', '-Inf'} or value.get('dtype', 'double') not in {'double', 'single'}:
                    raise ValueError('Nonfinite array tokens require a floating-point dtype')
            elif not isinstance(item, (int, float, bool)) or not math.isfinite(item):
                raise ValueError('Array values must be finite scalars or explicit NaN/Inf tokens')
    elif kind == 'complex':
        _keys(value, ('kind', 'real', 'imag'))
        validate_value(value['real'], entries, available, inputs, depth+1)
        validate_value(value['imag'], entries, available, inputs, depth+1)
    elif kind in {'cell', 'struct'}:
        key = 'items' if kind == 'cell' else 'fields'
        _keys(value, ('kind', key))
        collection = value[key]
        if kind == 'cell' and not isinstance(collection, list) or kind == 'struct' and not isinstance(collection, dict):
            raise ValueError(f'Invalid {kind} payload')
        if kind == 'struct':
            for name in collection:
                _identifier(name)
        for item in collection.values() if kind == 'struct' else collection:
            validate_value(item, entries, available, inputs, depth+1)
    elif kind == 'input':
        _keys(value, ('kind', 'name'), ('format', 'variable', 'columns'))
        if value['name'] not in inputs:
            raise ValueError('Unknown declared input name')
        if value.get('format', 'matrix') not in {'matrix', 'table', 'mat', 'path', 'image'}:
            raise ValueError('Unknown input format')
        if value.get('format') == 'mat':
            _identifier(value.get('variable'))
        if 'columns' in value:
            _indices(value['columns'])
    elif kind in {'ref', 'figure'}:
        _keys(value, ('kind', 'step'), ('output', 'fields', 'columns') if kind == 'ref' else ('index', 'fields', 'columns'))
        if value['step'] not in available:
            raise ValueError('References must select a completed earlier step')
        if kind == 'ref':
            n = value.get('output', 1)
            if type(n) is not int or not 1 <= n <= available[value['step']]:
                raise ValueError('Output reference is outside the earlier step output count')
        if 'fields' in value:
            if not isinstance(value['fields'], list):
                raise ValueError('fields must be a list')
            for field in value['fields']:
                _identifier(field)
        if 'columns' in value:
            _indices(value['columns'])
        if 'index' in value and (type(value['index']) is not int or value['index'] < 1):
            raise ValueError('index must be a positive integer')
    elif kind == 'output_path':
        _keys(value, ('kind', 'path'))
        p = Path(value['path'])
        if p.is_absolute() or not p.parts or '..' in p.parts or '\\' in value['path'] or ':' in value['path']:
            raise ValueError('Output path must stay inside this new run')
    elif kind == 'function':
        _keys(value, ('kind', 'entrypoint'))
        e = entries.get(value['entrypoint'])
        if not e or e['kind'] != 'function' or e['visibility'] != 'public':
            raise ValueError('Function handles require a public catalog function')
    elif kind == 'ui':
        _keys(value, ('kind', 'owner'), ('component', 'tag', 'type', 'text', 'index'))
        validate_value(value['owner'], entries, available, inputs, depth+1)
        if 'component' in value:
            _identifier(value['component'])
        if 'index' in value and (type(value['index']) is not int or value['index'] < 1):
            raise ValueError('UI index must be a positive integer')
    else:
        raise ValueError(f'Unknown typed value: {kind}')


def _indices(indices):
    if not isinstance(indices, list) or not indices or any(type(n) is not int or n < 1 for n in indices):
        raise ValueError('Indices must be positive MATLAB 1-based integers')


def validate_plan(args):
    if 'seed' in args and (type(args['seed']) is not int or not 0 <= args['seed'] <= 4294967295):
        raise ValueError('seed must be an integer in [0, 2^32-1]')
    data = catalog()
    entries = {e['id']: e for e in data['entries']}
    inputs = args.get('inputs', {})
    if not isinstance(inputs, dict):
        raise ValueError('inputs must be a mapping of names to workspace file paths')
    for name, path in inputs.items():
        _identifier(name)
        if not isinstance(path, str):
            raise ValueError('Input paths must be strings')
    steps = args['steps']
    if not isinstance(steps, list) or not 1 <= len(steps) <= 100:
        raise ValueError('Provide 1..100 native steps')
    available = {}
    for step in steps:
        if not isinstance(step, dict):
            raise ValueError('Each step must be an object')
        action = step.get('action', 'call')
        _keys(step, ('id',), ('action', 'entrypoint', 'arguments', 'nargout', 'workspace', 'outputs',
                              'target', 'properties', 'callback', 'event'))
        _identifier(step['id'])
        if step['id'] in available:
            raise ValueError('Step IDs must be unique')
        nout = 0
        if action in {'call', 'script'}:
            entry = entries.get(step.get('entrypoint'))
            if not entry or entry['visibility'] != 'public':
                raise ValueError('Use a public exact catalog entrypoint; private helpers are reached through their owner')
            if (entry['kind'] == 'script') != (action == 'script'):
                raise ValueError('Scripts require action=script; functions/classes require action=call')
            if action == 'call':
                if any(k in step for k in ('workspace', 'outputs', 'target', 'properties', 'callback', 'event')):
                    raise ValueError('Unexpected fields for call step')
                nout = step.get('nargout', 0 if entry['kind'] == 'function' and not entry['outputs'] else 1)
                if type(nout) is not int or not 0 <= nout <= 64:
                    raise ValueError('nargout must be an integer from 0 through 64')
                if entry['kind'] == 'class' and nout > 1:
                    raise ValueError('Class constructors return at most one object')
                if entry['kind'] == 'function' and 'varargout' not in entry['outputs'] and nout > len(entry['outputs']):
                    raise ValueError('nargout exceeds the function declaration')
                argv = step.get('arguments', [])
                if not isinstance(argv, list):
                    raise ValueError('arguments must be an array of typed descriptors')
                if entry['kind'] == 'function' and 'varargin' not in entry['inputs'] and len(argv) > len(entry['inputs']):
                    raise ValueError('Too many positional arguments for this declaration')
                for value in argv:
                    validate_value(value, entries, available, inputs)
            else:
                if any(k in step for k in ('arguments', 'nargout', 'target', 'properties', 'callback', 'event')):
                    raise ValueError('Unexpected fields for script step')
                workspace = step.get('workspace', {})
                outputs = step.get('outputs', [])
                if not isinstance(workspace, dict) or not isinstance(outputs, list):
                    raise ValueError('Scripts require a workspace mapping and an output name list')
                for name, value in workspace.items():
                    _identifier(name)
                    validate_value(value, entries, available, inputs)
                for name in outputs:
                    _identifier(name)
                nout = len(outputs)
        elif action in {'ui_set', 'ui_get', 'ui_invoke', 'ui_inspect'}:
            if any(k in step for k in ('entrypoint', 'arguments', 'nargout', 'workspace', 'outputs')):
                raise ValueError('Unexpected fields for UI step')
            validate_value(step.get('target'), entries, available, inputs)
            if action == 'ui_set':
                if not isinstance(step.get('properties'), dict):
                    raise ValueError('ui_set requires a property mapping')
                for name, value in step['properties'].items():
                    _identifier(name)
                    if name.endswith('Fcn') or name.endswith('Callback') or name in {'Callback', 'DeleteFcn', 'CreateFcn'}:
                        raise ValueError('UI callback replacement is not supported; invoke the original callback')
                    validate_value(value, entries, available, inputs)
            if action == 'ui_get':
                if not isinstance(step.get('properties'), list):
                    raise ValueError('ui_get requires a property list')
                for name in step['properties']:
                    _identifier(name)
                nout = 1
            if action == 'ui_inspect':
                nout = 1
            if action == 'ui_invoke':
                if step.get('callback', 'Callback') not in CALLBACKS:
                    raise ValueError('Unknown callback property')
                if 'event' in step:
                    validate_value(step['event'], entries, available, inputs)
        else:
            raise ValueError('Unknown native step action')
        available[step['id']] = nout
    dialogs = args.get('dialogs', [])
    if not isinstance(dialogs, list):
        raise ValueError('dialogs must be an ordered list')
    allowed_dialogs = {'inputdlg', 'questdlg', 'uigetfile', 'uiputfile', 'uigetdir', 'listdlg', 'menu',
                       'ginput', 'myginput', 'input', 'waitforbuttonpress'}
    for dialog in dialogs:
        _keys(dialog, ('name', 'outputs'))
        if dialog['name'] not in allowed_dialogs or not isinstance(dialog['outputs'], list):
            raise ValueError('Unsupported scripted dialog')
        for value in dialog['outputs']:
            validate_value(value, entries, {}, inputs)
    return data


def run(root, args):
    from . import tools
    data = validate_plan(args)
    if os.environ.get('ACYCLE_BACKEND', 'local') != 'local':
        raise ValueError('Native multi-input/UI jobs currently require local MATLAB; existing high-level tools retain GitHub transport')
    acycle_root = os.environ.get('ACYCLE_ROOT', '')
    if not acycle_root:
        raise ValueError('Set ACYCLE_ROOT to the pinned Acycle checkout')
    # Check the whole source set, not just a function whose dependencies may have changed.
    upstream = Path(acycle_root).resolve()
    for entry in [*data['entries'], *data.get('resources', [])]:
        source = (upstream / entry['id']).resolve()
        if not source.is_relative_to(upstream) or not source.is_file() or hashlib.sha256(source.read_bytes()).hexdigest() != entry['sha256']:
            raise ValueError(f'Upstream source mismatch: {entry["id"]}; review and regenerate the catalog')
    resolved_inputs = {}
    for name, source in args.get('inputs', {}).items():
        path = Path(source).expanduser()
        path = (root / path).resolve() if not path.is_absolute() else path.resolve()
        if not any(path.is_relative_to(base) for base in (root, upstream)) or not path.is_file():
            raise ValueError('Native input files must be inside workspace or ACYCLE_ROOT')
        resolved_inputs[name] = path
    run_id = datetime.now(timezone.utc).strftime('%Y%m%dT%H%M%SZ-') + uuid.uuid4().hex[:12]
    directory = tools._run_path(root, run_id)
    output = directory / 'outputs'
    output.mkdir(parents=True)
    frozen = directory / 'inputs'
    frozen.mkdir()
    inputs = {}
    for name, source in resolved_inputs.items():
        target = frozen / (name + source.suffix.lower())
        shutil.copyfile(source, target)
        inputs[name] = {'path': str(target), 'original_path': str(source),
                        'sha256': hashlib.sha256(target.read_bytes()).hexdigest()}
    record = {'run_id': run_id, 'operation': 'native', 'status': 'running', 'backend': 'local',
              'label': args.get('label', ''), 'created_at': datetime.now(timezone.utc).isoformat(),
              'output_dir': str(output), 'inputs': inputs, 'parameters': args,
              'source_revision': data['revision'], 'parent_run_id': None}
    tools._write(directory / 'request.json', record)
    try:
        response = tools._execute({'operation': 'native', 'output_dir': str(output),
                                   'acycle_root': str(upstream), 'inputs': inputs,
                                   'parameters': {k: v for k, v in args.items() if k not in {'inputs', 'label'}}})
        record.update(status='completed', result=response, summary=response.get('summary', {}),
                      artifacts=response.get('artifacts', {}), provenance=response.get('provenance', {}))
        record['artifact_sha256'] = {
            key: hashlib.sha256(Path(p).read_bytes()).hexdigest() for key, p in record['artifacts'].items()
            if isinstance(p, str) and Path(p).is_file() and Path(p).resolve().is_relative_to(output)}
    except BaseException as exc:
        record.update(status='cancelled' if isinstance(exc, (KeyboardInterrupt, SystemExit)) else 'failed',
                      error=f'{type(exc).__name__}: {exc}')
        record['diagnostics'] = {p.name: str(p) for p in output.iterdir() if p.is_file() and p.suffix in {'.log', '.json'}}
        tools._write(directory / 'result.json', record)
        if isinstance(exc, (KeyboardInterrupt, SystemExit)):
            raise
        raise tools.RunError(record) from exc
    tools._write(directory / 'result.json', record)
    return record


def schemas():
    def spec(name, description, properties, required=()):
        return {'type': 'function', 'function': {'name': name, 'description': description,
                'parameters': {'type': 'object', 'additionalProperties': False,
                               'properties': properties, 'required': list(required)}}}
    return [spec('acycle_catalog', 'Discover ALL pinned Acycle MATLAB files, signatures, source help, dependencies and GUI menu bindings. Source coverage is not MATLAB runtime validation. Get entrypoint details before native calls.', {
        'query': {'type': 'string'}, 'entrypoint': {'type': 'string'},
        'view': {'type': 'string', 'enum': ['entries', 'menus']},
        'role': {'type': 'string', 'enum': ['calculation', 'helper', 'plotter', 'gui', 'mixed']},
        'interface': {'type': 'string', 'enum': ['call', 'gui', 'script', 'owner_only']},
        'offset': {'type': 'integer', 'minimum': 0}, 'limit': {'type': 'integer', 'minimum': 1, 'maximum': 100}}),
        spec('acycle_native', 'Execute a typed workflow against exact catalog entrypoints in local MATLAB. Supports public functions/classes, scripts with explicit workspace, original UI callbacks, frozen multi-file input, result chaining, MAT/CSV/figures and source hashes. Each argument is a descriptor: literal(value), array(data,shape,dtype), complex(real,imag), input(name,format), ref(step,output,fields), cell(items), struct(fields), output_path(path), function(entrypoint), figure(step,index), or ui(owner,component/tag/type/text/index). GUI calls require sufficient context; unexpected blocking dialogs fail, never invent defaults. Not a sandbox. See docs/NATIVE_API.md.', {
            'inputs': {'type': 'object', 'additionalProperties': {'type': 'string'}},
            'steps': {'type': 'array', 'minItems': 1, 'maxItems': 100, 'items': {
                'type': 'object', 'required': ['id'], 'additionalProperties': False,
                'properties': {'id': {'type': 'string'}, 'action': {'type': 'string', 'enum': ['call', 'script', 'ui_set', 'ui_get', 'ui_invoke', 'ui_inspect']},
                    'entrypoint': {'type': 'string'}, 'arguments': {'type': 'array', 'items': {'type': 'object'}},
                    'nargout': {'type': 'integer', 'minimum': 0, 'maximum': 64},
                    'workspace': {'type': 'object'}, 'outputs': {'type': 'array', 'items': {'type': 'string'}},
                    'target': {'type': 'object'}, 'properties': {'anyOf': [{'type': 'object'}, {'type': 'array', 'items': {'type': 'string'}}]},
                    'callback': {'type': 'string'}, 'event': {'type': 'object'}}}},
            'dialogs': {'type': 'array', 'items': {'type': 'object', 'required': ['name', 'outputs'],
                'properties': {'name': {'type': 'string'}, 'outputs': {'type': 'array', 'items': {'type': 'object'}}}, 'additionalProperties': False}},
            'seed': {'type': 'integer', 'minimum': 0, 'maximum': 4294967295},
            'label': {'type': 'string'}}, ('steps',))]
