"""Coverage-guided fuzzing for user-supplied metadata and URL input."""
import json
import sys
import atheris
with atheris.instrument_imports():
    from signalforge.core import SignalError, clean_text, load_items, safe_url

@atheris.instrument_func
def test_one_input(data):
    if len(data)>2048:
        data=data[:2048]
    value=data.decode("utf-8","replace")
    cleaned=clean_text(value)
    assert isinstance(cleaned,str)
    assert len(cleaned)<=2000

    # Fuzz the trust boundary without ever visiting the URL.
    try:
        parsed=safe_url(value)
    except SignalError:
        pass
    else:
        assert parsed.startswith("https://")

    # Fuzz the JSON ingestion boundary with plausible attacker-controlled values.
    try:
        doc=json.loads(value)
    except (ValueError,UnicodeError):
        return
    try:
        result=load_items(doc)
    except SignalError:
        return
    assert isinstance(result,list)
    for item in result:
        assert item["url"].startswith("https://")
        assert item["views"] is None or isinstance(item["views"],int)

if __name__=="__main__":
    atheris.Setup(sys.argv,test_one_input)
    atheris.Fuzz()
