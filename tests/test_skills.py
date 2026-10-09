import pytest
import skills

opened_urls = []

@pytest.fixture(autouse=True)
def no_side_effects(monkeypatch):
    opened_urls.clear()
    monkeypatch.setattr(skills.webbrowser, "open", lambda url, new=0: opened_urls.append(url) or True)
    monkeypatch.setattr(skills.os, "startfile", lambda url: opened_urls.append(url), raising=False)
    monkeypatch.setattr(skills.subprocess, "Popen", lambda *a, **k: None)
    monkeypatch.setattr(skills, "adjust_volume", lambda action, steps=5: f"volume {action}")
    monkeypatch.setattr(skills, "get_wikipedia_summary", lambda t: (True, f"wiki:{t}", None))
    monkeypatch.setattr(skills, "get_live_weather", lambda c: (True, f"weather:{c}", None))

@pytest.mark.parametrize("cmd", ["open knowledge base", "open barcode scanner", "open calculus notes", "open x ray"])
def test_open_requires_exact_name(cmd):
    handled, _, _ = skills.execute_skill(cmd)
    assert handled is False

def test_open_known_app():
    handled, resp, _ = skills.execute_skill("open notepad")
    assert handled and "Notepad" in resp

def test_weather_extracts_city():
    _, resp, _ = skills.execute_skill("what's the weather like in new york right now")
    assert resp == "weather:new york"

def test_wikipedia_routing():
    _, resp, _ = skills.execute_skill("what is quantum computing")
    assert resp == "wiki:quantum computing"

def test_volume():
    _, resp, _ = skills.execute_skill("volume up")
    assert resp == "volume up"

def test_launch_url_rejects_injection():
    assert skills.launch_url('https://x.com" & calc & "') is False
    assert opened_urls == []
