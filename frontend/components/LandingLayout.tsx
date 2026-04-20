import React, { useEffect, useState } from 'react';
import { View, Text, Pressable, StyleSheet, Linking, useWindowDimensions, ScrollView } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { useRouter } from 'expo-router';
import { useAuth } from '../contexts/AuthContext';

// ===== BREAKPOINTS =====
const BP_DESKTOP = 1024;
const BP_TABLET = 768;

// ===== DATA =====
const FACTS = [
  'CBC was introduced in Kenya in 2017, replacing the 8-4-4 system.',
  'CBC focuses on values, skills and competencies over memorization.',
  'There are 7 core competencies in the CBC framework.',
  'CBC introduces learners to career pathways from Grade 7.',
  'Parental involvement is a key pillar of the CBC model.',
];

const QUOTES = [
  { text: 'Education is not the filling of a pail, but the lighting of a fire.', author: 'W.B. Yeats' },
  { text: 'The art of teaching is the art of assisting discovery.', author: 'Mark Van Doren' },
  { text: 'A good teacher can inspire hope and ignite the imagination.', author: 'Brad Henry' },
];

const UPCOMING_EVENTS = [
  { date: 'May 5', day: 'Mon', title: 'Term 2 Opens', bg: '#EEF2FF', tc: '#3730A3', dot: '#5B5BD6' },
  { date: 'May 12', day: 'Mon', title: 'Mid-Term CATs Begin', bg: '#EEF2FF', tc: '#3730A3', dot: '#5B5BD6' },
  { date: 'May 16', day: 'Fri', title: 'Inter-School Athletics', bg: '#F0FDF4', tc: '#166534', dot: '#16A34A' },
  { date: 'May 23', day: 'Fri', title: 'Drama Festival — Zonal', bg: '#F0FDF4', tc: '#166534', dot: '#16A34A' },
  { date: 'May 30', day: 'Fri', title: 'Mid-Term Break Starts', bg: '#EEF2FF', tc: '#3730A3', dot: '#5B5BD6' },
  { date: 'Jun 6', day: 'Fri', title: 'Schools Reopen', bg: '#EEF2FF', tc: '#3730A3', dot: '#5B5BD6' },
  { date: 'Jul 4', day: 'Fri', title: 'Term 2 Exams Start', bg: '#FFF7ED', tc: '#9A3412', dot: '#EA580C' },
  { date: 'Aug 1', day: 'Fri', title: 'Term 2 Closes', bg: '#FFF7ED', tc: '#9A3412', dot: '#EA580C' },
  { date: 'Aug 8', day: 'Fri', title: 'Music Festival — County', bg: '#F0FDF4', tc: '#166534', dot: '#16A34A' },
];

const USEFUL_LINKS = [
  { label: 'Ministry of Education', url: 'https://education.go.ke' },
  { label: 'KNEC Portal', url: 'https://www.knec.ac.ke' },
  { label: 'CBC / CBE Portal', url: 'https://cbcportal.ac.ke' },
  { label: 'KICD Resources', url: 'https://kicd.ac.ke' },
  { label: 'TSC Online', url: 'https://www.tsc.go.ke' },
];

const TIPS: Record<number, string> = {
  0: 'Review your scheme of work and align it with KICD guidelines.',
  1: 'Start lessons with a warm-up activity to activate prior knowledge.',
  2: 'Use differentiated tasks to cater for all learner abilities.',
  3: 'Include formative assessment checkpoints every 15 minutes.',
  4: 'Incorporate local context and real-world Kenyan examples.',
  5: 'End each week by reviewing learning objectives with your class.',
  6: 'Prep visual aids and manipulatives for the coming week.',
};

const SUBJECTS = ['Mathematics', 'English', 'Kiswahili', 'Science', 'Social Studies', 'CRE', 'Creative Arts', 'Agriculture', 'Life Skills'];

const TERM_CALENDAR = [
  {
    name: 'Term 1', period: 'Jan 6 – Apr 4', status: 'Past',
    headerBg: '#F3F4F6', headerText: '#9CA3AF', badgeBorder: '#E5E7EB',
    academic: [
      { label: 'Schools open', date: 'Jan 6' },
      { label: 'Mid-term break', date: 'Feb 21–28' },
      { label: 'End-term exams', date: 'Mar 24–28' },
      { label: 'Schools close', date: 'Apr 4' },
    ],
    cocurricular: [
      { label: 'Debating — Zonal', date: 'Feb 14' },
      { label: 'Athletics — Sub-county', date: 'Mar 7' },
      { label: 'Music Festival — Zonal', date: 'Mar 21' },
    ],
  },
  {
    name: 'Term 2', period: 'Apr 29 – Aug 1', status: 'Current',
    headerBg: '#EEF2FF', headerText: '#3730A3', badgeBorder: '#C7D2FE',
    academic: [
      { label: 'Schools open', date: 'Apr 29' },
      { label: 'Mid-term CATs', date: 'May 12–16' },
      { label: 'Mid-term break', date: 'May 30–Jun 6' },
      { label: 'End-term exams', date: 'Jul 21–25' },
      { label: 'Schools close', date: 'Aug 1' },
    ],
    cocurricular: [
      { label: 'Athletics — County', date: 'May 16' },
      { label: 'Drama — Zonal', date: 'May 23' },
      { label: 'Games — Sub-county', date: 'Jun 20' },
      { label: 'Music — County', date: 'Aug 8' },
    ],
  },
  {
    name: 'Term 3', period: 'Aug 26 – Oct 31', status: 'Upcoming',
    headerBg: '#F0FDF4', headerText: '#166534', badgeBorder: '#BBF7D0',
    academic: [
      { label: 'Schools open', date: 'Aug 26' },
      { label: 'Mid-term break', date: 'Sep 26–Oct 3' },
      { label: 'End-term exams', date: 'Oct 20–24' },
      { label: 'Schools close', date: 'Oct 31' },
    ],
    cocurricular: [
      { label: 'Drama — National', date: 'Sep 5' },
      { label: 'Athletics — National', date: 'Sep 19' },
      { label: 'Music — National', date: 'Oct 10' },
      { label: 'Science Congress', date: 'Oct 17' },
    ],
  },
];

const FEATURE_TILES = [
  { icon: 'document-text-outline', label: 'Generate Scheme of Work', bg: '#EEF2FF', color: '#3730A3', border: '#C7D2FE', route: '/(teacher)/schemes' },
  { icon: 'create-outline', label: 'Generate Lesson Plan', bg: '#F0FDF4', color: '#166534', border: '#BBF7D0', route: '/(teacher)/home' },
  { icon: 'book-outline', label: 'Generate Lesson Notes', bg: '#FFF7ED', color: '#9A3412', border: '#FED7AA', route: '/(teacher)/notes' },
  { icon: 'download-outline', label: 'Download CBC Past Papers', bg: '#EFF6FF', color: '#1E40AF', border: '#BFDBFE', route: '/(teacher)/revision' },
];

// ===== AD SLOT =====
const AdSlot: React.FC<{ width: number; height: number }> = ({ width, height }) => (
  <View style={{ alignItems: 'center' }}>
    <Text style={styles.adLabel}>Advertisement</Text>
    <View style={[styles.adBox, { maxWidth: width, height, width: '100%' }]}>
      <Text style={styles.adPlaceholderText}>{width} × {height}</Text>
    </View>
  </View>
);

// ===== WIDGETS =====
const DidYouKnowWidget: React.FC = () => {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx((i) => (i + 1) % FACTS.length), 8000);
    return () => clearInterval(t);
  }, []);
  return (
    <View style={styles.widgetCard}>
      <Text style={styles.widgetTitle}>Did You Know?</Text>
      <Text style={styles.widgetFact}>{FACTS[idx]}</Text>
      <View style={styles.dotRow}>
        {FACTS.map((_, i) => (
          <View key={i} style={[styles.dot, i === idx && styles.dotActive]} />
        ))}
      </View>
    </View>
  );
};

const MPESA_STEPS = [
  'Open MPesa on your phone',
  'Select Lipa na MPesa',
  'Select Buy Goods & Services',
  'Enter Till No. 8336258',
  'Enter amount & your M-PIN',
];

export const MPesaPaymentWidget: React.FC = () => (
  <View style={mpesaStyles.card} data-testid="mpesa-payment-widget">
    {/* Green accent bar on left edge */}
    <View style={mpesaStyles.accentBar} />

    <View style={mpesaStyles.inner}>
      {/* Header row */}
      <View style={mpesaStyles.headerRow}>
        <View style={mpesaStyles.iconSquare}>
          <Ionicons name="card-outline" size={16} color="#16a34a" />
        </View>
        <Text style={mpesaStyles.headerTitle}>MPesa Payment</Text>
      </View>

      {/* Message */}
      <Text style={mpesaStyles.message}>
        If your STK push did not arrive, pay manually via{' '}
        <Text style={mpesaStyles.bold}>Buy Goods</Text> on MPesa:
      </Text>

      {/* Till number highlight */}
      <View style={mpesaStyles.tillBox}>
        <View>
          <Text style={mpesaStyles.tillLabel}>Till Number</Text>
          <Text style={mpesaStyles.tillNumber}>8336258</Text>
        </View>
        <View style={mpesaStyles.tillBadge}>
          <Text style={mpesaStyles.tillBadgeText}>Buy Goods</Text>
        </View>
      </View>

      {/* Steps */}
      <View style={{ gap: 4 }}>
        {MPESA_STEPS.map((step, i) => (
          <View key={i} style={mpesaStyles.stepRow}>
            <View style={mpesaStyles.stepBullet}>
              <Text style={mpesaStyles.stepBulletText}>{i + 1}</Text>
            </View>
            <Text style={mpesaStyles.stepText}>{step}</Text>
          </View>
        ))}
      </View>

      {/* Footer note */}
      <View style={mpesaStyles.footerDivider} />
      <Text style={mpesaStyles.footerNote}>
        After payment, refresh the page or contact support at{' '}
        <Text
          style={mpesaStyles.footerEmail}
          onPress={() => Linking.openURL('mailto:legitlab@outlook.com')}
        >
          legitlab@outlook.com
        </Text>{' '}
        with your transaction code.
      </Text>
    </View>
  </View>
);

const mpesaStyles = StyleSheet.create({
  card: {
    backgroundColor: '#F0FDF4',
    borderWidth: 1,
    borderColor: '#86EFAC',
    borderRadius: 12,
    paddingVertical: 12,
    paddingHorizontal: 14,
    position: 'relative',
    overflow: 'hidden',
  },
  accentBar: {
    position: 'absolute',
    left: 0,
    top: 0,
    bottom: 0,
    width: 4,
    backgroundColor: '#16a34a',
    borderTopLeftRadius: 12,
    borderBottomLeftRadius: 12,
  },
  inner: { paddingLeft: 8 },
  headerRow: { flexDirection: 'row', alignItems: 'center', gap: 7, marginBottom: 8 },
  iconSquare: {
    width: 28,
    height: 28,
    borderRadius: 8,
    backgroundColor: '#dcfce7',
    alignItems: 'center',
    justifyContent: 'center',
  },
  headerTitle: { fontSize: 12, fontWeight: '600', color: '#166534' },
  message: { fontSize: 11, color: '#166534', lineHeight: 17, opacity: 0.9, marginBottom: 10 },
  bold: { fontWeight: '700' },
  tillBox: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#86EFAC',
    borderRadius: 8,
    paddingVertical: 8,
    paddingHorizontal: 12,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  tillLabel: { fontSize: 9, color: '#6B7280', letterSpacing: 0.5, textTransform: 'uppercase' },
  tillNumber: { fontSize: 18, fontWeight: '700', color: '#166534', letterSpacing: 0.8 },
  tillBadge: { backgroundColor: '#dcfce7', borderRadius: 6, paddingVertical: 4, paddingHorizontal: 8 },
  tillBadgeText: { fontSize: 10, fontWeight: '600', color: '#166534' },
  stepRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 7 },
  stepBullet: {
    width: 16,
    height: 16,
    borderRadius: 8,
    backgroundColor: '#16a34a',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 1,
  },
  stepBulletText: { fontSize: 9, color: '#FFFFFF', fontWeight: '700', lineHeight: 10 },
  stepText: { fontSize: 11, color: '#166534', lineHeight: 16, opacity: 0.85, flex: 1 },
  footerDivider: { height: 1, backgroundColor: '#bbf7d0', marginTop: 10, marginBottom: 8 },
  footerNote: { fontSize: 10, color: '#6B7280', lineHeight: 15 },
  footerEmail: { color: '#16a34a', fontWeight: '500' },
});

// ===== CALENDAR WIDGET =====
// Parses "May 5" → { month: 4, day: 5 } (0-indexed month)
const MONTH_MAP: Record<string, number> = {
  jan: 0, feb: 1, mar: 2, apr: 3, may: 4, jun: 5,
  jul: 6, aug: 7, sep: 8, oct: 9, nov: 10, dec: 11,
};
const MONTH_NAMES = [
  'January', 'February', 'March', 'April', 'May', 'June',
  'July', 'August', 'September', 'October', 'November', 'December',
];
const DAY_LABELS = ['S', 'M', 'T', 'W', 'T', 'F', 'S'];

type CalEvent = { day: number; title: string; dot: string; bg: string; tc: string };

function parseEventsForMonth(year: number, monthIdx: number): CalEvent[] {
  const out: CalEvent[] = [];
  for (const ev of UPCOMING_EVENTS) {
    // "May 5" → ["May", "5"]
    const m = ev.date.match(/^([A-Za-z]+)\s+(\d+)$/);
    if (!m) continue;
    const mIdx = MONTH_MAP[m[1].slice(0, 3).toLowerCase()];
    if (mIdx !== monthIdx) continue;
    out.push({
      day: parseInt(m[2], 10),
      title: ev.title,
      dot: ev.dot,
      bg: ev.bg,
      tc: ev.tc,
    });
  }
  return out;
}

const CalendarWidget: React.FC = () => {
  const today = new Date();
  const [viewMonth, setViewMonth] = useState(today.getMonth());
  const [viewYear, setViewYear] = useState(today.getFullYear());
  const [openDay, setOpenDay] = useState<number | null>(null);

  const monthEvents = parseEventsForMonth(viewYear, viewMonth);
  const eventsByDay = new Map<number, CalEvent[]>();
  for (const e of monthEvents) {
    const list = eventsByDay.get(e.day) ?? [];
    list.push(e);
    eventsByDay.set(e.day, list);
  }

  const firstOfMonth = new Date(viewYear, viewMonth, 1).getDay(); // 0=Sun
  const daysInMonth = new Date(viewYear, viewMonth + 1, 0).getDate();
  const isCurrentMonth = viewMonth === today.getMonth() && viewYear === today.getFullYear();
  const todayDay = today.getDate();

  const cells: Array<number | null> = [];
  for (let i = 0; i < firstOfMonth; i++) cells.push(null);
  for (let d = 1; d <= daysInMonth; d++) cells.push(d);
  while (cells.length % 7 !== 0) cells.push(null);

  const handleDayPress = (day: number) => {
    if (!eventsByDay.has(day)) return; // no action on empty date
    setOpenDay((cur) => (cur === day ? null : day)); // toggle same date
  };

  const goPrev = () => {
    setOpenDay(null);
    if (viewMonth === 0) { setViewMonth(11); setViewYear((y) => y - 1); }
    else setViewMonth((m) => m - 1);
  };
  const goNext = () => {
    setOpenDay(null);
    if (viewMonth === 11) { setViewMonth(0); setViewYear((y) => y + 1); }
    else setViewMonth((m) => m + 1);
  };

  return (
    <View style={styles.widgetCard} data-testid="calendar-widget">
      {/* Header */}
      <View style={calStyles.header}>
        <Pressable onPress={goPrev} style={calStyles.navBtn} hitSlop={8} data-testid="calendar-prev">
          <Ionicons name="chevron-back" size={14} color="#5B5BD6" />
        </Pressable>
        <Text style={calStyles.monthLabel}>{MONTH_NAMES[viewMonth]} {viewYear}</Text>
        <Pressable onPress={goNext} style={calStyles.navBtn} hitSlop={8} data-testid="calendar-next">
          <Ionicons name="chevron-forward" size={14} color="#5B5BD6" />
        </Pressable>
      </View>

      {/* Day labels */}
      <View style={calStyles.row}>
        {DAY_LABELS.map((l, i) => (
          <View key={i} style={calStyles.cell}>
            <Text style={calStyles.dayLabel}>{l}</Text>
          </View>
        ))}
      </View>

      {/* Date grid */}
      {Array.from({ length: cells.length / 7 }).map((_, rowIdx) => (
        <View key={rowIdx} style={calStyles.row}>
          {cells.slice(rowIdx * 7, rowIdx * 7 + 7).map((day, colIdx) => {
            if (day === null) {
              return <View key={colIdx} style={calStyles.cell} />;
            }
            const evs = eventsByDay.get(day);
            const hasEvent = !!evs;
            const isToday = isCurrentMonth && day === todayDay;
            const firstEv = evs?.[0];
            return (
              <Pressable
                key={colIdx}
                onPress={() => handleDayPress(day)}
                style={calStyles.cell}
                data-testid={`calendar-day-${day}`}
              >
                <View
                  style={[
                    calStyles.dayPill,
                    isToday && calStyles.dayPillToday,
                    hasEvent && firstEv && { backgroundColor: firstEv.bg },
                  ]}
                >
                  <Text
                    style={[
                      calStyles.dayNum,
                      isToday && calStyles.dayNumToday,
                      hasEvent && firstEv && { color: firstEv.tc, fontWeight: '700' },
                    ]}
                  >
                    {day}
                  </Text>
                  {hasEvent && firstEv && !isToday && (
                    <View style={[calStyles.eventDot, { backgroundColor: firstEv.dot }]} />
                  )}
                </View>
              </Pressable>
            );
          })}
        </View>
      ))}

      {/* Popover for selected day */}
      {openDay !== null && eventsByDay.has(openDay) && (
        <View style={calStyles.popover} data-testid="calendar-popover">
          <View style={calStyles.popoverHeader}>
            <Text style={calStyles.popoverDate}>
              {MONTH_NAMES[viewMonth]} {openDay}
            </Text>
            <Pressable onPress={() => setOpenDay(null)} hitSlop={8} data-testid="calendar-popover-close">
              <Ionicons name="close" size={12} color="#6B7280" />
            </Pressable>
          </View>
          {(eventsByDay.get(openDay) ?? []).map((e, i) => (
            <View key={i} style={calStyles.popoverRow}>
              <View style={[calStyles.popoverDot, { backgroundColor: e.dot }]} />
              <Text style={calStyles.popoverTitle}>{e.title}</Text>
            </View>
          ))}
        </View>
      )}

      {/* Legend */}
      <View style={calStyles.legend}>
        <View style={[styles.legendDot, { backgroundColor: '#5B5BD6' }]} />
        <Text style={styles.legendText}>Academic</Text>
        <View style={[styles.legendDot, { backgroundColor: '#16A34A', marginLeft: 8 }]} />
        <Text style={styles.legendText}>Co-curr</Text>
        <View style={[styles.legendDot, { backgroundColor: '#EA580C', marginLeft: 8 }]} />
        <Text style={styles.legendText}>Exams</Text>
      </View>
    </View>
  );
};

const calStyles = StyleSheet.create({
  header: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 8,
  },
  navBtn: { padding: 4 },
  monthLabel: { fontSize: 12, fontWeight: '700', color: '#111827' },
  row: { flexDirection: 'row' },
  cell: {
    flex: 1,
    aspectRatio: 1,
    alignItems: 'center',
    justifyContent: 'center',
    padding: 2,
  },
  dayLabel: { fontSize: 9, fontWeight: '700', color: '#9CA3AF', letterSpacing: 0.3 },
  dayPill: {
    width: '100%',
    height: '100%',
    borderRadius: 6,
    alignItems: 'center',
    justifyContent: 'center',
    position: 'relative',
  },
  dayPillToday: {
    backgroundColor: '#5B5BD6',
  },
  dayNum: { fontSize: 11, color: '#374151', fontWeight: '500' },
  dayNumToday: { color: '#FFFFFF', fontWeight: '700' },
  eventDot: {
    position: 'absolute',
    bottom: 2,
    width: 4,
    height: 4,
    borderRadius: 2,
  },
  popover: {
    marginTop: 10,
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    padding: 8,
  },
  popoverHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 4,
  },
  popoverDate: { fontSize: 11, fontWeight: '700', color: '#111827' },
  popoverRow: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 2 },
  popoverDot: { width: 5, height: 5, borderRadius: 3 },
  popoverTitle: { fontSize: 10, color: '#374151', flex: 1 },
  legend: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    marginTop: 10,
    gap: 3,
  },
});

const UpcomingEventsWidget: React.FC = () => (
  <View style={styles.widgetCard}>
    <View style={styles.widgetHeaderRow}>
      <Text style={styles.widgetTitle}>Upcoming Events</Text>
      <View style={styles.legendRow}>
        <View style={[styles.legendDot, { backgroundColor: '#5B5BD6' }]} />
        <Text style={styles.legendText}>Academic</Text>
        <View style={[styles.legendDot, { backgroundColor: '#16A34A', marginLeft: 6 }]} />
        <Text style={styles.legendText}>Co-curr</Text>
      </View>
    </View>
    <View style={{ gap: 6 }}>
      {UPCOMING_EVENTS.map((ev, i) => (
        <View key={i} style={styles.eventRow}>
          <View style={[styles.eventDateBlock, { backgroundColor: ev.bg }]}>
            <Text style={[styles.eventDayName, { color: ev.tc }]}>{ev.day}</Text>
            <Text style={[styles.eventDateNum, { color: ev.tc }]}>{ev.date}</Text>
          </View>
          <View style={styles.eventContent}>
            <View style={[styles.eventDot, { backgroundColor: ev.dot }]} />
            <Text style={styles.eventTitle} numberOfLines={1}>{ev.title}</Text>
          </View>
        </View>
      ))}
    </View>
    <Text style={styles.eventFooterNote}>Confirm dates with your school calendar</Text>
  </View>
);

const TeacherQuoteWidget: React.FC = () => {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx((i) => (i + 1) % QUOTES.length), 10000);
    return () => clearInterval(t);
  }, []);
  const q = QUOTES[idx];
  return (
    <View style={styles.widgetCard}>
      <Text style={styles.widgetTitle}>Teacher's Corner</Text>
      <View style={styles.quoteBlock}>
        <Text style={styles.quoteText}>&ldquo;{q.text}&rdquo;</Text>
        <Text style={styles.quoteAuthor}>— {q.author}</Text>
      </View>
    </View>
  );
};

const UsefulLinksWidget: React.FC = () => (
  <View style={styles.widgetCard}>
    <Text style={styles.widgetTitle}>Useful Links</Text>
    {USEFUL_LINKS.map((l, i) => (
      <React.Fragment key={l.label}>
        {i > 0 && <View style={styles.linkDivider} />}
        <Pressable onPress={() => Linking.openURL(l.url)} style={styles.usefulLink}>
          <View style={styles.linkDot} />
          <Text style={styles.usefulLinkText}>{l.label}</Text>
        </Pressable>
      </React.Fragment>
    ))}
  </View>
);

const TipOfDayWidget: React.FC = () => {
  const tip = TIPS[new Date().getDay()];
  return (
    <View style={styles.widgetCard}>
      <View style={{ flexDirection: 'row', alignItems: 'center', marginBottom: 6 }}>
        <Ionicons name="bulb" size={14} color="#F59E0B" style={{ marginRight: 5 }} />
        <Text style={styles.widgetTitle}>Lesson Planning Tip</Text>
      </View>
      <Text style={styles.widgetFact}>{tip}</Text>
    </View>
  );
};

const TermCalendarWidget: React.FC = () => (
  <View style={[styles.widgetCard, { padding: 0, overflow: 'hidden' }]}>
    <View style={styles.termHeader}>
      <Text style={styles.widgetTitle}>2025 Term Calendar</Text>
      <Text style={styles.widgetSubtitle}>Academic & co-curricular activities</Text>
    </View>
    {TERM_CALENDAR.map((term, idx) => (
      <View key={term.name}>
        <View style={[styles.termSectionHeader, { backgroundColor: term.headerBg }]}>
          <View>
            <Text style={[styles.termSectionName, { color: term.headerText }]}>{term.name}</Text>
            <Text style={styles.termSectionPeriod}>{term.period}</Text>
          </View>
          <View style={[styles.termBadge, { backgroundColor: term.headerBg, borderColor: term.badgeBorder }]}>
            <Text style={[styles.termBadgeText, { color: term.headerText }]}>{term.status}</Text>
          </View>
        </View>
        <View style={styles.termActivitiesSection}>
          <Text style={[styles.activitiesLabel, { color: '#5B5BD6' }]}>📚 ACADEMIC</Text>
          {term.academic.map((a, i) => (
            <View key={i} style={styles.activityRow}>
              <View style={[styles.activityDot, { backgroundColor: '#5B5BD6' }]} />
              <Text style={styles.activityLabel}>{a.label}</Text>
              <Text style={styles.activityDate}>{a.date}</Text>
            </View>
          ))}
        </View>
        <View style={[styles.termActivitiesSection, { paddingBottom: 12 }]}>
          <Text style={[styles.activitiesLabel, { color: '#16A34A' }]}>🏆 CO-CURRICULAR</Text>
          {term.cocurricular.map((a, i) => (
            <View key={i} style={styles.activityRow}>
              <View style={[styles.activityDot, { backgroundColor: '#16A34A' }]} />
              <Text style={styles.activityLabel}>{a.label}</Text>
              <Text style={styles.activityDate}>{a.date}</Text>
            </View>
          ))}
        </View>
        {idx < TERM_CALENDAR.length - 1 && <View style={styles.termDivider} />}
      </View>
    ))}
  </View>
);

const SubjectsWidget: React.FC = () => (
  <View style={styles.widgetCard}>
    <Text style={styles.widgetTitle}>Subjects</Text>
    <View style={styles.subjectGrid}>
      {SUBJECTS.map((s) => (
        <View key={s} style={styles.subjectPill}>
          <Text style={styles.subjectPillText}>{s}</Text>
        </View>
      ))}
    </View>
  </View>
);

// ===== FEATURE TILES (clickable with auth check) =====
export const FeatureTiles: React.FC = () => {
  const { user } = useAuth();
  const router = useRouter();
  const { width } = useWindowDimensions();
  const twoCols = width >= 400;

  const handlePress = (route: string) => {
    if (user) {
      router.push(route as any);
    } else {
      if (typeof window !== 'undefined' && window.alert) {
        window.alert('Please sign in to access this feature. Your session may have expired.');
      }
      // Stay on login — user will sign in and then can navigate
    }
  };

  return (
    <View style={styles.featureContainer}>
      <Text style={styles.featureHeading}>WHAT YOU CAN DO WITH CBE PLANNER</Text>
      <View style={[styles.featureGrid, !twoCols && { flexDirection: 'column' }]}>
        {FEATURE_TILES.map((f) => (
          <Pressable
            key={f.label}
            onPress={() => handlePress(f.route)}
            style={({ pressed }) => [
              styles.featureBtn,
              {
                backgroundColor: f.bg,
                borderColor: f.border,
                width: twoCols ? '48.5%' : '100%',
                opacity: pressed ? 0.85 : 1,
              },
            ]}
          >
            <Ionicons name={f.icon as any} size={18} color={f.color} style={{ marginRight: 8 }} />
            <Text style={[styles.featureBtnLabel, { color: f.color }]} numberOfLines={2}>
              {f.label}
            </Text>
          </Pressable>
        ))}
      </View>
      <Text style={styles.featureFooter}>✓ Free to get started · No credit card required</Text>
    </View>
  );
};

// ===== MAIN LAYOUT =====
interface Props {
  children: React.ReactNode;
}

export const LandingLayout: React.FC<Props> = ({ children }) => {
  const { width } = useWindowDimensions();
  const isDesktop = width >= BP_DESKTOP;
  const isTablet = width >= BP_TABLET && width < BP_DESKTOP;
  const isMobile = width < BP_TABLET;

  return (
    <ScrollView style={styles.page} contentContainerStyle={styles.pageContent}>
      <View
        style={[
          styles.grid,
          isDesktop && styles.gridDesktop,
          isTablet && styles.gridTablet,
          isMobile && styles.gridMobile,
        ]}
      >
        {isDesktop && (
          <View style={styles.sidebarLeft}>
            <View style={{ gap: 14 }}>
              <DidYouKnowWidget />
              <CalendarWidget />
              <UpcomingEventsWidget />
              <TeacherQuoteWidget />
            </View>
          </View>
        )}

        <View style={[styles.centerCol, isMobile && styles.centerColMobile]}>
          {children}

          {/* Ad directly below the auth card */}
          <View style={{ marginTop: 20, alignItems: 'center' }}>
            <AdSlot width={300} height={250} />
          </View>
        </View>

        {!isMobile && (
          <View style={styles.sidebarRight}>
            <View style={{ gap: 14 }}>
              <UsefulLinksWidget />
              <TipOfDayWidget />
              <TermCalendarWidget />
              <SubjectsWidget />
              <AdSlot width={300} height={250} />
            </View>
          </View>
        )}
      </View>

      {/* Bottom ad banner */}
      <View style={styles.bottomAdSection}>
        <View style={{ alignItems: 'center' }}>
          {isDesktop && <AdSlot width={728} height={90} />}
          {isTablet && <AdSlot width={468} height={60} />}
          {isMobile && <AdSlot width={320} height={50} />}
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  page: { flex: 1, backgroundColor: '#F3F4F6' },
  pageContent: { flexGrow: 1 },
  grid: {
    flexDirection: 'row',
    alignItems: 'flex-start',
    width: '100%',
    maxWidth: 1800,
    alignSelf: 'center',
    paddingHorizontal: 24,
    paddingVertical: 24,
    gap: 28,
  },
  gridDesktop: {},
  gridTablet: { gap: 16, paddingHorizontal: 16 },
  gridMobile: {
    flexDirection: 'column',
    paddingHorizontal: 0,
    paddingVertical: 0,
    gap: 0,
  },
  sidebarLeft: { width: 280, flexShrink: 0 },
  sidebarRight: { width: 280, flexShrink: 0 },
  centerCol: {
    flex: 1,
    maxWidth: 640,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    padding: 36,
    alignSelf: 'stretch',
  },
  centerColMobile: {
    borderRadius: 0,
    borderLeftWidth: 0,
    borderRightWidth: 0,
    padding: 20,
    width: '100%',
    maxWidth: undefined,
    minHeight: '100%',
  },

  // Widget card
  widgetCard: {
    backgroundColor: '#FFFFFF',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 12,
    padding: 14,
  },
  widgetTitle: { fontSize: 13, fontWeight: '600', color: '#111827', marginBottom: 8 },
  widgetSubtitle: { fontSize: 10, color: '#9CA3AF', marginTop: 3 },
  widgetFact: { fontSize: 12, color: '#6B7280', lineHeight: 18 },
  widgetHeaderRow: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', marginBottom: 10 },

  // Dots
  dotRow: { flexDirection: 'row', gap: 5, marginTop: 10 },
  dot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#D1D5DB' },
  dotActive: { backgroundColor: '#5B5BD6' },

  // Legend
  legendRow: { flexDirection: 'row', alignItems: 'center' },
  legendDot: { width: 6, height: 6, borderRadius: 3 },
  legendText: { fontSize: 9, color: '#6B7280', marginLeft: 3 },

  // Events
  eventRow: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  eventDateBlock: {
    minWidth: 42,
    borderRadius: 7,
    paddingVertical: 4,
    paddingHorizontal: 3,
    alignItems: 'center',
  },
  eventDayName: { fontSize: 8, fontWeight: '600', letterSpacing: 0.3, textTransform: 'uppercase' },
  eventDateNum: { fontSize: 10, fontWeight: '500', marginTop: 2 },
  eventContent: { flexDirection: 'row', alignItems: 'center', gap: 7, flex: 1 },
  eventDot: { width: 5, height: 5, borderRadius: 3 },
  eventTitle: { fontSize: 11, color: '#374151', flex: 1 },
  eventFooterNote: { fontSize: 10, color: '#9CA3AF', textAlign: 'center', marginTop: 10 },

  // Quote
  quoteBlock: { paddingLeft: 10, borderLeftWidth: 3, borderLeftColor: '#5B5BD6', marginTop: 4 },
  quoteText: { fontSize: 12, color: '#374151', fontStyle: 'italic', lineHeight: 18 },
  quoteAuthor: { fontSize: 11, color: '#9CA3AF', marginTop: 6 },

  // Useful Links
  usefulLink: { flexDirection: 'row', alignItems: 'center', gap: 8, paddingVertical: 5 },
  usefulLinkText: { fontSize: 12, color: '#5B5BD6' },
  linkDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: '#5B5BD6' },
  linkDivider: { height: 1, backgroundColor: '#F3F4F6', marginVertical: 2 },

  // Subjects
  subjectGrid: { flexDirection: 'row', flexWrap: 'wrap', gap: 6, marginTop: 4 },
  subjectPill: { backgroundColor: '#F3F4F6', borderRadius: 20, paddingHorizontal: 10, paddingVertical: 4 },
  subjectPillText: { fontSize: 11, color: '#374151' },

  // Term calendar
  termHeader: { padding: 14, borderBottomWidth: 1, borderBottomColor: '#F3F4F6' },
  termSectionHeader: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between', paddingHorizontal: 14, paddingVertical: 9 },
  termSectionName: { fontSize: 12, fontWeight: '600' },
  termSectionPeriod: { fontSize: 10, color: '#9CA3AF', marginTop: 1 },
  termBadge: { paddingHorizontal: 8, paddingVertical: 3, borderRadius: 20, borderWidth: 1 },
  termBadgeText: { fontSize: 10, fontWeight: '500' },
  termActivitiesSection: { paddingHorizontal: 14, paddingTop: 8, paddingBottom: 4 },
  activitiesLabel: { fontSize: 10, fontWeight: '600', letterSpacing: 0.5, textTransform: 'uppercase', marginBottom: 5 },
  activityRow: { flexDirection: 'row', alignItems: 'center', gap: 7, paddingVertical: 2 },
  activityDot: { width: 5, height: 5, borderRadius: 3 },
  activityLabel: { flex: 1, fontSize: 11, color: '#374151' },
  activityDate: { fontSize: 10, color: '#9CA3AF' },
  termDivider: { height: 1, backgroundColor: '#F3F4F6' },

  // Ads
  adLabel: { fontSize: 10, color: '#9CA3AF', letterSpacing: 0.5, marginBottom: 4 },
  adBox: {
    backgroundColor: '#F9FAFB',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 10,
    alignItems: 'center',
    justifyContent: 'center',
  },
  adPlaceholderText: { color: '#D1D5DB', fontSize: 12 },

  bottomAdSection: { borderTopWidth: 1, borderTopColor: '#E5E7EB', paddingVertical: 40, paddingHorizontal: 16, backgroundColor: '#F3F4F6' },

  // Feature tiles
  featureContainer: { borderTopWidth: 1, borderTopColor: '#F3F4F6', marginTop: 24, paddingTop: 20 },
  featureHeading: { fontSize: 10, color: '#9CA3AF', letterSpacing: 0.8, textAlign: 'center', marginBottom: 14, fontWeight: '600' },
  featureGrid: { flexDirection: 'row', flexWrap: 'wrap', justifyContent: 'space-between', gap: 10 },
  featureBtn: {
    borderRadius: 10,
    borderWidth: 1,
    paddingVertical: 12,
    paddingHorizontal: 10,
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 0,
  },
  featureBtnLabel: { fontSize: 12, fontWeight: '500', flex: 1 },
  featureFooter: { fontSize: 12, color: '#6B7280', textAlign: 'center', marginTop: 14 },
});

export default LandingLayout;
