import React, { useEffect, useState } from 'react';
import { View, Text, StyleSheet, Pressable, Linking } from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { usePathname } from 'expo-router';
import { CalendarWidgetCompact } from './LandingLayout';

/**
 * Compact widgets designed for 180px-wide persistent sidebars across
 * post-login teacher pages. Kept deliberately slim so they complement
 * the central 950px app column without competing for attention.
 */

// ===== LEFT SIDEBAR =====

export const MPesaTillCard: React.FC = () => (
  <View style={styles.card} data-testid="app-mpesa-till-card">
    <View style={styles.mpesaAccentBar} />
    <View style={{ paddingLeft: 6 }}>
      <View style={styles.mpesaHeader}>
        <Ionicons name="card-outline" size={12} color="#16a34a" />
        <Text style={styles.mpesaHeaderTxt}>MPesa Payment</Text>
      </View>
      <Text style={styles.mpesaMsg}>
        STK push didn't arrive? Pay via <Text style={styles.bold}>Buy Goods</Text>:
      </Text>
      <View style={styles.tillBox}>
        <Text style={styles.tillLbl}>Till Number</Text>
        <Text style={styles.tillNum}>8336258</Text>
      </View>
      {[
        'Open MPesa',
        'Lipa na MPesa',
        'Buy Goods',
        'Till 8336258',
        'Amount + PIN',
      ].map((s, i) => (
        <View key={i} style={styles.stepRow}>
          <View style={styles.stepBullet}><Text style={styles.stepNum}>{i + 1}</Text></View>
          <Text style={styles.stepTxt}>{s}</Text>
        </View>
      ))}
      <View style={styles.divider} />
      <Text style={styles.supportTxt}>
        Need help?{' '}
        <Text
          style={styles.supportLink}
          onPress={() => Linking.openURL('mailto:legitlab@outlook.com')}
        >
          legitlab@outlook.com
        </Text>
      </Text>
    </View>
  </View>
);

const TIPS = [
  'Align your scheme with KICD guidelines.',
  'Start lessons with a warm-up.',
  'Use differentiated tasks for all abilities.',
  'Add formative checks every 15 minutes.',
  'Use real Kenyan examples.',
  'Review objectives weekly.',
  'Prep visual aids in advance.',
];

const TipCard: React.FC = () => {
  const tip = TIPS[new Date().getDay()];
  return (
    <View style={styles.card} data-testid="app-tip-card">
      <View style={styles.cardHeader}>
        <Ionicons name="bulb" size={12} color="#F59E0B" />
        <Text style={styles.cardTitle}>Today's Tip</Text>
      </View>
      <Text style={styles.cardBody}>{tip}</Text>
    </View>
  );
};

export const AppLeftSidebar: React.FC = () => {
  const pathname = usePathname() || '';
  // Show the MPesa till card ONLY on the scheme generation page
  const isSchemesPage = pathname === '/schemes' || pathname.endsWith('/(teacher)/schemes');
  return (
    <View style={{ gap: 12 }}>
      <CalendarWidgetCompact />
      {isSchemesPage && <MPesaTillCard />}
      <TipCard />
    </View>
  );
};

// ===== RIGHT SIDEBAR =====

const QUOTES = [
  { t: 'Education is not the filling of a pail, but the lighting of a fire.', a: 'W.B. Yeats' },
  { t: 'The art of teaching is the art of assisting discovery.', a: 'Mark Van Doren' },
  { t: 'A good teacher can inspire hope and ignite the imagination.', a: 'Brad Henry' },
];

const QuoteCard: React.FC = () => {
  const [idx, setIdx] = useState(0);
  useEffect(() => {
    const t = setInterval(() => setIdx((i) => (i + 1) % QUOTES.length), 10000);
    return () => clearInterval(t);
  }, []);
  const q = QUOTES[idx];
  return (
    <View style={styles.card} data-testid="app-quote-card">
      <View style={styles.cardHeader}>
        <Ionicons name="chatbox-ellipses-outline" size={12} color="#5B5BD6" />
        <Text style={styles.cardTitle}>Teacher's Corner</Text>
      </View>
      <View style={styles.quoteBlock}>
        <Text style={styles.quoteTxt}>&ldquo;{q.t}&rdquo;</Text>
        <Text style={styles.quoteAuthor}>— {q.a}</Text>
      </View>
    </View>
  );
};

const LINKS = [
  { label: 'Ministry of Education', url: 'https://education.go.ke' },
  { label: 'KNEC Portal', url: 'https://www.knec.ac.ke' },
  { label: 'CBC Portal', url: 'https://cbcportal.ac.ke' },
  { label: 'KICD Resources', url: 'https://kicd.ac.ke' },
  { label: 'TSC Online', url: 'https://www.tsc.go.ke' },
];

const LinksCard: React.FC = () => (
  <View style={styles.card} data-testid="app-links-card">
    <View style={styles.cardHeader}>
      <Ionicons name="link-outline" size={12} color="#5B5BD6" />
      <Text style={styles.cardTitle}>Useful Links</Text>
    </View>
    {LINKS.map((l, i) => (
      <React.Fragment key={l.label}>
        {i > 0 && <View style={styles.linkSep} />}
        <Pressable onPress={() => Linking.openURL(l.url)} style={styles.linkRow}>
          <View style={styles.linkDot} />
          <Text style={styles.linkTxt}>{l.label}</Text>
        </Pressable>
      </React.Fragment>
    ))}
  </View>
);

const SupportCard: React.FC = () => (
  <View style={[styles.card, styles.supportCard]} data-testid="app-support-card">
    <View style={styles.cardHeader}>
      <Ionicons name="mail-outline" size={12} color="#166534" />
      <Text style={[styles.cardTitle, { color: '#166534' }]}>Support</Text>
    </View>
    <Text style={styles.supportBody}>
      Questions or feedback?{'\n'}Reach us anytime.
    </Text>
    <Pressable
      onPress={() => Linking.openURL('mailto:legitlab@outlook.com')}
      style={styles.supportBtn}
    >
      <Ionicons name="send-outline" size={10} color="#FFFFFF" />
      <Text style={styles.supportBtnTxt}>Email Us</Text>
    </Pressable>
  </View>
);

export const AppRightSidebar: React.FC = () => (
  <View style={{ gap: 12 }}>
    <QuoteCard />
    <LinksCard />
    <SupportCard />
  </View>
);

// ===== STYLES =====

const styles = StyleSheet.create({
  card: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    padding: 10,
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 1 },
    shadowOpacity: 0.03,
    shadowRadius: 2,
  },
  cardHeader: { flexDirection: 'row', alignItems: 'center', gap: 5, marginBottom: 6 },
  cardTitle: { fontSize: 11, fontWeight: '700', color: '#111827', letterSpacing: 0.2 },
  cardBody: { fontSize: 10, color: '#6B7280', lineHeight: 14 },

  bold: { fontWeight: '700' },

  // MPesa card
  mpesaAccentBar: {
    position: 'absolute',
    left: -10,
    top: -10,
    bottom: -10,
    width: 3,
    backgroundColor: '#16a34a',
    borderTopLeftRadius: 10,
    borderBottomLeftRadius: 10,
  },
  mpesaHeader: { flexDirection: 'row', alignItems: 'center', gap: 4, marginBottom: 4 },
  mpesaHeaderTxt: { fontSize: 11, fontWeight: '700', color: '#166534' },
  mpesaMsg: { fontSize: 9, color: '#166534', lineHeight: 13, marginBottom: 6 },
  tillBox: {
    backgroundColor: '#F0FDF4',
    borderWidth: 1,
    borderColor: '#86EFAC',
    borderRadius: 6,
    paddingVertical: 5,
    paddingHorizontal: 7,
    marginBottom: 6,
    alignItems: 'center',
  },
  tillLbl: { fontSize: 8, color: '#6B7280', letterSpacing: 0.3, textTransform: 'uppercase' },
  tillNum: { fontSize: 15, fontWeight: '800', color: '#166534', letterSpacing: 0.6 },
  stepRow: { flexDirection: 'row', alignItems: 'flex-start', gap: 5, marginBottom: 3 },
  stepBullet: {
    width: 12, height: 12, borderRadius: 6,
    backgroundColor: '#16a34a',
    alignItems: 'center', justifyContent: 'center', marginTop: 1,
  },
  stepNum: { fontSize: 7, color: '#FFF', fontWeight: '700', lineHeight: 8 },
  stepTxt: { fontSize: 9, color: '#166534', flex: 1, lineHeight: 12 },
  divider: { height: 1, backgroundColor: '#E5E7EB', marginVertical: 6 },
  supportTxt: { fontSize: 8, color: '#6B7280', lineHeight: 12 },
  supportLink: { color: '#16a34a', fontWeight: '500' },

  // Quote
  quoteBlock: { paddingLeft: 6, borderLeftWidth: 2, borderLeftColor: '#5B5BD6' },
  quoteTxt: { fontSize: 10, color: '#374151', fontStyle: 'italic', lineHeight: 14 },
  quoteAuthor: { fontSize: 9, color: '#9CA3AF', marginTop: 4 },

  // Links
  linkRow: { flexDirection: 'row', alignItems: 'center', gap: 6, paddingVertical: 3 },
  linkDot: { width: 4, height: 4, borderRadius: 2, backgroundColor: '#5B5BD6' },
  linkTxt: { fontSize: 10, color: '#5B5BD6' },
  linkSep: { height: 1, backgroundColor: '#F3F4F6' },

  // Support
  supportCard: { backgroundColor: '#F0FDF4', borderColor: '#BBF7D0' },
  supportBody: { fontSize: 10, color: '#166534', lineHeight: 14, marginBottom: 8 },
  supportBtn: {
    backgroundColor: '#16a34a',
    borderRadius: 6,
    paddingVertical: 6,
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 4,
  },
  supportBtnTxt: { color: '#FFFFFF', fontSize: 10, fontWeight: '600' },
});
