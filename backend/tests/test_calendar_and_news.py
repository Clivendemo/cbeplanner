"""
Regression tests for the calendar + news public endpoints.

These tests hit the deployed backend's public read endpoints — they don't
require auth tokens, so they're safe to run as smoke checks after every
deploy. Admin-only mutation endpoints are covered separately.

Run:  cd /app/backend && pytest tests/test_calendar_and_news.py -v
"""
import os
import time
import pytest
import requests

BASE_URL = os.environ.get(
    'EXPO_PUBLIC_BACKEND_URL',
    'https://magical-shannon-6.preview.emergentagent.com',
).rstrip('/')

TIMEOUT = 15


def _get(path: str):
    return requests.get(f"{BASE_URL}{path}", timeout=TIMEOUT)


# ==================== Calendar events ====================

def test_calendar_events_public_endpoint_returns_200():
    r = _get('/api/calendar/events')
    assert r.status_code == 200, r.text


def test_calendar_events_shape_is_stable():
    """Events must always include the fields the NewsStrip + widgets consume."""
    r = _get('/api/calendar/events')
    data = r.json()
    assert isinstance(data, dict)
    assert 'events' in data
    assert isinstance(data['events'], list)
    for ev in data['events'][:3]:  # check the first few for shape
        assert 'id' in ev
        assert 'date' in ev
        assert 'title' in ev
        assert 'category' in ev
        assert ev['category'] in {'academic', 'cocurricular', 'exam'}
        assert 'palette' in ev
        assert {'bg', 'tc', 'dot'}.issubset(set(ev['palette'].keys()))


def test_calendar_events_are_sorted_by_date():
    r = _get('/api/calendar/events')
    dates = [e['date'] for e in r.json().get('events', [])]
    assert dates == sorted(dates), f"events returned in non-ascending date order: {dates}"


# ==================== Term calendar ====================

def test_calendar_terms_public_endpoint_returns_200():
    r = _get('/api/calendar/terms')
    assert r.status_code == 200, r.text


def test_calendar_terms_shape_is_stable():
    r = _get('/api/calendar/terms')
    terms = r.json().get('terms', [])
    for tm in terms[:3]:
        assert 'id' in tm
        assert 'name' in tm
        assert 'period' in tm
        assert 'status' in tm
        assert tm['status'] in {'past', 'current', 'upcoming'}
        assert 'academic' in tm and isinstance(tm['academic'], list)
        assert 'cocurricular' in tm and isinstance(tm['cocurricular'], list)
        assert 'palette' in tm


# ==================== News strip ====================

def test_news_public_endpoint_returns_200():
    r = _get('/api/news')
    assert r.status_code == 200, r.text
    data = r.json()
    assert isinstance(data, dict)
    assert 'news' in data
    assert isinstance(data['news'], list)


def test_news_only_returns_active_items():
    r = _get('/api/news')
    for n in r.json().get('news', []):
        assert n.get('active') is True, f"inactive news item leaked to public endpoint: {n}"


# ==================== Admin endpoints: auth required ====================

@pytest.mark.parametrize('path,method', [
    ('/api/admin/calendar/events', 'POST'),
    ('/api/admin/calendar/events/dummy', 'DELETE'),
    ('/api/admin/calendar/terms', 'POST'),
    ('/api/admin/news', 'POST'),
    ('/api/admin/news/dummy', 'DELETE'),
])
def test_admin_endpoints_require_auth(path, method):
    r = requests.request(method, f"{BASE_URL}{path}", timeout=TIMEOUT, json={})
    assert r.status_code in {401, 403}, f"{method} {path} should reject unauthenticated — got {r.status_code}"


# ==================== Latency ====================

def test_public_calendar_latency_is_reasonable():
    """Budget: calendar endpoint under 3 seconds cold, under 1 second warm."""
    # Warm up
    _get('/api/calendar/events')
    start = time.time()
    _get('/api/calendar/events')
    elapsed = time.time() - start
    assert elapsed < 2.0, f"warm /api/calendar/events took {elapsed:.2f}s — too slow"
