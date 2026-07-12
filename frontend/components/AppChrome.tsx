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
import { getCalendarEvents } from './useCalendarData';
import { loadNews, DEFAULT_NEWS } from './useNewsData';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

// News loading + defaults moved to useNewsData.ts

// ===== NewsStrip =====

export const NewsStrip: React.FC = () => {
  const [items, setItems] = useState<{ tag: string; text: string }[]>(DEFAULT_NEWS);

  useEffect(() => {
    // Merge: admin-created announcements + upcoming events from the calendar.
    // Both sources are module-level cached, so mounting NewsStrip multiple
    // times (route navigation re-mounts AppChrome) does NOT re-fire requests.
    let cancelled = false;
    (async () => {
      try {
        const [news, events] = await Promise.all([
          loadNews(),
          getCalendarEvents().catch(() => []),
        ]);
        if (cancelled) return;
        const evItems = events.slice(0, 6).map((e: any) => ({
          tag: e.category === 'exam' ? 'Exam' : e.category === 'cocurricular' ? 'Event' : 'Academic',
          text: `${e.title} · ${e.date}`,
        }));
        const combined = [...news, ...evItems];
        setItems(combined.length > 0 ? combined : DEFAULT_NEWS);
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
