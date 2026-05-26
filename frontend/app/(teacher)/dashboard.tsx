import React, { useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  useWindowDimensions,
  Linking,
  Pressable,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';

// ---------------------------------------------------------------------------
// Dashboard layout (WordPress-style)
// ---------------------------------------------------------------------------
//
// Reference: the WordPress admin dashboard the user shared on 2026-05-26.
// Single full-width "Welcome" banner at the top with three quick-action
// columns (Get Started / Next Steps / More Actions), then a 2-column grid
// of widget cards below. The wallet balance and free-lessons counters are
// intentionally NOT shown here — they belong on the Profile page.

const MOBILE_BREAKPOINT = 768;
const NARROW_BREAKPOINT = 1024;

const COLORS = {
  bg: '#F3F4F6',
  card: '#FFFFFF',
  cardBorder: '#E5E7EB',
  textPrimary: '#111827',
  textSecondary: '#6B7280',
  accent: '#5C6BC0',
  accentSoft: '#EEF2FF',
  accentBorder: '#C7D2FE',
  warning: '#E65100',
  warningSoft: '#FFF7ED',
  warningBorder: '#FED7AA',
  warningText: '#7C2D12',
  link: '#2563EB',
  success: '#166534',
  successSoft: '#DCFCE7',
  successBorder: '#BBF7D0',
};

const USEFUL_LINKS = [
  { label: 'Ministry of Education', url: 'https://education.go.ke' },
  { label: 'KNEC Portal', url: 'https://www.knec.ac.ke' },
  { label: 'CBC Portal', url: 'https://cbcportal.ac.ke' },
  { label: 'KICD Resources', url: 'https://kicd.ac.ke' },
  { label: 'TSC Online', url: 'https://www.tsc.go.ke' },
];

const QUOTES = [
  { t: 'Education is not the filling of a pail, but the lighting of a fire.', a: 'W.B. Yeats' },
  { t: 'The art of teaching is the art of assisting discovery.', a: 'Mark Van Doren' },
  { t: 'A good teacher can inspire hope and ignite the imagination.', a: 'Brad Henry' },
];

export default function Dashboard() {
  const router = useRouter();
  const { user, refreshProfile } = useAuth();
  const { width } = useWindowDimensions();
  const isMobile = width < MOBILE_BREAKPOINT;
  const isNarrow = width < NARROW_BREAKPOINT;

  useFocusEffect(
    useCallback(() => {
      refreshProfile();
    }, []),
  );

  // Pick a fresh quote each visit — no auto-rotation needed inline.
  const quote = QUOTES[Math.floor(Math.random() * QUOTES.length)];

  const go = (route: string) => () => router.push(route as any);

  // -------------------------------------------------------------------------
  // Welcome banner — Get Started / Next Steps / More Actions
  // -------------------------------------------------------------------------
  const WelcomeBanner = (
    <View style={styles.welcomeCard} data-testid="dashboard-welcome-banner">
      <Text style={styles.welcomeTitle}>
        Welcome back, {user?.firstName || 'Teacher'}!
      </Text>
      <Text style={styles.welcomeSub}>
        We&apos;ve assembled some shortcuts to get you started:
      </Text>

      <View style={[styles.row3, isNarrow && styles.row3Stacked]}>
        {/* Get Started — large indigo CTA */}
        <View style={styles.actionCol}>
          <Text style={styles.actionColHeading}>Get Started</Text>
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={go('/(teacher)/schemes')}
            activeOpacity={0.85}
            data-testid="dashboard-cta-schemes"
          >
            <Text style={styles.primaryCtaText}>Generate Scheme of Work</Text>
          </TouchableOpacity>
          <Text style={styles.actionColCaption}>
            …or{' '}
            <Text
              style={styles.inlineLink}
              onPress={go('/(teacher)/home')}
            >
              create a lesson plan
            </Text>{' '}
            instead.
          </Text>
        </View>

        {/* Next Steps — link list */}
        <View style={styles.actionCol}>
          <Text style={styles.actionColHeading}>Next Steps</Text>
          <Pressable style={styles.linkRow} onPress={go('/(teacher)/home')}>
            <Ionicons name="document-text-outline" size={14} color={COLORS.link} />
            <Text style={styles.linkText}>Create a lesson plan</Text>
          </Pressable>
          <Pressable style={styles.linkRow} onPress={go('/(teacher)/notes')}>
            <Ionicons name="create-outline" size={14} color={COLORS.link} />
            <Text style={styles.linkText}>Generate lesson notes</Text>
          </Pressable>
          <Pressable style={styles.linkRow} onPress={go('/(teacher)/revision')}>
            <Ionicons name="school-outline" size={14} color={COLORS.link} />
            <Text style={styles.linkText}>Download revision papers</Text>
          </Pressable>
        </View>

        {/* More Actions — secondary nav */}
        <View style={styles.actionCol}>
          <Text style={styles.actionColHeading}>More Actions</Text>
          <Pressable style={styles.linkRow} onPress={go('/(teacher)/my-schemes')}>
            <Ionicons name="albums-outline" size={14} color={COLORS.link} />
            <Text style={styles.linkText}>Review my schemes</Text>
          </Pressable>
          <Pressable style={styles.linkRow} onPress={go('/(teacher)/lessons')}>
            <Ionicons name="folder-open-outline" size={14} color={COLORS.link} />
            <Text style={styles.linkText}>My lesson plans</Text>
          </Pressable>
          <Pressable style={styles.linkRow} onPress={go('/(teacher)/profile')}>
            <Ionicons name="person-circle-outline" size={14} color={COLORS.link} />
            <Text style={styles.linkText}>Profile & support</Text>
          </Pressable>
        </View>
      </View>
    </View>
  );

  // -------------------------------------------------------------------------
  // Widget grid — At a Glance, Quick Draft (Useful Links + Teacher's Corner)
  // -------------------------------------------------------------------------
  const UsefulLinksCard = (
    <View style={styles.widgetCard} data-testid="dashboard-widget-useful-links">
      <View style={styles.widgetHeader}>
        <Ionicons name="link-outline" size={14} color={COLORS.accent} />
        <Text style={styles.widgetTitle}>Useful Links</Text>
      </View>
      <View style={styles.widgetBody}>
        {USEFUL_LINKS.map((l, i) => (
          <React.Fragment key={l.label}>
            {i > 0 && <View style={styles.itemSep} />}
            <Pressable
              onPress={() => Linking.openURL(l.url)}
              style={styles.usefulLinkRow}
            >
              <View style={styles.linkDot} />
              <Text style={styles.usefulLinkText}>{l.label}</Text>
              <Ionicons name="open-outline" size={12} color={COLORS.textSecondary} />
            </Pressable>
          </React.Fragment>
        ))}
      </View>
    </View>
  );

  const TeachersCornerCard = (
    <View style={styles.widgetCard} data-testid="dashboard-widget-quote">
      <View style={styles.widgetHeader}>
        <Ionicons
          name="chatbox-ellipses-outline"
          size={14}
          color={COLORS.accent}
        />
        <Text style={styles.widgetTitle}>Teacher&apos;s Corner</Text>
      </View>
      <View style={styles.widgetBody}>
        <Text style={styles.quoteText}>&ldquo;{quote.t}&rdquo;</Text>
        <Text style={styles.quoteAuthor}>— {quote.a}</Text>
      </View>
    </View>
  );

  const SupportCard = (
    <View
      style={[styles.widgetCard, styles.widgetCardSuccess]}
      data-testid="dashboard-widget-support"
    >
      <View style={styles.widgetHeader}>
        <Ionicons name="mail-outline" size={14} color={COLORS.success} />
        <Text style={[styles.widgetTitle, { color: COLORS.success }]}>
          Support
        </Text>
      </View>
      <View style={styles.widgetBody}>
        <Text style={styles.supportText}>
          Questions or feedback? Reach us anytime — we read every email.
        </Text>
        <Pressable
          onPress={() => Linking.openURL('mailto:legitlab@outlook.com')}
          style={styles.supportBtn}
          data-testid="dashboard-support-email-btn"
        >
          <Ionicons name="send-outline" size={11} color="#FFFFFF" />
          <Text style={styles.supportBtnText}>Email Us</Text>
        </Pressable>
      </View>
    </View>
  );

  const PlanningTipCard = (
    <View
      style={[styles.widgetCard, styles.widgetCardWarning]}
      data-testid="dashboard-widget-tip"
    >
      <View style={styles.widgetHeader}>
        <Ionicons name="bulb-outline" size={14} color={COLORS.warning} />
        <Text style={[styles.widgetTitle, { color: COLORS.warning }]}>
          Lesson Planning Tip
        </Text>
      </View>
      <View style={styles.widgetBody}>
        <Text style={styles.tipText}>
          Use differentiated tasks to cater for all learner abilities — start
          with a guided example, then a paired practice, and finish with an
          independent challenge.
        </Text>
      </View>
    </View>
  );

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView
        style={styles.scroll}
        contentContainerStyle={[
          styles.scrollContent,
          isMobile && styles.scrollContentMobile,
        ]}
        showsVerticalScrollIndicator={false}
      >
        <Text style={styles.pageTitle}>Dashboard</Text>

        {WelcomeBanner}

        <View style={[styles.widgetGrid, isNarrow && styles.widgetGridStacked]}>
          <View style={styles.widgetCol}>
            {UsefulLinksCard}
            {PlanningTipCard}
          </View>
          <View style={styles.widgetCol}>
            {TeachersCornerCard}
            {SupportCard}
          </View>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

// ---------------------------------------------------------------------------
// Styles
// ---------------------------------------------------------------------------

const styles = StyleSheet.create({
  container: { flex: 1, backgroundColor: COLORS.bg },
  scroll: { flex: 1 },
  scrollContent: {
    paddingHorizontal: 32,
    paddingVertical: 24,
    maxWidth: 1280,
    width: '100%',
    alignSelf: 'center',
  },
  scrollContentMobile: { paddingHorizontal: 16 },

  pageTitle: {
    fontSize: 22,
    fontWeight: '700',
    color: COLORS.textPrimary,
    marginBottom: 16,
  },

  // Welcome banner
  welcomeCard: {
    backgroundColor: COLORS.card,
    borderRadius: 8,
    padding: 24,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
    marginBottom: 20,
  },
  welcomeTitle: {
    fontSize: 22,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 6,
  },
  welcomeSub: {
    fontSize: 14,
    color: COLORS.textSecondary,
    marginBottom: 20,
  },

  row3: { flexDirection: 'row', gap: 32 },
  row3Stacked: { flexDirection: 'column', gap: 20 },

  actionCol: { flex: 1, minWidth: 200 },
  actionColHeading: {
    fontSize: 15,
    fontWeight: '700',
    color: COLORS.textPrimary,
    marginBottom: 12,
  },
  primaryCta: {
    backgroundColor: COLORS.accent,
    paddingVertical: 14,
    paddingHorizontal: 16,
    borderRadius: 4,
    alignItems: 'center',
    marginBottom: 10,
  },
  primaryCtaText: { color: '#FFFFFF', fontSize: 14, fontWeight: '600' },
  actionColCaption: { fontSize: 12, color: COLORS.textSecondary, lineHeight: 18 },
  inlineLink: { color: COLORS.link, textDecorationLine: 'underline' },

  linkRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    gap: 8,
  },
  linkText: { fontSize: 13, color: COLORS.link },

  // Widget grid
  widgetGrid: { flexDirection: 'row', gap: 20 },
  widgetGridStacked: { flexDirection: 'column' },
  widgetCol: { flex: 1, gap: 20 },

  widgetCard: {
    backgroundColor: COLORS.card,
    borderRadius: 6,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
    overflow: 'hidden',
  },
  widgetCardWarning: {
    backgroundColor: COLORS.warningSoft,
    borderColor: COLORS.warningBorder,
  },
  widgetCardSuccess: {
    backgroundColor: COLORS.successSoft,
    borderColor: COLORS.successBorder,
  },
  widgetHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 8,
    paddingHorizontal: 14,
    paddingVertical: 10,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.cardBorder,
  },
  widgetTitle: { fontSize: 13, fontWeight: '700', color: COLORS.textPrimary },
  widgetBody: { padding: 14 },

  // Useful links rows
  usefulLinkRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 8,
    gap: 10,
  },
  linkDot: {
    width: 6,
    height: 6,
    borderRadius: 3,
    backgroundColor: COLORS.accent,
  },
  usefulLinkText: { flex: 1, fontSize: 13, color: COLORS.textPrimary },
  itemSep: { height: 1, backgroundColor: '#F3F4F6' },

  // Quote
  quoteText: {
    fontSize: 14,
    fontStyle: 'italic',
    color: COLORS.textPrimary,
    lineHeight: 21,
  },
  quoteAuthor: {
    fontSize: 12,
    color: COLORS.textSecondary,
    marginTop: 8,
    textAlign: 'right',
  },

  // Tip & support
  tipText: { fontSize: 13, color: COLORS.warningText, lineHeight: 19 },
  supportText: { fontSize: 13, color: COLORS.success, lineHeight: 19, marginBottom: 12 },
  supportBtn: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: COLORS.success,
    paddingHorizontal: 12,
    paddingVertical: 8,
    borderRadius: 4,
    alignSelf: 'flex-start',
  },
  supportBtnText: { color: '#FFFFFF', fontSize: 12, fontWeight: '700' },
});
