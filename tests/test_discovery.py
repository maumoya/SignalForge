import io,json,unittest
from datetime import datetime,timezone
from urllib.error import HTTPError
from signalforge.core import SignalError
from signalforge.discovery import search_public_repositories,export_github_candidates

NOW=datetime(2026,11,8,tzinfo=timezone.utc)
def repo(name="org/tool",url="https://github.com/org/tool",stars=100,archived=False):
    return {"full_name":name,"html_url":url,"description":"Helpful local agent",
      "stargazers_count":stars,"forks_count":12,
      "pushed_at":"2026-11-01T00:00:00Z","archived":archived}
class Reply:
    status=200
    def __init__(self,items, url):
        self.body=json.dumps({"items":items}).encode()
        self.url=url
    def __enter__(self):return self
    def __exit__(self,*args):return False
    def geturl(self):return self.url
    def read(self,n):return self.body[:n]
class Client:
    def __init__(self,items,override_url=None):self.items=items;self.override_url=override_url;self.requests=[]
    def open(self,req,timeout=10):
        self.requests.append((req.full_url,timeout))
        return Reply(self.items,self.override_url or req.full_url)

class PublicGitHubTests(unittest.TestCase):
    def test_fixed_origin_and_bounded_request(self):
        c=Client([repo()])
        a=search_public_repositories("local coding agents",limit=5,opener=c,now=NOW)
        self.assertIn("api.github.com/search/repositories",c.requests[0][0])
        self.assertIn("per_page=5",c.requests[0][0])
        self.assertEqual(c.requests[0][1],10)
        self.assertEqual(len(a["repositories"]),1)
    def test_rejects_private_url(self):
        c=Client([repo(url="https://127.0.0.1/secret"),repo(name="a/b",url="file:///etc/passwd")])
        self.assertEqual(search_public_repositories("agents",opener=c,now=NOW)["repositories"],[])
    def test_redirected_origin_rejected(self):
        c=Client([repo()],override_url="https://attacker.example/data")
        with self.assertRaises(SignalError):search_public_repositories("agents",opener=c,now=NOW)
    def test_bad_queries_rejected(self):
        for q in ("","x","a\nb","a"*101):
            with self.subTest(q=q),self.assertRaises(SignalError):
                search_public_repositories(q,opener=Client([]),now=NOW)
    def test_deduplicate_and_nonnegative(self):
        c=Client([repo(),repo(stars=-30),repo(name="org/other",url="https://github.com/org/other",stars=-1)])
        result=search_public_repositories("agents",opener=c,now=NOW)
        self.assertEqual(len(result["repositories"]),2)
        self.assertEqual(next(x for x in result["repositories"] if x["full_name"]=="org/other")["stars"],0)
    def test_approval_gated_candidates(self):
        report=search_public_repositories("agents",opener=Client([repo()]),now=NOW)
        a=export_github_candidates(report)
        self.assertEqual(a["schema_version"],"signalforge-candidates/1.0")
        self.assertTrue(a["read_only"] and a["no_auto_install"])
        self.assertEqual(a["candidates"][0]["status"],"investigate-only")
        self.assertTrue(a["candidates"][0]["owner_approval_required"])
    def test_zero_internet_for_injected_mock(self):
        c=Client([repo()])
        a=search_public_repositories("agents",opener=c,now=NOW)
        self.assertEqual(len(c.requests),1)
        self.assertEqual(a["repositories"][0]["security_status"],"unverified")
    def test_score_never_claims_security(self):
        a=search_public_repositories("agents",opener=Client([repo(stars=5000)]),now=NOW)
        self.assertLessEqual(a["repositories"][0]["research_attention_score"],100)
        self.assertEqual(a["repositories"][0]["implementation_status"],"not-assessed")

if __name__=="__main__":unittest.main()
