import React, { useCallback, useEffect, useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  useWindowDimensions,
  Linking,
  Pressable,
  Image,
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';
import { useFocusEffect } from '@react-navigation/native';
import axios from 'axios';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;

const CLASSROOM_IMG = require('../../assets/images/classroom.webp');
const NOTEBOOK_IMG = require('../../assets/images/notebook.webp');

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

const ONBOARDING_STEPS = [
  {
    n: 1,
    title: 'Pick Grade & Subject',
    body: 'Choose the class you\u2019re planning for and the learning area you\u2019ll cover.',
    icon: 'school-outline' as const,
  },
  {
    n: 2,
    title: 'Select Topics & Breaks',
    body: 'Tick the sub-strands you\u2019ll teach and add any term breaks or CATs.',
    icon: 'list-outline' as const,
  },
  {
    n: 3,
    title: 'Preview & Download',
    body: 'Preview the scheme for free, then export the KICD-aligned PDF.',
    icon: 'cloud-download-outline' as const,
  },
];

interface RecentScheme {
  id: string;
  gradeName?: string;
  subjectName?: string;
  term?: number;
  year?: number;
  createdAt?: string;
}

interface RecentLesson {
  id: string;
  gradeName?: string;
  subjectName?: string;
  substrandName?: string;
  createdAt?: string;
}

export default function Dashboard() {
  const router = useRouter();
  const { user, refreshProfile, firebaseUser } = useAuth();
  const { width } = useWindowDimensions();
  const isMobile = width < MOBILE_BREAKPOINT;
  const isNarrow = width < NARROW_BREAKPOINT;

  const [recentSchemes, setRecentSchemes] = useState<RecentScheme[]>([]);
  const [recentLessons, setRecentLessons] = useState<RecentLesson[]>([]);
  const [loadingRecent, setLoadingRecent] = useState(true);

  const loadRecent = useCallback(async () => {
    if (!firebaseUser) return;
    try {
      const token = await firebaseUser.getIdToken();
      const headers = { Authorization: `Bearer ${token}` };
      const [sRes, lRes] = await Promise.all([
        axios.get(`${BACKEND_URL}/api/schemes`, { headers }).catch(() => null),
        axios.get(`${BACKEND_URL}/api/lesson-plans`, { headers }).catch(() => null),
      ]);
      const schemes: RecentScheme[] = sRes?.data?.schemes || sRes?.data?.data || [];
      const lessons: RecentLesson[] =
        lRes?.data?.lessonPlans || lRes?.data?.lesson_plans || lRes?.data?.data || [];
      const byDateDesc = (a: any, b: any) =>
        String(b?.createdAt || '').localeCompare(String(a?.createdAt || ''));
      setRecentSchemes([...schemes].sort(byDateDesc).slice(0, 3));
      setRecentLessons([...lessons].sort(byDateDesc).slice(0, 3));
    } catch {
      /* silently keep empty state */
    } finally {
      setLoadingRecent(false);
    }
  }, [firebaseUser]);

  useFocusEffect(
    useCallback(() => {
      refreshProfile();
      loadRecent();
    }, [loadRecent]),
  );

  const totalRecent = recentSchemes.length + recentLessons.length;
  const showOnboarding = !loadingRecent && totalRecent === 0;

  const formatDate = (iso?: string) => {
    if (!iso) return '';
    try {
      return new Date(iso).toLocaleDateString('en-GB', { day: '2-digit', month: 'short' });
    } catch {
      return '';
    }
  };

  // Pick a fresh quote each visit — no auto-rotation needed inline.
  const quote = QUOTES[Math.floor(Math.random() * QUOTES.length)];

  const go = (route: string) => () => router.push(route as any);

  // -------------------------------------------------------------------------
  // Welcome banner — hero row (headline + text + shortcuts) with editorial image
  // -------------------------------------------------------------------------
  const WelcomeBanner = (
    <View style={styles.welcomeCard} data-testid="dashboard-welcome-banner">
      <View style={[styles.heroRow, isNarrow && styles.heroRowStacked]}>
        <View style={styles.heroText}>
          <Text style={styles.heroEyebrow}>YOUR TEACHING WORKSPACE</Text>
          <Text style={styles.welcomeTitle}>
            Welcome back, {user?.firstName || 'Teacher'}!
          </Text>
          <Text style={styles.welcomeSub}>
            We&apos;ve assembled some shortcuts to get you started:
          </Text>
        </View>
        {!isNarrow && (
          <View style={styles.heroImageWrap} data-testid="dashboard-hero-image">
            <Image
              source={CLASSROOM_IMG}
              style={styles.heroImage}
              resizeMode="cover"
              accessibilityLabel="Classroom whiteboard with a diagram"
            />
            <View style={styles.heroImageOverlay} pointerEvents="none" />
            <View style={styles.heroImageBadge} pointerEvents="none">
              <Ionicons name="sparkles" size={12} color="#FFFFFF" />
              <Text style={styles.heroImageBadgeText}>KICD Aligned</Text>
            </View>
          </View>
        )}
      </View>

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
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={go('/(teacher)/home')}
            activeOpacity={0.85}
            data-testid="dashboard-cta-create-lesson"
          >
            <Text style={styles.primaryCtaText}>Create a Lesson Plan</Text>
          </TouchableOpacity>
        </View>

        {/* Next Steps — matching CTA buttons */}
        <View style={styles.actionCol}>
          <Text style={styles.actionColHeading}>Next Steps</Text>
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={go('/(teacher)/notes')}
            activeOpacity={0.85}
            data-testid="dashboard-cta-notes"
          >
            <Text style={styles.primaryCtaText}>Generate Lesson Notes</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={go('/(teacher)/revision')}
            activeOpacity={0.85}
            data-testid="dashboard-cta-revision"
          >
            <Text style={styles.primaryCtaText}>Download Revision Papers</Text>
          </TouchableOpacity>
        </View>

        {/* More Actions — matching CTA buttons */}
        <View style={styles.actionCol}>
          <Text style={styles.actionColHeading}>More Actions</Text>
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={go('/(teacher)/my-schemes')}
            activeOpacity={0.85}
            data-testid="dashboard-cta-my-schemes"
          >
            <Text style={styles.primaryCtaText}>Review My Schemes</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={go('/(teacher)/lessons')}
            activeOpacity={0.85}
            data-testid="dashboard-cta-my-lessons"
          >
            <Text style={styles.primaryCtaText}>My Lesson Plans</Text>
          </TouchableOpacity>
          <TouchableOpacity
            style={styles.primaryCta}
            onPress={go('/(teacher)/profile')}
            activeOpacity={0.85}
            data-testid="dashboard-cta-profile"
          >
            <Text style={styles.primaryCtaText}>Profile &amp; Support</Text>
          </TouchableOpacity>
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

        {showOnboarding && (
          <View style={styles.onboardingCard} data-testid="dashboard-onboarding-card">
            <View style={styles.onboardingHeader}>
              <View style={styles.onboardingHeaderLeft}>
                <View style={styles.onboardingIconWrap}>
                  <Ionicons name="rocket-outline" size={16} color="#FFFFFF" />
                </View>
                <View>
                  <Text style={styles.onboardingTitle}>
                    3 easy steps to your first Scheme of Work
                  </Text>
                  <Text style={styles.onboardingSub}>
                    Follow along &mdash; you&apos;ll have a KICD-aligned PDF in a few minutes.
                  </Text>
                </View>
              </View>
              <TouchableOpacity
                style={styles.onboardingCta}
                onPress={go('/(teacher)/schemes')}
                activeOpacity={0.85}
                data-testid="dashboard-onboarding-start-btn"
              >
                <Text style={styles.onboardingCtaText}>Start now</Text>
                <Ionicons name="arrow-forward" size={14} color="#FFFFFF" />
              </TouchableOpacity>
            </View>
            <View style={[styles.stepRow, isNarrow && styles.stepRowStacked]}>
              {ONBOARDING_STEPS.map((step, idx) => (
                <View key={step.n} style={styles.stepItem}>
                  <View style={styles.stepNumWrap}>
                    <View style={styles.stepNum}>
                      <Text style={styles.stepNumText}>{step.n}</Text>
                    </View>
                    {idx < ONBOARDING_STEPS.length - 1 && !isNarrow && (
                      <View style={styles.stepConnector} />
                    )}
                  </View>
                  <View style={styles.stepBody}>
                    <View style={styles.stepTitleRow}>
                      <Ionicons name={step.icon} size={14} color={COLORS.accent} />
                      <Text style={styles.stepTitle}>{step.title}</Text>
                    </View>
                    <Text style={styles.stepDesc}>{step.body}</Text>
                  </View>
                </View>
              ))}
            </View>
          </View>
        )}

        {(recentSchemes.length > 0 || recentLessons.length > 0) && (
          <View
            style={[styles.recentGrid, isNarrow && styles.recentGridStacked]}
            data-testid="dashboard-recent-activity"
          >
            <View style={styles.recentCol}>
              <View style={styles.recentHeader}>
                <View style={styles.recentHeaderLeft}>
                  <Ionicons name="albums-outline" size={16} color={COLORS.accent} />
                  <Text style={styles.recentTitle}>Recent Schemes</Text>
                </View>
                <Pressable
                  onPress={go('/(teacher)/my-schemes')}
                  data-testid="dashboard-recent-schemes-viewall"
                >
                  <Text style={styles.recentViewAll}>View all</Text>
                </Pressable>
              </View>
              {recentSchemes.length === 0 ? (
                <View style={styles.recentEmpty}>
                  <Image source={NOTEBOOK_IMG} style={styles.recentEmptyImg} resizeMode="cover" />
                  <Text style={styles.recentEmptyTitle}>No schemes yet</Text>
                  <Text style={styles.recentEmptyBody}>
                    Generate one in under 3 minutes.
                  </Text>
                </View>
              ) : (
                <View style={styles.recentList}>
                  {recentSchemes.map((s) => (
                    <Pressable
                      key={s.id}
                      style={styles.recentItem}
                      onPress={() =>
                        router.push(`/(teacher)/scheme-detail?id=${s.id}` as any)
                      }
                      data-testid={`dashboard-recent-scheme-${s.id}`}
                    >
                      <View style={styles.recentItemIcon}>
                        <Ionicons name="calendar" size={16} color={COLORS.accent} />
                      </View>
                      <View style={styles.recentItemText}>
                        <Text style={styles.recentItemTitle} numberOfLines={1}>
                          {s.subjectName || 'Scheme'}
                        </Text>
                        <Text style={styles.recentItemSub} numberOfLines={1}>
                          {[s.gradeName, s.term ? `Term ${s.term}` : null, s.year]
                            .filter(Boolean)
                            .join(' \u00b7 ')}
                        </Text>
                      </View>
                      <Text style={styles.recentItemDate}>{formatDate(s.createdAt)}</Text>
                      <Ionicons name="chevron-forward" size={14} color={COLORS.textSecondary} />
                    </Pressable>
                  ))}
                </View>
              )}
            </View>

            <View style={styles.recentCol}>
              <View style={styles.recentHeader}>
                <View style={styles.recentHeaderLeft}>
                  <Ionicons name="folder-open-outline" size={16} color={COLORS.accent} />
                  <Text style={styles.recentTitle}>Recent Lesson Plans</Text>
                </View>
                <Pressable
                  onPress={go('/(teacher)/lessons')}
                  data-testid="dashboard-recent-lessons-viewall"
                >
                  <Text style={styles.recentViewAll}>View all</Text>
                </Pressable>
              </View>
              {recentLessons.length === 0 ? (
                <View style={styles.recentEmpty}>
                  <Image source={NOTEBOOK_IMG} style={styles.recentEmptyImg} resizeMode="cover" />
                  <Text style={styles.recentEmptyTitle}>No lesson plans yet</Text>
                  <Text style={styles.recentEmptyBody}>
                    Create your first plan from a scheme.
                  </Text>
                </View>
              ) : (
                <View style={styles.recentList}>
                  {recentLessons.map((l) => (
                    <Pressable
                      key={l.id}
                      style={styles.recentItem}
                      onPress={() =>
                        router.push(`/(teacher)/lesson-detail?id=${l.id}` as any)
                      }
                      data-testid={`dashboard-recent-lesson-${l.id}`}
                    >
                      <View style={styles.recentItemIcon}>
                        <Ionicons name="book" size={16} color={COLORS.accent} />
                      </View>
                      <View style={styles.recentItemText}>
                        <Text style={styles.recentItemTitle} numberOfLines={1}>
                          {l.substrandName || l.subjectName || 'Lesson'}
                        </Text>
                        <Text style={styles.recentItemSub} numberOfLines={1}>
                          {[l.gradeName, l.subjectName].filter(Boolean).join(' \u00b7 ')}
                        </Text>
                      </View>
                      <Text style={styles.recentItemDate}>{formatDate(l.createdAt)}</Text>
                      <Ionicons name="chevron-forward" size={14} color={COLORS.textSecondary} />
                    </Pressable>
                  ))}
                </View>
              )}
            </View>
          </View>
        )}

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
    fontSize: 24,
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
    fontSize: 24,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 6,
  },
  welcomeSub: {
    fontSize: 15,
    color: COLORS.textSecondary,
    marginBottom: 20,
  },

  row3: { flexDirection: 'row', gap: 32 },
  row3Stacked: { flexDirection: 'column', gap: 20 },

  actionCol: { flex: 1, minWidth: 200 },
  actionColHeading: {
    fontSize: 16,
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
  primaryCtaText: { color: '#FFFFFF', fontSize: 15, fontWeight: '600' },
  actionColCaption: { fontSize: 13, color: COLORS.textSecondary, lineHeight: 19 },
  inlineLink: { color: COLORS.link, textDecorationLine: 'underline' },

  linkRow: {
    flexDirection: 'row',
    alignItems: 'center',
    paddingVertical: 6,
    gap: 8,
  },
  linkText: { fontSize: 14, color: COLORS.link },

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
  widgetTitle: { fontSize: 14, fontWeight: '700', color: COLORS.textPrimary },
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
  usefulLinkText: { flex: 1, fontSize: 14, color: COLORS.textPrimary },
  itemSep: { height: 1, backgroundColor: '#F3F4F6' },

  // Quote
  quoteText: {
    fontSize: 15,
    fontStyle: 'italic',
    color: COLORS.textPrimary,
    lineHeight: 22,
  },
  quoteAuthor: {
    fontSize: 13,
    color: COLORS.textSecondary,
    marginTop: 8,
    textAlign: 'right',
  },

  // Tip & support
  tipText: { fontSize: 14, color: COLORS.warningText, lineHeight: 20 },
  supportText: { fontSize: 14, color: COLORS.success, lineHeight: 20, marginBottom: 12 },
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
  supportBtnText: { color: '#FFFFFF', fontSize: 13, fontWeight: '700' },

  // ── Hero row (welcome banner) ────────────────────────────────────
  heroRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 24,
    marginBottom: 20,
  },
  heroRowStacked: { flexDirection: 'column', alignItems: 'stretch', gap: 12 },
  heroText: { flex: 1 },
  heroEyebrow: {
    fontSize: 11,
    fontWeight: '700',
    color: COLORS.accent,
    letterSpacing: 1.4,
    marginBottom: 6,
  },
  heroImageWrap: {
    width: 300,
    height: 172,
    borderRadius: 10,
    overflow: 'hidden',
    position: 'relative',
    // @ts-ignore web-only shadow
    boxShadow: '0 10px 30px rgba(40,53,147,0.18)',
    borderWidth: 1,
    borderColor: COLORS.accentBorder,
  },
  heroImage: { width: '100%', height: '100%' },
  heroImageOverlay: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    // @ts-ignore web-only gradient overlay
    backgroundImage:
      'linear-gradient(160deg, rgba(40,53,147,0.55) 0%, rgba(40,53,147,0.05) 45%, rgba(255,255,255,0) 100%)',
  },
  heroImageBadge: {
    position: 'absolute',
    top: 12,
    left: 12,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 4,
    backgroundColor: 'rgba(40,53,147,0.85)',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 999,
  },
  heroImageBadgeText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '700',
    letterSpacing: 0.3,
  },

  // ── Onboarding checklist card ────────────────────────────────────
  onboardingCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 10,
    padding: 22,
    marginBottom: 20,
    borderWidth: 1,
    borderColor: COLORS.accentBorder,
    // @ts-ignore web-only
    backgroundImage:
      'linear-gradient(135deg, #FFFFFF 0%, #F5F6FF 65%, #EEF2FF 100%)',
  },
  onboardingHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    marginBottom: 18,
    gap: 12,
    flexWrap: 'wrap',
  },
  onboardingHeaderLeft: { flexDirection: 'row', alignItems: 'center', gap: 12, flex: 1, minWidth: 240 },
  onboardingIconWrap: {
    width: 32,
    height: 32,
    borderRadius: 8,
    backgroundColor: COLORS.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  onboardingTitle: {
    fontSize: 16,
    fontWeight: '700',
    color: COLORS.textPrimary,
    marginBottom: 2,
  },
  onboardingSub: { fontSize: 13, color: COLORS.textSecondary },
  onboardingCta: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    backgroundColor: COLORS.accent,
    paddingHorizontal: 14,
    paddingVertical: 8,
    borderRadius: 6,
  },
  onboardingCtaText: { color: '#FFFFFF', fontSize: 13, fontWeight: '600' },

  stepRow: { flexDirection: 'row', gap: 24 },
  stepRowStacked: { flexDirection: 'column', gap: 14 },
  stepItem: { flex: 1, flexDirection: 'row', gap: 12, alignItems: 'flex-start' },
  stepNumWrap: { alignItems: 'center' },
  stepNum: {
    width: 28,
    height: 28,
    borderRadius: 14,
    backgroundColor: COLORS.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepNumText: { color: '#FFFFFF', fontSize: 13, fontWeight: '700' },
  stepConnector: {
    position: 'absolute',
    top: 14,
    left: 34,
    width: 999,
    height: 1,
    backgroundColor: COLORS.accentBorder,
  },
  stepBody: { flex: 1 },
  stepTitleRow: { flexDirection: 'row', alignItems: 'center', gap: 6, marginBottom: 4 },
  stepTitle: { fontSize: 14, fontWeight: '700', color: COLORS.textPrimary },
  stepDesc: { fontSize: 13, color: COLORS.textSecondary, lineHeight: 19 },

  // ── Recent Activity grid ────────────────────────────────────────
  recentGrid: { flexDirection: 'row', gap: 20, marginBottom: 20 },
  recentGridStacked: { flexDirection: 'column' },
  recentCol: {
    flex: 1,
    backgroundColor: COLORS.card,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.cardBorder,
    overflow: 'hidden',
  },
  recentHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: COLORS.cardBorder,
    backgroundColor: '#FAFAFF',
  },
  recentHeaderLeft: { flexDirection: 'row', alignItems: 'center', gap: 8 },
  recentTitle: { fontSize: 14, fontWeight: '700', color: COLORS.textPrimary },
  recentViewAll: { fontSize: 12, fontWeight: '600', color: COLORS.accent },
  recentList: { paddingVertical: 6 },
  recentItem: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    paddingHorizontal: 16,
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6',
  },
  recentItemIcon: {
    width: 34,
    height: 34,
    borderRadius: 8,
    backgroundColor: COLORS.accentSoft,
    alignItems: 'center',
    justifyContent: 'center',
  },
  recentItemText: { flex: 1 },
  recentItemTitle: { fontSize: 14, fontWeight: '600', color: COLORS.textPrimary },
  recentItemSub: { fontSize: 12, color: COLORS.textSecondary, marginTop: 2 },
  recentItemDate: { fontSize: 11, color: COLORS.textSecondary, fontWeight: '600' },

  recentEmpty: {
    alignItems: 'center',
    paddingVertical: 22,
    paddingHorizontal: 20,
    gap: 8,
  },
  recentEmptyImg: {
    width: '100%',
    height: 120,
    borderRadius: 8,
    marginBottom: 4,
    opacity: 0.9,
  },
  recentEmptyTitle: { fontSize: 14, fontWeight: '700', color: COLORS.textPrimary },
  recentEmptyBody: { fontSize: 12, color: COLORS.textSecondary, textAlign: 'center' },
});
