/**
 * Shared calendar data hook — fetches events + terms from the backend
 * and exposes them in the display-ready format the widgets expect.
 *
 * Used by: LandingLayout (upcoming events, term calendar, calendar widget),
 * AppSidebars (CalendarWidgetCompact).
 *
 * Keeps a module-level in-memory cache so the same data isn't re-fetched
 * for every mounted widget on a given page.
 */
import { useEffect, useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// ===== Display-ready shapes (match the previous hardcoded data) =====

export interface DisplayEvent {
  id: string;
  isoDate: string;        // "2026-05-05"
  date: string;           // "May 5"
  day: string;            // "Mon"
  title: string;
  category: 'academic' | 'cocurricular' | 'exam';
  bg: string;
  tc: string;
  dot: string;
}

export interface TermActivity {
  label: string;
  date: string;
}

export interface DisplayTerm {
  id: string;
  name: string;
  period: string;
  status: 'past' | 'current' | 'upcoming';
  displayStatus: 'Past' | 'Current' | 'Upcoming';
  year: number;
  academic: TermActivity[];
  cocurricular: TermActivity[];
  headerBg: string;
  headerText: string;
  badgeBorder: string;
}

// ===== Helpers =====

const MONTH_SHORT = ['Jan', 'Feb', 'Mar', 'Apr', 'May', 'Jun', 'Jul', 'Aug', 'Sep', 'Oct', 'Nov', 'Dec'];
const DAY_SHORT = ['Sun', 'Mon', 'Tue', 'Wed', 'Thu', 'Fri', 'Sat'];

function formatEvent(raw: any): DisplayEvent {
  // Parse YYYY-MM-DD in local time by appending 'T12:00:00' to avoid TZ drift.
  const [y, m, d] = raw.date.split('-').map((v: string) => parseInt(v, 10));
  const dt = new Date(y, m - 1, d);
  return {
    id: raw.id,
    isoDate: raw.date,
    date: `${MONTH_SHORT[m - 1]} ${d}`,
    day: DAY_SHORT[dt.getDay()],
    title: raw.title,
    category: raw.category,
    bg: raw.palette?.bg ?? '#F3F4FF',
    tc: raw.palette?.tc ?? '#3730A3',
    dot: raw.palette?.dot ?? '#5C6BC0',
  };
}

function formatTerm(raw: any): DisplayTerm {
  const status = (raw.status || 'upcoming') as DisplayTerm['status'];
  return {
    id: raw.id,
    name: raw.name,
    period: raw.period,
    status,
    displayStatus: (status.charAt(0).toUpperCase() + status.slice(1)) as DisplayTerm['displayStatus'],
    year: raw.year,
    academic: raw.academic || [],
    cocurricular: raw.cocurricular || [],
    headerBg: raw.palette?.headerBg ?? '#F3F4F6',
    headerText: raw.palette?.headerText ?? '#9CA3AF',
    badgeBorder: raw.palette?.badgeBorder ?? '#DDDDF5',
  };
}

// ===== Module cache =====

let _cache: { events: DisplayEvent[]; terms: DisplayTerm[]; at: number } | null = null;
let _inFlight: Promise<{ events: DisplayEvent[]; terms: DisplayTerm[] }> | null = null;
const CACHE_TTL_MS = 5 * 60 * 1000; // 5 min

async function fetchBoth(): Promise<{ events: DisplayEvent[]; terms: DisplayTerm[] }> {
  const [evRes, tmRes] = await Promise.all([
    axios.get(`${BACKEND_URL}/api/calendar/events`).catch(() => ({ data: { events: [] } })),
    axios.get(`${BACKEND_URL}/api/calendar/terms`).catch(() => ({ data: { terms: [] } })),
  ]);
  return {
    events: (evRes.data.events || []).map(formatEvent),
    terms: (tmRes.data.terms || []).map(formatTerm),
  };
}

/** Internal: returns a fresh promise if any, else schedules one. Dedups
 *  concurrent callers so 5 widgets mounting together share a single fetch. */
function loadCalendar(): Promise<{ events: DisplayEvent[]; terms: DisplayTerm[] }> {
  if (_cache && Date.now() - _cache.at < CACHE_TTL_MS) {
    return Promise.resolve({ events: _cache.events, terms: _cache.terms });
  }
  if (_inFlight) return _inFlight;
  _inFlight = fetchBoth().then((data) => {
    _cache = { ...data, at: Date.now() };
    _inFlight = null;
    return data;
  }).catch((e) => {
    _inFlight = null;
    throw e;
  });
  return _inFlight;
}

export function invalidateCalendarCache() {
  _cache = null;
  _inFlight = null;
}

/** Exposed so unrelated consumers (e.g. NewsStrip) can piggy-back on the
 *  shared cache rather than issuing a duplicate `/api/calendar/events` call. */
export async function getCalendarEvents(): Promise<DisplayEvent[]> {
  const { events } = await loadCalendar();
  return events;
}

// ===== Hook =====

export function useCalendarData() {
  const [events, setEvents] = useState<DisplayEvent[]>(_cache?.events ?? []);
  const [terms, setTerms] = useState<DisplayTerm[]>(_cache?.terms ?? []);
  const [loading, setLoading] = useState(!_cache);

  useEffect(() => {
    const fresh = _cache && Date.now() - _cache.at < CACHE_TTL_MS;
    if (fresh) {
      setEvents(_cache!.events);
      setTerms(_cache!.terms);
      setLoading(false);
      return;
    }
    let cancelled = false;
    loadCalendar()
      .then((data) => {
        if (cancelled) return;
        setEvents(data.events);
        setTerms(data.terms);
        setLoading(false);
      })
      .catch(() => {
        if (!cancelled) setLoading(false);
      });
    return () => {
      cancelled = true;
    };
  }, []);

  return { events, terms, loading };
}
