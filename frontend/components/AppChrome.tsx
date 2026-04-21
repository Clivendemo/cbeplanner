/**
 * Global chrome — NewsStrip (marquee header), GlobalFooter,
 * and BackgroundWrapper. Used by the root layout so every page
 * gets the premium background + scrolling news + footer.
 *
 * Web-only for the animated strip/footer (uses real DOM for
 * perf-friendly CSS animations). On native builds these render as
 * no-ops so layouts are untouched.
 */
import React, { useEffect, useState } from 'react';
import { Platform, View, StyleSheet } from 'react-native';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// ===== Default news items (used if API returns none) =====

const DEFAULT_NEWS: { tag: string; text: string }[] = [
  { tag: 'MoE', text: 'CBC reforms update released by the Ministry of Education' },
  { tag: 'KNEC', text: 'KCSE 2026 timetable now available on the KNEC portal' },
  { tag: 'KICD', text: 'New teacher training guidelines announced for Grades 7–9' },
  { tag: 'TSC', text: 'TSC Online portal enhanced with faster payslip access' },
  { tag: 'Update', text: 'Junior School grade-level assessments go digital in 2026' },
  { tag: 'Tip', text: 'Kenyan teachers: try starting each lesson with a real-life example' },
];

// ===== NewsStrip =====

export const NewsStrip: React.FC = () => {
  const [items, setItems] = useState<{ tag: string; text: string }[]>(DEFAULT_NEWS);

  useEffect(() => {
    // Pull admin-managed upcoming events and turn them into news-ticker rows.
    // Falls back silently to DEFAULT_NEWS on any error.
    let cancelled = false;
    (async () => {
      try {
        const res = await axios.get(`${BACKEND_URL}/api/calendar/events`);
        const events = res.data?.events || [];
        if (cancelled || events.length === 0) return;
        const ev = events.slice(0, 6).map((e: any) => ({
          tag: e.category === 'exam' ? 'Exam' : e.category === 'cocurricular' ? 'Event' : 'Academic',
          text: `${e.title} · ${e.date}`,
        }));
        // Mix with a couple defaults for variety
        setItems([...ev, ...DEFAULT_NEWS.slice(0, 3)]);
      } catch {
        /* keep defaults */
      }
    })();
    return () => { cancelled = true; };
  }, []);

  if (Platform.OS !== 'web') return null;

  // Duplicate the track so the animation loops seamlessly.
  const track = [...items, ...items];

  return (
    <div className="cbepl-news-strip" role="marquee" aria-label="Latest education news" data-testid="news-strip">
      <div className="cbepl-news-track">
        {track.map((n, i) => (
          <span key={i} className="cbepl-news-item">
            <span className="cbepl-news-bullet" />
            <strong>{n.tag}</strong>
            {n.text}
          </span>
        ))}
      </div>
    </div>
  );
};

// ===== Global footer =====

export const GlobalFooter: React.FC = () => {
  if (Platform.OS !== 'web') return null;
  const year = new Date().getFullYear();
  return (
    <footer className="cbepl-footer" data-testid="global-footer">
      © {year} <a href="https://cbeplanner.com">CBE Planner</a>. All rights reserved.
    </footer>
  );
};

// ===== Background wrapper =====
// The premium gradient + animated glow are applied globally on <body> via CSS
// in +html.tsx. This wrapper simply ensures the RN tree fills the viewport and
// anchors the optional NewsStrip at the top / GlobalFooter at the bottom.

interface AppChromeProps {
  children: React.ReactNode;
  showStrip?: boolean;
  showFooter?: boolean;
}

export const AppChrome: React.FC<AppChromeProps> = ({
  children,
  showStrip = true,
  showFooter = true,
}) => {
  if (Platform.OS !== 'web') {
    // Native: no chrome, let RN layouts own the screen.
    return <>{children}</>;
  }
  return (
    <View style={styles.chromeRoot}>
      {showStrip && <NewsStrip />}
      <View style={styles.chromeBody}>{children}</View>
      {showFooter && <GlobalFooter />}
    </View>
  );
};

const styles = StyleSheet.create({
  chromeRoot: { flex: 1, minHeight: '100vh' as any },
  chromeBody: { flex: 1 },
});
