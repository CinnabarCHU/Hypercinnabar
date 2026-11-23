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

    def test_rate_step_sampling_is_independent_of_rate(self):
        packet = prepare_task("synthetic-rate-step", self.tasks["synthetic-rate-step"], self.dir)
        section = np.loadtxt(self.dir / "data.csv", delimiter=",", skiprows=1)
        np.testing.assert_allclose(np.diff(section[:, 0]), .05, atol=2e-14, rtol=0)
        self.assertNotIn("4-to-6", json.dumps(packet))

    def test_cip_forward_and_inverse_share_the_geological_clock(self):
        _, generator = case_tables(self.cases["cip-case3-forward-clock"])
        times, heights, rates = generator.T
        np.testing.assert_allclose(np.diff(heights), np.diff(times)*rates[1:]/100, atol=1e-10, rtol=0)
        trap = np.r_[0., np.cumsum(np.diff(times)*(rates[:-1]+rates[1:])/200)]
        self.assertGreater(np.max(np.abs(trap-heights)), .01)
        _, inv = case_tables(self.cases["cip-case3-inverse-clock"])
        observed = np.loadtxt(ROOT/self.tasks["cip1-case3"]["reference_file"], delimiter=",", skiprows=1)
        np.testing.assert_array_equal(inv[:, 1], observed[:, 1])
        np.testing.assert_allclose(np.interp(inv[:, 1], heights, times), observed[:, 2], atol=1e-8, rtol=0)
        np.testing.assert_array_equal(inv[:, 0], observed[:, 2])

    def test_two_sides_of_hiatus_survive_and_discretizations_differ(self):
        for variant in ("original","reduced"):
            _, clock = case_tables(self.cases["odp846-segmented-clock-"+variant])
            changes = np.flatnonzero(np.diff(clock[:, 0]))
            self.assertEqual(len(changes), 2)
            np.testing.assert_allclose(clock[changes,1], clock[changes+1,1], atol=1e-12, rtol=0)
            self.assertTrue(np.all(clock[changes+1,2]-clock[changes,2] > 15))
        continuous = self.cases["imbrie-response-continuous"]
        cin, cref = case_tables(continuous)
        ein, eref = case_tables(self.cases["imbrie-response-euler"])
        np.testing.assert_array_equal(cin, ein)
        self.assertGreater(np.max(np.abs(cref[:,1]-eref[:,1])), .1)
        csv_table(self.dir,"result",continuous["output_columns"],eref)
        self.assertEqual(score_case(continuous,self.dir)["status"],"mismatch")

    def test_analytic_envelope_block_response_and_rate_proxy_truth(self):
        raw, ref = case_tables(self.cases["am-hilbert-envelope"])
        phase = 2*np.pi*raw[:,0]/256
        envelope = 1.4 + .35*np.cos(3*phase+.21)
        np.testing.assert_allclose(raw[:,1], envelope*np.cos(32*phase+.4), atol=1e-12, rtol=0)
        np.testing.assert_allclose(ref[:,1], envelope, atol=1e-12, rtol=0)
        for name, decay in (("continuous", np.exp(-.4/17)), ("euler", 1-.4/17)):
            forcing, ice = case_tables(self.cases["imbrie-response-"+name])
            drive = np.mean(forcing[:,1])-forcing[-1,1]
            n = np.arange(14)
            expected = drive+(3-drive)*decay**n
            np.testing.assert_allclose(ice[::-1][:14,1],expected,rtol=0,atol=1e-12)
        from fixtures import rate_section
        _, ref = case_tables(self.cases["two-rate-forward-proxy"])
        np.testing.assert_array_equal(ref[:,[0,3]],rate_section())

    def test_empirical_clock_reports_errors_on_unknown_levels(self):
        for name, count in (("rossello-precession",76),("odp846-published-clock",322)):
            task = self.tasks[name]
            clock = np.loadtxt(ROOT/task["reference_file"], delimiter=",", skiprows=1)
            self.assertEqual(len(clock),count)
            self.assertTrue(np.all(np.diff(clock[:,2]) >= 0))
            for path in task["packet_files"]:
                if Path(path).name == "queries.csv":
                    self.assertEqual((ROOT/path).read_text().splitlines()[0],"segment,coordinate_m")
                else:
                    data = np.loadtxt(ROOT/path, delimiter=",", skiprows=1)
                    np.testing.assert_array_equal(data,clock[[0,-1],1:])
            self.assertNotIn(task["reference_record"],task["inputs"].values())
            clock[1:-1,2] += .25
            csv_table(self.dir,"prediction",["segment","coordinate_m","time_ka"],clock)
            metrics = score_task(task,self.dir)["metrics"]
            self.assertEqual(metrics["interior_rows"],count-2)
            self.assertAlmostEqual(metrics["interior_rmse_ka"],.25)
            self.assertEqual(metrics["endpoint_errors_ka"],[0.,0.])

    def test_timeopt_publications_have_distinct_comparisons(self):
        sample = dict(rate_cm_per_ka=.353, precession_arcsec_yr=87.74, lod_h=None,
                      rate_ci95=[.343,.365],precession_ci95=None)
        (self.dir/"result.json").write_text(json.dumps(sample))
        scores = score_task(self.tasks["xiamaling-precession"],self.dir)["metrics"]
        peaks = [s for s in scores if s["field"]=="precession_arcsec_yr"]
        self.assertEqual([s["reference"] for s in peaks],[87.74,85.79])
        self.assertNotEqual(peaks[0]["comparison"],peaks[1]["comparison"])
        self.assertTrue(all(not s["available"] for s in scores if s["field"]=="lod_h"))
        sample["rate_ci95"] = [.365,.343]
        (self.dir/"result.json").write_text(json.dumps(sample))
        with self.assertRaises(ValueError): score_task(self.tasks["xiamaling-precession"],self.dir)

    def test_hays_ratio_uses_the_same_core_and_is_scale_invariant(self):
        task = self.tasks["hays76-simplex"]
        periods = {k:v for k,v in zip(task["output_fields"], [87,38,21,109,47,24])}
        for factor in (1,2):
            (self.dir/"result.json").write_text(json.dumps({k:factor*v for k,v in periods.items()}))
            result = score_task(task,self.dir)["metrics"]
            ratios = [m for m in result if m["quantity"]=="period_ratio"]
            np.testing.assert_allclose([m["value"] for m in ratios],[38/21,47/24])
            self.assertEqual([m["reference"] for m in ratios],[1.8,1.9])

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
