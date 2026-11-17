"""Behaviour tests for false dead-code classifications, without MATLAB."""
import sys
import unittest
from unittest.mock import patch
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / 'tools'))
from audit_acycle import entry, parse_source, resolve, reachability, branch_inventory


class GraphTests(unittest.TestCase):
    def resolved(self, source, exports, path='caller.m'):
        c = parse_source(path, source)
        return c, [(r, resolve(r, c, exports)) for r in c.refs]

    def test_comments_do_not_create_dependencies(self):
        _, refs = self.resolved('function caller\n% phantom(1)\ny=1;\nend\n', {'phantom':['phantom.m::<file>']})
        self.assertFalse(any(target for _, target in refs))

    def test_local_function_shadows_other_file(self):
        c, refs = self.resolved('function caller\ny=helper(1);\nend\nfunction y=helper(x)\ny=x;\nend\n',
                               {'helper':[entry('helper.m')]})
        targets = [t for r, ts in refs if r['name']=='helper' for t in ts]
        self.assertTrue(targets)
        self.assertTrue(all(t.startswith('caller.m::helper@') for t in targets))

    def test_array_index_is_not_same_named_function(self):
        _, refs = self.resolved('function y=caller(helper)\ny=helper(1);\nend\n', {'helper':[entry('helper.m')]})
        self.assertFalse(any(t for r,t in refs if r['name']=='helper'))

    def test_no_argument_script_is_retained(self):
        _, refs = self.resolved('function caller\nGETac_pwd;\nend\n', {'GETac_pwd':[entry('GETac_pwd.m')]})
        self.assertIn(entry('GETac_pwd.m'), [t for r,ts in refs for t in ts])

    def test_private_function_is_owner_scoped(self):
        exports={'helper':[entry('lib/private/helper.m')]}
        for path,expected in [('lib/owner.m',True),('other/owner.m',False)]:
            _, refs = self.resolved('function owner\nhelper(1);\nend\n', exports,path)
            self.assertEqual(any(t for r,t in refs),expected)

    def test_handle_and_literal_callback_are_distinct_evidence(self):
        _, refs = self.resolved("function caller\nf=@callback;\nfeval('callback');\nend\nfunction callback\nend\n",{})
        kinds={r['kind'] for r,t in refs if t and r['name']=='callback'}
        self.assertIn('function_handle',kinds)
        self.assertIn('literal_dispatch',kinds)
        self.assertIn('symbol_literal_possible',kinds)

    def test_nested_scope_does_not_leak_into_sibling(self):
        _, refs=self.resolved('function caller\nfoo;\nend\nfunction sibling\nfunction foo\nend\nend\n',{})
        self.assertFalse(any(t for r,t in refs if r['name']=='foo'))

    def test_crlf_source_lines_are_preserved(self):
        c=parse_source('caller.m','function caller\r\nscriptname;\r\nend\r\n')
        self.assertEqual(next(r['line'] for r in c.refs if r['name']=='scriptname'),2)

    def test_transitive_closure_handles_cycles(self):
        edges=[{'source':'a','target':'b'},{'source':'b','target':'a'},{'source':'b','target':'c'}]
        self.assertEqual(reachability(['a'],edges),{'a','b','c'})

    def test_data_string_is_not_external_gui_call(self):
        _, refs=self.resolved("function caller\nunit='ft';\nend\n",{'ft':[entry('ft.m')]})
        self.assertFalse(any(t for r,t in refs))

    def test_switch_case_zero_is_not_a_false_condition(self):
        c=parse_source('caller.m','function caller(x)\nswitch x\ncase 0\ny=1;\nend\nif false\ny=2;\nend\nend\n')
        self.assertEqual([x['line'] for x in c.constant_conditions],[6])

    def test_symbolic_head_is_not_a_third_branch(self):
        def fake_git(root,*args):
            if args[0]=='for-each-ref':
                return '\n'.join('refs/remotes/origin/'+x for x in ['HEAD','dev-codex','master'])
            self.assertFalse(any(x.endswith('/HEAD') for x in args))
            if args[0]=='rev-list': return '0 0'
            if args[0]=='diff': return ''
            return 'value'
        with patch('audit_acycle.git',side_effect=fake_git):
            self.assertEqual([r['branch'] for r in branch_inventory(Path('.'))],['dev-codex','master'])


if __name__ == '__main__':
    unittest.main()
