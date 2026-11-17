"""Regression checks for dependency omissions found during the core trace."""
import sys
import unittest
from pathlib import Path

sys.path.insert(0,str(Path(__file__).resolve().parents[1]/'tools'))
from track_analysis_cores import parse_trace
from audit_acycle import entry, resolve


class CoreTraceTests(unittest.TestCase):
    def targets(self, source):
        c,_ = parse_trace('caller.m',source.encode())
        exports = {name:[entry(name+'.m')] for name in ('fft','helper','data')}
        return [(r['name'],t) for r in c.refs for t in resolve(r,c,exports)]

    def test_call_left_of_elementwise_product_is_not_assignment(self):
        targets = self.targets('function y=caller(x)\ny=fft(x).*2;\nend\n')
        self.assertIn(('fft',entry('fft.m')),targets)

    def test_assignment_index_does_not_call_same_named_function(self):
        targets = self.targets('function data=caller(x)\ndata(helper(x))=2;\nend\n')
        self.assertIn(('helper',entry('helper.m')),targets)
        self.assertNotIn(('data',entry('data.m')),targets)

    def test_bare_function_in_binary_expression_and_local_shadowing(self):
        targets = self.targets('function y=caller\ny=helper+2;\nend\nfunction y=helper\ny=1;\nend\n')
        self.assertTrue(any(name=='helper' and target.startswith('caller.m::helper@')
                            for name,target in targets))
        self.assertNotIn(('helper',entry('helper.m')),targets)


if __name__ == '__main__':
    unittest.main()
