"""Resolve the reviewed operation boundaries against both pinned inventories."""
import re
from collections import Counter, defaultdict

KINDS = {
    'science': '科学计算', 'view': '视图', 'data': '数据',
    'core': 'Core', 'gui': 'GUI', 'io': '成果 IO', 'workflow': '工作流',
    'test': '方法自测', 'case': '验证案例', 'study': '研究配方', 'check': '成果核查',
}


def resolve_selectors(module, rows, field, available):
    explicit = defaultdict(list)
    fallback = None
    for row in rows:
        selector = row[field]
        if selector == '*':
            assert fallback is None, (module, field, 'duplicate wildcard')
            fallback = row['operation']
        elif selector != '-':
            for value in selector.split():
                assert value in available, (module, field, value)
                assert row['operation'] not in explicit[value], (module, field, value)
                explicit[value].append(row['operation'])
    resolved = {}
    for value in available:
        operations = explicit[value] or ([fallback] if fallback else [])
        assert operations, (module, field, 'uncovered', value)
        if field == 'packages':
            assert len(operations) == 1, (module, value, operations)
        resolved[value] = operations
    return resolved


def consolidation(families, plan, packages, menus, roles):
    by_module = defaultdict(list)
    operations = set()
    for row in plan:
        module = row['module']
        op = row['operation']
        assert re.fullmatch(r'[A-Z][A-Za-z0-9]*', op) and op.casefold() not in operations, op
        operations.add(op.casefold())
        assert row['kind'] in KINDS and row['maintenance'] and row['decision_zh'], op
        role_names = row['proposed_roles'].split()
        if role_names != ['-']:
            assert role_names == [n for n in ('helper','analyzer','plotter') if n in role_names], op
            assert row['kind'] in ('science','data','view'), op
        by_module[module].append(row)
    assert set(by_module) == set(families), (set(by_module) ^ set(families))
    by_package = {}
    by_menu = defaultdict(list)
    for module, rows in by_module.items():
        names = {r[0] for r in packages if r[1] == module}
        by_package.update(resolve_selectors(module, rows, 'packages', names))
        tags = set(families[module]['menu_tags'].split())
        for tag, actions in resolve_selectors(module, rows, 'menus', tags).items():
            by_menu[tag].extend(actions)

    # All old package/version/role triples still resolve via the original implementation.
    # The new operation column describes maintenance, never permission to redirect replay.
    op_ids = {row[2] for row in roles}
    reconciled = set()
    index = []
    for package, module, _, guide_route, guide_roles, master_route, master_roles in packages:
        for version, offered in [('v1.0',guide_roles),('v3.1.1+dcba427',master_roles)]:
            reconciled.update(f'{package}-{version}/{role}' for role in offered.split())
        index.append(['package',package,module,' '.join(by_package[package]),
                      guide_route,guide_roles,master_route,master_roles])
    assert reconciled == op_ids and len(op_ids) == len(roles), 'incomplete role crosswalk'
    for tag, coverage, guide_state, _, master_state, _, owners, _ in menus:
        index.append(['menu',tag,owners,' '.join(by_menu[tag]),coverage,guide_state,'menu',master_state])
    assert set(by_menu) == {r[0] for r in menus}
    return index


def render_plan(families, plan, counts):
    maintenance = {row['maintenance'] for row in plan}
    lines = [
        '# Acycle 逐项归并方案',
        '',
        f"按原始菜单与源码归属顺序列出 {len(families)} 项。下表的 {len(plan)} 行是可独立维护的操作、视图、桌面功能或工程任务。第一列会因拆分而重复。第二列给出 {len(maintenance)} 个维护组及各组的建议操作名，同组可以有多个公开入口。角色列描述拟议接口；已发布的版本化入口按原名留存。",
        '',
        f"完整对账覆盖 {counts['menu']} 个菜单 tag 和 {counts['package']} 个旧包名。每个包可按 GUIDE 和 3.1.1 两栏查询其实际角色，合计 {counts['role']} 条版本化记录。菜单映射表示窗口所能配置的功能，专家包映射表示维护去向；两者都不改写旧日志的调用目标。Mini-Robot 的按钮调用单独从源码核实。",
        '',
        '[按菜单或包名查去向](modules/consolidation_index.tsv) · [每条旧操作、角色及源码行号](modules/roles.tsv) · [接口评审、重点分组与验收](METHOD_ROLE_REVIEW.zh-CN.md) · [逐行编辑的方案](modules/consolidation.tsv)',
        '',
        'H、A、P 分别表示 `helper`、`analyzer`、`plotter`。横线表示由 GUI、Core、IO 或工作流自身提供入口，或由资源目录按内容分派。已有图件可以复用另一操作的 plotter。标出的新角色要逐操作验收后才能使用。',
    ]
    area = None
    for row in plan:
        module = row['module']
        family = families[module]
        if family['area'] != area:
            area = family['area']
            lines += ['', f'## {area}', '', '| 原源码归属 | 新维护组与操作 | 类别 | 角色 | 归并依据及应保留的行为 |',
                      '| --- | --- | --- | --- | --- |']
        roles = row['proposed_roles'].split()
        short = ' · '.join({'helper':'H', 'analyzer':'A', 'plotter':'P', '-':'—'}[r] for r in roles)
        lines.append(f"| `{module}` | {row['maintenance']} · `{row['operation']}` | {KINDS[row['kind']]} | {short} | {row['decision_zh']} |")
    lines += ['', '## 数量与维护', '',
              '、'.join(f'{KINDS[kind]} {count}' for kind,count in Counter(r['kind'] for r in plan).items())+'。',
              '', '编辑用 TSV 中的 `*` 接收同一旧归属内尚未显式列出的包或菜单，`-` 表示没有该类入口。多个操作可以来自同一菜单。每个旧包只有一个主维护去向；跨组原函数调用另见调用清单。新操作名为提案，登记版本、函数签名及物理目录可分步落实。[调用清单](modules/shared_call_sites.tsv) · [重建脚本](tools/build_module_inventory.py)']
    return '\n'.join(lines)+'\n'
