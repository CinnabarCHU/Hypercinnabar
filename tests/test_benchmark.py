import json
import sys
import tempfile
import unittest
from pathlib import Path
from types import SimpleNamespace
from unittest.mock import patch

import numpy as np
from scipy.io import loadmat

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))
from bench import csv_table, execute, prepare_case, prepare_task
from fixtures import case_tables, lr04_data
from records import ROOT, catalog, digest, record_bytes
from scoring import clock_ensemble, read_json, score_case, score_task


class BenchmarkTests(unittest.TestCase):
    def setUp(self):
        temp = tempfile.TemporaryDirectory()
        self.addCleanup(temp.cleanup)
        self.dir = Path(temp.name)
        self.cases = catalog("cases")
        self.tasks = catalog("tasks")

    def test_interrupted_prepare_can_be_retried(self):
        target = self.dir / "request"
        target.mkdir()
        args = SimpleNamespace(command="prepare", id="tune-knots", directory=target)

        def interrupted(case, folder):
            (folder / "data.csv").write_text("partial")
            raise OSError("interrupted")

        with patch("bench.prepare_case", side_effect=interrupted), self.assertRaises(OSError):
            execute(args)
        self.assertEqual(list(target.iterdir()), [])
        self.assertEqual(execute(args), 0)
        self.assertEqual(json.loads((target / "request.json").read_text())["id"], "tune-knots")
        with self.assertRaises(ValueError):
            execute(args)

    def test_every_reference_rejects_a_changed_value(self):
        for name, case in self.cases.items():
            with self.subTest(name=name):
                _, ref = case_tables(case)
                self.assertTrue(np.isfinite(ref).all())
                csv_table(self.dir,"result",case["output_columns"],ref)
                self.assertEqual(score_case(case,self.dir)["status"],"match")
                changed=ref.copy()
                changed[-1,-1] += 1+abs(changed[-1,-1])
                csv_table(self.dir,"result",case["output_columns"],changed)
                self.assertEqual(score_case(case,self.dir)["status"],"mismatch")

    def test_parameters_and_fields_follow_revision(self):
        old=self.cases["cenogrid-carbon-v28-swa"]
        current=self.cases["cenogrid-carbon-current-swa"]
        data,ref=case_tables(old)
        np.testing.assert_array_equal(data,case_tables(current)[0])
        csv_table(self.dir,"result",old["output_columns"],ref)
        scores=score_case(current,self.dir)["columns"]
        self.assertEqual(scores["power"]["failures"],0)
        self.assertGreater(scores["fdr05"]["failures"],0)

    def test_shifted_nonnumeric_and_truncated_arrays(self):
        case=self.cases["constant-sedrate"]
        _,ref=case_tables(case)
        flipped=ref.copy(); flipped[:,0]+=1
        csv_table(self.dir,"result",case["output_columns"],flipped)
        self.assertEqual(score_case(case,self.dir)["status"],"mismatch")
        for invalid in [ref[:-1],np.full(ref.shape,np.nan)]:
            csv_table(self.dir,"result",case["output_columns"],invalid)
            with self.assertRaises(ValueError):score_case(case,self.dir)
        csv_table(self.dir,"result",["proxy","time_ka"],ref)
        with self.assertRaises(ValueError):score_case(case,self.dir)

    def test_scientific_disagreement_and_missing_fdr(self):
        hist=catalog("historical-results")
        for name in ("petm-broad","petm-published"):
            c=hist[name]["comparison"]
            (self.dir/"result.json").write_text(json.dumps({"rate_cm_per_ka":c["observed_best_rate_cm_kyr"],"global_p":c["observed_rate_global_p"]}))
            self.assertEqual(score_task(self.tasks[name],self.dir)["status"],"criterion_unmet")
        peak=hist["lavernock"]["comparison"]["observed_peaks"]
        pred={"wavelength_m":peak["period"],"peak_power":peak["power"],"fdr05_power":None}
        (self.dir/"result.json").write_text(json.dumps(pred))
        result=score_task(self.tasks["lavernock"],self.dir)
        self.assertEqual([m["met"] for m in result["metrics"]],[True,False])
        pred["fdr05_power"]=peak["power"]-.1
        (self.dir/"result.json").write_text(json.dumps(pred))
        self.assertEqual(score_task(self.tasks["lavernock"],self.dir)["status"],"criterion_met")

    def test_packet_contains_only_requested_inputs(self):
        entry=self.tasks["lr04-gaps"]
        packet=prepare_task("lr04-gaps",entry,self.dir)
        self.assertEqual(set(p.name for p in self.dir.iterdir()),{"data.csv","queries.csv"})
        self.assertNotIn("metrics",packet)
        seen,ref,_=lr04_data()
        self.assertFalse(np.intersect1d(seen[:,0],ref[:,0]).size)
        csv_table(self.dir,"prediction",["age_ka","benthic_d18O_permil"],ref[::-1])
        with self.assertRaises(ValueError):score_task(entry,self.dir)
        csv_table(self.dir,"prediction",["age_ka","benthic_d18O_permil"],ref)
        self.assertEqual(score_task(entry,self.dir)["metrics"]["all"]["rmse_permil"],0)

    def test_clock_support_monotonicity_and_ensemble(self):
        task=self.tasks["odp846-oracle-original"]
        ref=np.loadtxt(ROOT/task["reference_file"],delimiter=",",skiprows=1)
        headers=["segment","coordinate_m","time_ka"]
        csv_table(self.dir,"prediction",headers,ref)
        np.testing.assert_equal(score_task(task,self.dir)["metrics"]["rmse_ka"],0)
        for broken in (ref[::-1],np.c_[ref[:,:2],-ref[:,2]]):
            csv_table(self.dir,"prediction",headers,broken)
            with self.assertRaises(ValueError):score_task(task,self.dir)
        csv_table(self.dir,"prediction",headers,ref)
        samples=np.c_[ref[:,:2], ref[:,2]-1,ref[:,2]+1]
        csv_table(self.dir,"ensemble",["segment","coordinate_m","draw_1","draw_2"],samples)
        vals=clock_ensemble(self.dir/"ensemble.csv",ref)
        self.assertAlmostEqual(vals["mean_crps_ka"],.5)
        self.assertEqual(vals["reference_in_90pct_fraction"],1)
        samples[:,2] *= -1
        csv_table(self.dir,"ensemble",["segment","coordinate_m","draw_1","draw_2"],samples)
        with self.assertRaises(ValueError):score_task(task,self.dir)

    def test_binary_decisions_require_every_record(self):
        task=self.tasks["synthetic-detection"]
        pred=np.c_[np.arange(40),np.zeros(40)]
        csv_table(self.dir,"prediction",["record_id","detected"],pred)
        self.assertEqual(score_task(task,self.dir)["metrics"]["balanced_accuracy"],.5)
        pred[-1,0]=1
        csv_table(self.dir,"prediction",["record_id","detected"],pred)
        with self.assertRaises(ValueError):score_task(task,self.dir)

    def test_nonfinite_duplicate_and_wrong_type_json(self):
        f=self.dir/"result.json"
        for payload in ['{"rate_cm_per_ka":NaN}','{"rate_cm_per_ka":2,"rate_cm_per_ka":3}']:
            f.write_text(payload)
            with self.assertRaises(ValueError):read_json(f)
        for val in [True,"3.02",0,-2,None,1e309]:
            f.write_text(json.dumps({"rate_cm_per_ka":val}))
            with self.assertRaises(ValueError):score_task(self.tasks["odp926b-timeopt"],self.dir)

    def test_inventory_sources_and_expected_fields(self):
        self.assertFalse(set(self.cases)&set(self.tasks))
        records=catalog("records")
        for name,rec in records.items():
            if "file" in rec:
                data=record_bytes(name)
                self.assertEqual(rec["rows"],len(data.splitlines())-1)
        for name,entry in self.tasks.items():
            with self.subTest(name=name):
                self.assertTrue(set(entry["inputs"].values())<=set(records))
                for rel in entry.get("packet_files",[]): self.assertTrue((ROOT/rel).is_file())
                if "reference_file" in entry: self.assertTrue((ROOT/entry["reference_file"]).is_file())
        for suite in catalog("suites").values():
            self.assertRegex(suite["commit"],r"^[0-9a-f]{40}$")
        self.assertEqual(len(catalog("harness-cases")["cases"]),12)

if __name__=="__main__":
    unittest.main()
