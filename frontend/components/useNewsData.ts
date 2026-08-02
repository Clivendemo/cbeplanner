/**
 * useNewsData — shared hook for /api/news
 *
 * Keeps a module-level in-memory cache (5-min TTL) so multiple widgets
 * on the same page share a single fetch, matching the pattern in
 * useCalendarData.
 *
 * Used by: AppChrome (NewsStrip), LoginShellWidgets (NewsCard)
 */
import { useEffect, useState } from 'react';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

export interface NewsItem {
  tag: string;
  text: string;
}

export const DEFAULT_NEWS: NewsItem[] = [
  { tag: 'MoE',    text: 'CBC reforms update released by the Ministry of Education' },
  { tag: 'KNEC',   text: 'KCSE 2026 timetable now available on the KNEC portal' },
  { tag: 'KICD',   text: 'New teacher training guidelines announced for Grades 7–9' },
  { tag: 'TSC',    text: 'TSC Online portal enhanced with faster payslip access' },
  { tag: 'Update', text: 'Junior School grade-level assessments go digital in 2026' },
  { tag: 'Tip',    text: 'Kenyan teachers: try starting each lesson with a real-life example' },
];

const NEWS_TTL_MS = 5 * 60 * 1000; // 5 min

let _newsCache: { data: NewsItem[]; at: number } | null = null;
let _newsInFlight: Promise<NewsItem[]> | null = null;

export async function loadNews(): Promise<NewsItem[]> {
  if (_newsCache && Date.now() - _newsCache.at < NEWS_TTL_MS) return _newsCache.data;
  if (_newsInFlight) return _newsInFlight;
  _newsInFlight = axios
    .get(`${BACKEND_URL}/api/news`)
    .then((r) => {
      const data: NewsItem[] = (r.data?.news || []).map((n: any) => ({
        tag: n.tag,
        text: n.text,
      }));
      _newsCache = { data, at: Date.now() };
      _newsInFlight = null;
      return data;
    })
    .catch(() => {
      _newsInFlight = null;
      return DEFAULT_NEWS;
    });
  return _newsInFlight;
}

export function invalidateNewsCache() {
  _newsCache = null;
  _newsInFlight = null;
}

export function useNewsData() {
  const [items, setItems]   = useState<NewsItem[]>(_newsCache?.data ?? DEFAULT_NEWS);
  const [loading, setLoading] = useState(!_newsCache);

  useEffect(() => {
    if (_newsCache && Date.now() - _newsCache.at < NEWS_TTL_MS) {
      setItems(_newsCache.data);
      setLoading(false);
      return;
    }
    let cancelled = false;
    loadNews().then((data) => {
      if (!cancelled) {
        setItems(data.length > 0 ? data : DEFAULT_NEWS);
        setLoading(false);
      }
    });
    return () => { cancelled = true; };
  }, []);

  return { items, loading };
}
