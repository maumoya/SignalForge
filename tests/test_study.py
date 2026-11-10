import json,tempfile,unittest
from pathlib import Path
from signalforge import analyze,SignalError
from signalforge.features import run_hypotheses,main,_benjamini_hochberg
from tests.test_core import item

ROOT=Path(__file__).resolve().parent.parent
SAMPLE=json.loads((ROOT/"examples/study/videos.json").read_text(encoding="utf-8"))
HYPOTHESES=json.loads((ROOT/"examples/study/hypotheses.json").read_text(encoding="utf-8"))

class ProtocolOptionTests(unittest.TestCase):
    def test_defaults_unchanged(self):
        r=analyze([item(i) for i in range(8)])
        self.assertEqual(r["parameters"],{"neighbors_each_side":10,"minimum_neighbors":5,"drop_newest":0})
        self.assertEqual(r["items"][0]["multiplier"],1)
    def test_min_neighbors_ten_leaves_small_channels_unscored(self):
        r=analyze([item(i) for i in range(8)],minimum=10)
        self.assertTrue(all(x["multiplier"] is None for x in r["items"]))
    def test_drop_newest_marks_fresh_and_keeps_them_out_of_baselines(self):
        r=analyze([item(i,9000 if i>=20 else 100) for i in range(25)],drop_newest=5)["items"]
        self.assertEqual([x["evidence_level"] for x in r[20:]],["too-fresh"]*5)
        self.assertTrue(all(x["multiplier"] is None for x in r[20:]))
        self.assertEqual((r[19]["baseline"],r[19]["neighbor_count"]),(100,10))
    def test_bad_options_rejected(self):
        for kw in ({"minimum":0},{"minimum":21},{"drop_newest":-1},{"drop_newest":51},{"minimum":True}):
            with self.subTest(kw=kw),self.assertRaises(SignalError): analyze([item(0)],**kw)
    def test_distribution_shares(self):
        d=analyze([item(i,1100 if i==10 else 400 if i==5 else 100) for i in range(21)])["distribution"]
        self.assertEqual((d["scored"],d["share_over_3x"],d["share_over_10x"]),(21,round(2/21,4),round(1/21,4)))
    def test_hook_and_duration_are_kept_as_data(self):
        r=analyze([{**item(0),"hook":"Stop  scrolling","duration_seconds":31},{**item(1),"duration_seconds":-4}])["items"]
        self.assertEqual((r[0]["hook"],r[0]["duration_seconds"],r[1]["duration_seconds"]),("Stop scrolling",31,None))

class HypothesisTests(unittest.TestCase):
    def setUp(self):
        self.rows={h["id"]:h for h in run_hypotheses(SAMPLE,HYPOTHESES)["hypotheses"]}
    def test_planted_lift_is_a_rule(self):
        h=self.rows["number-in-title"]
        self.assertEqual(h["verdict"],"rule")
        self.assertTrue(1.3<h["effect_multiplier"]<1.7 and h["ci95"][0]>1 and h["share_creators_as_predicted"]>0.5)
    def test_wrong_prediction_is_reported_reversed(self):
        self.assertEqual(self.rows["tutorial-word"]["verdict"],"reversed")
        self.assertLess(self.rows["tutorial-word"]["effect_multiplier"],1)
    def test_null_feature_is_not_promoted(self):
        self.assertEqual(self.rows["question"]["verdict"],"not supported")
    def test_under_thirty_videos_is_insufficient(self):
        h=self.rows["money"]
        self.assertEqual((h["verdict"],h["effect_multiplier"],h["q_value"]),("insufficient data",None,None))
    def test_unpredicted_effect_is_only_a_lead(self):
        self.assertTrue(self.rows["first-person"]["verdict"].startswith("lead"))
    def test_review_examples_capped_at_ten(self):
        self.assertEqual(len(self.rows["number-in-title"]["review_examples"]),10)
    def test_benjamini_hochberg(self):
        q=_benjamini_hochberg([0.01,0.04,None,0.03])
        self.assertEqual([None if v is None else round(v,4) for v in q],[0.03,0.04,None,0.04])
    def test_hook_field_uses_only_items_with_hooks(self):
        r=run_hypotheses([item(i) for i in range(30)],{"registered_at":"2026-11-10",
            "hypotheses":[{"id":"h","field":"hook","pattern":"stop","direction":"up"}]})["hypotheses"][0]
        self.assertEqual((r["videos_tested"],r["verdict"]),(0,"insufficient data"))
    def test_registration_date_and_shape_required(self):
        ok={"id":"a","pattern":"x","direction":"up"}
        for bad in ({"hypotheses":[ok]},{"registered_at":"yesterday","hypotheses":[ok]},
            {"registered_at":"2026-11-10","hypotheses":[]},{"registered_at":"2026-11-10","hypotheses":[{**ok,"direction":"sideways"}]},
            {"registered_at":"2026-11-10","hypotheses":[{**ok,"pattern":"("}]},{"registered_at":"2026-11-10","hypotheses":[ok,ok]},
            {"registered_at":"2026-11-10","hypotheses":[{**ok,"field":"description"}]},[]):
            with self.subTest(bad=bad),self.assertRaises(SignalError): run_hypotheses([],bad)
    def test_cli_writes_once_and_never_overwrites(self):
        with tempfile.TemporaryDirectory() as d:
            out=Path(d)/"r.json"
            args=[str(ROOT/"examples/study/videos.json"),"--hypotheses",str(ROOT/"examples/study/hypotheses.json"),"--out",str(out)]
            self.assertEqual(main(args),0)
            self.assertEqual(json.loads(out.read_text())["schema_version"],"signalforge-features/1.0")
            self.assertEqual(main(args),2)
    def test_sample_file_matches_its_generator(self):
        import subprocess,sys
        made=subprocess.run([sys.executable,str(ROOT/"examples/study/make_sample.py")],capture_output=True,text=True,check=True).stdout
        self.assertEqual(json.loads(made),SAMPLE)



class IngestTests(unittest.TestCase):
    def test_ytdlp_lines_become_scorable_items(self):
        from signalforge.ingest import convert
        lines=[json.dumps({"webpage_url":f"https://www.youtube.com/shorts/v{i}","extractor_key":"Youtube","uploader_id":"@chan",
            "title":f"Clip {i}","view_count":100,"timestamp":1767225600+86400*i,"duration":30}) for i in range(8)]
        lines+=["not json",json.dumps({"title":"no url"}),json.dumps({"webpage_url":"https://www.youtube.com/shorts/d","upload_date":"20260301"}),""]
        items,skipped=convert(lines,"ai tools")
        self.assertEqual((len(items),skipped),(9,2))
        self.assertEqual(items[8]["published_at"],"2026-03-01T00:00:00+00:00")
        scored=analyze(items)["items"]
        self.assertEqual((scored[0]["platform"],scored[0]["creator"],scored[0]["multiplier"],scored[0]["duration_seconds"]),("youtube","@chan",1,30))
    def test_channel_listing_rows_take_the_creator_from_the_playlist(self):
        from signalforge.ingest import convert
        lines=[json.dumps({"url":f"https://www.youtube.com/watch?v=v{i}","webpage_url":f"https://www.youtube.com/watch?v=v{i}",
            "ie_key":"Youtube","title":f"Talk {i}","view_count":1000,"duration":600,"timestamp":1767225600+86400*i,
            "uploader_id":None,"channel_id":None,"playlist_uploader_id":"@org","playlist_channel_id":"UC123"}) for i in range(6)]
        items,skipped=convert(lines,"")
        self.assertEqual((len(items),skipped),(6,0))
        self.assertEqual({x["creator"] for x in items},{"@org"})
if __name__=="__main__": unittest.main()
