/**
 * Public landing page (Phase 1 redesign).
 * Rendered for logged-out visitors at "/". Authenticated users are redirected
 * by AuthGate in _layout.tsx to their dashboard, so this file never displays
 * to them.
 *
 * Reuses:
 *  - existing /auth/login (Sign In)
 *  - existing /auth/signup (Get Started Free)
 *  - existing colour tokens from (teacher)/dashboard.tsx
 *  - existing hero asset (assets/images/classroom.webp)
 */
import React, { useState } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Image,
  useWindowDimensions,
  Platform,
} from 'react-native';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import { useAuth } from '../contexts/AuthContext';

const CLASSROOM_IMG = require('../assets/images/classroom.webp');
const NOTEBOOK_IMG = require('../assets/images/notebook.webp');

const MOBILE_BREAKPOINT = 768;
const NARROW_BREAKPOINT = 1024;

const COLORS = {
  bg: '#F7F8FC',
  surface: '#FFFFFF',
  border: '#E5E7EB',
  textPrimary: '#111827',
  textSecondary: '#4B5563',
  textMuted: '#6B7280',
  accent: '#5C6BC0',
  accentDark: '#3F4C9F',
  accentSoft: '#EEF2FF',
  accentBorder: '#C7D2FE',
  success: '#166534',
  successSoft: '#DCFCE7',
};

// Only actual, shipped features are listed here.
const FEATURES = [
  {
    icon: 'document-text-outline' as const,
    title: 'Lesson Plans',
    body: 'Create structured lesson plans aligned with the Kenyan curriculum.',
  },
  {
    icon: 'calendar-outline' as const,
    title: 'Schemes of Work',
    body: 'Organise your schemes of work and keep your teaching plan on track.',
  },
  {
    icon: 'book-outline' as const,
    title: 'Teaching Notes',
    body: 'Prepare structured teaching resources to support classroom instruction.',
  },
  {
    icon: 'clipboard-outline' as const,
    title: 'Revision & Assessment',
    body: 'Support learner revision and assessment with organised resources.',
  },
  {
    icon: 'today-outline' as const,
    title: 'Academic Calendar',
    body: 'Keep track of academic dates, activities and important education deadlines.',
  },
  {
    icon: 'folder-open-outline' as const,
    title: 'Personal Workspace',
    body: 'Save, manage and access your teaching resources in one place.',
  },
];

const TRUST_ITEMS = [
  'CBC & CBE Support',
  'KICD-Aligned Content',
  'Built for Kenyan Teachers',
];

// Nav links only include real routes/sections that exist on this page.
const NAV_LINKS: { label: string; anchor: 'features' | 'howitworks' | 'workspace' }[] = [
  { label: 'Features', anchor: 'features' },
  { label: 'How It Works', anchor: 'howitworks' },
  { label: 'Workspace', anchor: 'workspace' },
];

export default function Landing() {
  const router = useRouter();
  const { user } = useAuth();
  const { width } = useWindowDimensions();
  const isMobile = width < MOBILE_BREAKPOINT;
  const isNarrow = width < NARROW_BREAKPOINT;
  const [mobileMenuOpen, setMobileMenuOpen] = useState(false);

  const goSignup = () => router.push('/auth/signup' as any);
  const goLogin = () => router.push('/auth/login' as any);
  const goDashboard = () => router.push('/(teacher)/dashboard' as any);

  const scrollToId = (id: string) => {
    if (Platform.OS !== 'web') return;
    // @ts-ignore
    const el = document.getElementById(id);
    if (el) el.scrollIntoView({ behavior: 'smooth', block: 'start' });
    setMobileMenuOpen(false);
  };

  return (
    <ScrollView
      style={styles.scroll}
      contentContainerStyle={styles.scrollContent}
      showsVerticalScrollIndicator={false}
    >
      {/* ─────────────── Top Navigation ─────────────── */}
      <View style={[styles.nav, isMobile && styles.navMobile]} data-testid="landing-nav">
        <TouchableOpacity
          style={styles.brand}
          onPress={() => scrollToId('top')}
          activeOpacity={0.85}
          data-testid="landing-brand"
        >
          <View style={styles.brandMark}>
            <Ionicons name="school" size={18} color="#FFFFFF" />
          </View>
          <Text style={styles.brandName}>CBE Planner</Text>
        </TouchableOpacity>

        {!isMobile && (
          <View style={styles.navLinks}>
            {NAV_LINKS.map((l) => (
              <TouchableOpacity
                key={l.anchor}
                onPress={() => scrollToId(l.anchor)}
                data-testid={`landing-nav-${l.anchor}`}
              >
                <Text style={styles.navLink}>{l.label}</Text>
              </TouchableOpacity>
            ))}
          </View>
        )}

        <View style={styles.navActions}>
          {!isMobile && (
            <TouchableOpacity
              style={styles.navSignIn}
              onPress={user ? goDashboard : goLogin}
              activeOpacity={0.85}
              data-testid="landing-nav-signin"
            >
              <Text style={styles.navSignInText}>{user ? 'Open App' : 'Sign In'}</Text>
            </TouchableOpacity>
          )}
          <TouchableOpacity
            style={styles.navCta}
            onPress={user ? goDashboard : goSignup}
            activeOpacity={0.85}
            data-testid="landing-nav-getstarted"
          >
            <Text style={styles.navCtaText}>{user ? 'Go to Dashboard' : 'Get Started Free'}</Text>
          </TouchableOpacity>
          {isMobile && (
            <TouchableOpacity
              style={styles.hamburger}
              onPress={() => setMobileMenuOpen((v) => !v)}
              activeOpacity={0.85}
              accessibilityLabel="Toggle menu"
              data-testid="landing-mobile-menu-btn"
            >
              <Ionicons
                name={mobileMenuOpen ? 'close' : 'menu'}
                size={22}
                color={COLORS.textPrimary}
              />
            </TouchableOpacity>
          )}
        </View>
      </View>

      {/* Mobile menu dropdown */}
      {isMobile && mobileMenuOpen && (
        <View style={styles.mobileMenu} data-testid="landing-mobile-menu">
          {NAV_LINKS.map((l) => (
            <TouchableOpacity
              key={l.anchor}
              style={styles.mobileMenuItem}
              onPress={() => scrollToId(l.anchor)}
              data-testid={`landing-mobile-nav-${l.anchor}`}
            >
              <Text style={styles.mobileMenuText}>{l.label}</Text>
            </TouchableOpacity>
          ))}
          <TouchableOpacity
            style={styles.mobileMenuItem}
            onPress={() => {
              setMobileMenuOpen(false);
              (user ? goDashboard : goLogin)();
            }}
            data-testid="landing-mobile-signin"
          >
            <Text style={styles.mobileMenuText}>{user ? 'Open App' : 'Sign In'}</Text>
          </TouchableOpacity>
        </View>
      )}

      {/* ─────────────── Hero ─────────────── */}
      {/* @ts-ignore native RN ignores nativeID → data-testid on web is set by React Native Web */}
      <View
        style={[styles.hero, isNarrow && styles.heroNarrow]}
        // @ts-ignore
        nativeID="top"
        data-testid="landing-hero"
      >
        <View style={styles.heroText}>
          <View style={styles.heroEyebrowRow}>
            <View style={styles.heroEyebrowDot} />
            <Text style={styles.heroEyebrow}>KENYAN EDTECH · CBC & CBE</Text>
          </View>
          <Text style={[styles.heroHeadline, isMobile && styles.heroHeadlineMobile]}>
            Plan Better.{'\n'}Teach Smarter.
          </Text>
          <Text style={styles.heroLead}>
            Your digital lesson-planning companion for Kenyan teachers.
          </Text>
          <Text style={styles.heroBody}>
            Create curriculum-aligned lesson plans, schemes of work and teaching resources
            designed for the Kenyan classroom.
          </Text>

          <View style={[styles.heroCtaRow, isMobile && styles.heroCtaRowMobile]}>
            <TouchableOpacity
              style={styles.primaryCta}
              onPress={user ? goDashboard : goSignup}
              activeOpacity={0.9}
              data-testid="landing-hero-primary-cta"
            >
              <Text style={styles.primaryCtaText}>
                {user ? 'Go to Dashboard' : 'Get Started Free'}
              </Text>
              <Ionicons name="arrow-forward" size={16} color="#FFFFFF" />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.secondaryCta}
              onPress={() => scrollToId('features')}
              activeOpacity={0.9}
              data-testid="landing-hero-secondary-cta"
            >
              <Text style={styles.secondaryCtaText}>Explore Features</Text>
            </TouchableOpacity>
          </View>

          <Text style={styles.heroSubCta} data-testid="landing-free-note">
            Start with your first 5 lesson plans free · No credit card required.
          </Text>

          <View style={[styles.trustRow, isMobile && styles.trustRowMobile]}>
            {TRUST_ITEMS.map((t) => (
              <View key={t} style={styles.trustItem}>
                <Ionicons name="checkmark-circle" size={15} color={COLORS.accent} />
                <Text style={styles.trustText}>{t}</Text>
              </View>
            ))}
          </View>
        </View>

        {!isNarrow && (
          <View style={styles.heroVisual} data-testid="landing-hero-visual">
            <View style={styles.heroImageCard}>
              <Image source={CLASSROOM_IMG} style={styles.heroImage} resizeMode="cover" />
              <View style={styles.heroImageOverlay} pointerEvents="none" />
              <View style={styles.heroBadgeTL}>
                <Ionicons name="checkmark-circle" size={14} color="#FFFFFF" />
                <Text style={styles.heroBadgeText}>KICD-Aligned</Text>
              </View>
            </View>
            <View style={styles.heroStatCard}>
              <View style={styles.heroStatIconWrap}>
                <Ionicons name="stats-chart" size={16} color="#FFFFFF" />
              </View>
              <View style={styles.heroStatBody}>
                <Text style={styles.heroStatNum}>3 min</Text>
                <Text style={styles.heroStatLabel}>Average scheme build time</Text>
              </View>
            </View>
          </View>
        )}
      </View>

      {/* ─────────────── Feature Showcase ─────────────── */}
      <View
        style={styles.section}
        // @ts-ignore
        nativeID="features"
        data-testid="landing-features-section"
      >
        <Text style={styles.sectionEyebrow}>WHAT&apos;S INCLUDED</Text>
        <Text style={[styles.sectionHeadline, isMobile && styles.sectionHeadlineMobile]}>
          Everything You Need to Plan Better
        </Text>
        <Text style={styles.sectionLead}>
          Simple tools designed to help Kenyan teachers prepare, organise and deliver
          effective lessons.
        </Text>

        <View
          style={[
            styles.featureGrid,
            isNarrow && !isMobile && styles.featureGridTablet,
            isMobile && styles.featureGridMobile,
          ]}
        >
          {FEATURES.map((f) => (
            <View
              key={f.title}
              style={styles.featureCard}
              // @ts-ignore web-only hover already covered via subtle shadow
              data-testid={`landing-feature-${f.title.toLowerCase().replace(/[^a-z0-9]+/g, '-')}`}
            >
              <View style={styles.featureIconWrap}>
                <Ionicons name={f.icon} size={20} color={COLORS.accent} />
              </View>
              <Text style={styles.featureTitle}>{f.title}</Text>
              <Text style={styles.featureBody}>{f.body}</Text>
            </View>
          ))}
        </View>
      </View>

      {/* ─────────────── How It Works (anchor target) ─────────────── */}
      <View
        style={[styles.section, styles.sectionAlt]}
        // @ts-ignore
        nativeID="howitworks"
        data-testid="landing-howitworks-section"
      >
        <Text style={styles.sectionEyebrow}>HOW IT WORKS</Text>
        <Text style={[styles.sectionHeadline, isMobile && styles.sectionHeadlineMobile]}>
          A Scheme of Work in 3 Steps
        </Text>
        <View style={[styles.stepsRow, isMobile && styles.stepsRowMobile]}>
          <StepCard n={1} title="Pick Grade & Subject" body="Choose the class you're planning for and the learning area you'll cover." icon="school-outline" />
          <StepCard n={2} title="Select Topics & Breaks" body="Tick the sub-strands you'll teach and add any term breaks or CATs." icon="list-outline" />
          <StepCard n={3} title="Preview & Download" body="Preview the scheme for free, then export the KICD-aligned PDF." icon="cloud-download-outline" />
        </View>
      </View>

      {/* ─────────────── Workspace CTA strip (anchor target) ─────────────── */}
      <View
        style={[styles.workspaceStrip, isMobile && styles.workspaceStripMobile]}
        // @ts-ignore
        nativeID="workspace"
        data-testid="landing-workspace-cta"
      >
        <Image source={NOTEBOOK_IMG} style={styles.workspaceImg} resizeMode="cover" />
        <View style={styles.workspaceOverlay} pointerEvents="none" />
        <View style={styles.workspaceBody}>
          <Text style={styles.workspaceEyebrow}>YOUR WORKSPACE</Text>
          <Text style={styles.workspaceHeadline}>
            Ready to plan your next lesson?
          </Text>
          <Text style={styles.workspaceLead}>
            Join Kenyan teachers already using CBE Planner to prepare CBC-aligned lessons,
            schemes and notes in minutes.
          </Text>
          <View style={[styles.heroCtaRow, isMobile && styles.heroCtaRowMobile, styles.workspaceCtaRow]}>
            <TouchableOpacity
              style={styles.primaryCta}
              onPress={user ? goDashboard : goSignup}
              activeOpacity={0.9}
              data-testid="landing-workspace-primary-cta"
            >
              <Text style={styles.primaryCtaText}>
                {user ? 'Go to Dashboard' : 'Get Started Free'}
              </Text>
              <Ionicons name="arrow-forward" size={16} color="#FFFFFF" />
            </TouchableOpacity>
            <TouchableOpacity
              style={styles.secondaryCtaLight}
              onPress={user ? goDashboard : goLogin}
              activeOpacity={0.9}
              data-testid="landing-workspace-signin-cta"
            >
              <Text style={styles.secondaryCtaLightText}>{user ? 'Open App' : 'Sign In'}</Text>
            </TouchableOpacity>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}

// ─────────────── StepCard ───────────────
function StepCard({
  n, title, body, icon,
}: { n: number; title: string; body: string; icon: keyof typeof Ionicons.glyphMap }) {
  return (
    <View style={styles.stepCard} data-testid={`landing-step-${n}`}>
      <View style={styles.stepNumRow}>
        <View style={styles.stepNum}><Text style={styles.stepNumText}>{n}</Text></View>
        <View style={styles.stepIconWrap}>
          <Ionicons name={icon} size={18} color={COLORS.accent} />
        </View>
      </View>
      <Text style={styles.stepTitle}>{title}</Text>
      <Text style={styles.stepBody}>{body}</Text>
    </View>
  );
}

const styles = StyleSheet.create({
  scroll: { flex: 1, backgroundColor: COLORS.bg },
  scrollContent: { paddingBottom: 64 },

  // ── Nav ──
  nav: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'space-between',
    paddingHorizontal: 40,
    paddingVertical: 18,
    backgroundColor: 'rgba(255,255,255,0.85)',
    borderBottomWidth: 1,
    borderBottomColor: COLORS.border,
    // @ts-ignore web-only
    backdropFilter: 'saturate(180%) blur(12px)',
    // @ts-ignore web-only
    position: 'sticky',
    // @ts-ignore
    top: 0,
    zIndex: 40,
  },
  navMobile: { paddingHorizontal: 20, paddingVertical: 14 },
  brand: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  brandMark: {
    width: 32, height: 32, borderRadius: 8,
    backgroundColor: COLORS.accent,
    alignItems: 'center', justifyContent: 'center',
  },
  brandName: { fontSize: 17, fontWeight: '800', color: COLORS.textPrimary, letterSpacing: -0.2 },
  navLinks: { flexDirection: 'row', gap: 28 },
  navLink: { fontSize: 14, fontWeight: '600', color: COLORS.textSecondary },
  navActions: { flexDirection: 'row', alignItems: 'center', gap: 10 },
  navSignIn: {
    paddingHorizontal: 14, paddingVertical: 9,
    borderRadius: 8,
  },
  navSignInText: { fontSize: 14, fontWeight: '600', color: COLORS.textPrimary },
  navCta: {
    paddingHorizontal: 16, paddingVertical: 10,
    borderRadius: 8, backgroundColor: COLORS.accent,
  },
  navCtaText: { fontSize: 14, fontWeight: '700', color: '#FFFFFF' },
  hamburger: {
    width: 36, height: 36, borderRadius: 8,
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: COLORS.border,
  },
  mobileMenu: {
    backgroundColor: COLORS.surface,
    borderBottomWidth: 1, borderBottomColor: COLORS.border,
    paddingHorizontal: 20, paddingVertical: 8,
  },
  mobileMenuItem: {
    paddingVertical: 12,
    borderBottomWidth: 1, borderBottomColor: '#F3F4F6',
  },
  mobileMenuText: { fontSize: 15, fontWeight: '600', color: COLORS.textPrimary },

  // ── Hero ──
  hero: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 48,
    maxWidth: 1200,
    width: '100%',
    alignSelf: 'center',
    paddingHorizontal: 40,
    paddingTop: 72,
    paddingBottom: 72,
  },
  heroNarrow: { flexDirection: 'column', gap: 40, paddingHorizontal: 20, paddingTop: 40, paddingBottom: 40 },
  heroText: { flex: 1, maxWidth: 620 },
  heroEyebrowRow: { flexDirection: 'row', alignItems: 'center', gap: 8, marginBottom: 20 },
  heroEyebrowDot: { width: 6, height: 6, borderRadius: 3, backgroundColor: COLORS.accent },
  heroEyebrow: {
    fontSize: 12,
    fontWeight: '800',
    color: COLORS.accent,
    letterSpacing: 1.6,
  },
  heroHeadline: {
    fontSize: 56,
    fontWeight: '800',
    color: COLORS.textPrimary,
    lineHeight: 62,
    letterSpacing: -1.2,
    marginBottom: 20,
  },
  heroHeadlineMobile: { fontSize: 38, lineHeight: 44, letterSpacing: -0.8 },
  heroLead: {
    fontSize: 18,
    fontWeight: '600',
    color: COLORS.textPrimary,
    marginBottom: 12,
    lineHeight: 26,
  },
  heroBody: {
    fontSize: 15,
    color: COLORS.textSecondary,
    lineHeight: 24,
    marginBottom: 28,
    maxWidth: 560,
  },
  heroCtaRow: { flexDirection: 'row', gap: 12, alignItems: 'center', marginBottom: 16 },
  heroCtaRowMobile: { flexDirection: 'column', alignItems: 'stretch', gap: 10 },
  primaryCta: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    paddingHorizontal: 22,
    paddingVertical: 14,
    borderRadius: 10,
    backgroundColor: COLORS.accent,
    // @ts-ignore
    boxShadow: '0 6px 18px rgba(92,107,192,0.28)',
    minHeight: 48,
  },
  primaryCtaText: { color: '#FFFFFF', fontSize: 15, fontWeight: '700', letterSpacing: 0.2 },
  secondaryCta: {
    paddingHorizontal: 22,
    paddingVertical: 14,
    borderRadius: 10,
    backgroundColor: COLORS.surface,
    borderWidth: 1, borderColor: COLORS.border,
    minHeight: 48,
    alignItems: 'center', justifyContent: 'center',
  },
  secondaryCtaText: { color: COLORS.textPrimary, fontSize: 15, fontWeight: '600' },
  heroSubCta: {
    fontSize: 12,
    color: COLORS.textMuted,
    marginBottom: 28,
    fontWeight: '500',
  },
  trustRow: { flexDirection: 'row', gap: 20, flexWrap: 'wrap' },
  trustRowMobile: { gap: 12 },
  trustItem: { flexDirection: 'row', alignItems: 'center', gap: 6 },
  trustText: { fontSize: 13, color: COLORS.textPrimary, fontWeight: '600' },

  // Hero visual (right column)
  heroVisual: { flex: 1, maxWidth: 500, alignItems: 'flex-end', position: 'relative' as any },
  heroImageCard: {
    width: '100%',
    aspectRatio: 4 / 3,
    borderRadius: 16,
    overflow: 'hidden',
    borderWidth: 1,
    borderColor: COLORS.accentBorder,
    // @ts-ignore
    boxShadow: '0 22px 60px rgba(40,53,147,0.22)',
    position: 'relative' as any,
  },
  heroImage: { width: '100%', height: '100%' },
  heroImageOverlay: {
    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
    // @ts-ignore web-only gradient
    backgroundImage:
      'linear-gradient(150deg, rgba(40,53,147,0.35) 0%, rgba(40,53,147,0.05) 45%, rgba(255,255,255,0) 100%)',
  },
  heroBadgeTL: {
    position: 'absolute', top: 16, left: 16,
    flexDirection: 'row', alignItems: 'center', gap: 6,
    backgroundColor: 'rgba(40,53,147,0.9)',
    paddingHorizontal: 12, paddingVertical: 6,
    borderRadius: 999,
  },
  heroBadgeText: { color: '#FFFFFF', fontSize: 11, fontWeight: '700', letterSpacing: 0.5 },
  heroStatCard: {
    position: 'absolute',
    bottom: -20,
    left: -20,
    flexDirection: 'row',
    alignItems: 'center',
    gap: 12,
    backgroundColor: COLORS.surface,
    paddingHorizontal: 16, paddingVertical: 12,
    borderRadius: 12,
    borderWidth: 1, borderColor: COLORS.border,
    // @ts-ignore
    boxShadow: '0 8px 22px rgba(17,24,39,0.08)',
  },
  heroStatIconWrap: {
    width: 36, height: 36, borderRadius: 8,
    backgroundColor: COLORS.accent,
    alignItems: 'center', justifyContent: 'center',
  },
  heroStatBody: {},
  heroStatNum: { fontSize: 15, fontWeight: '800', color: COLORS.textPrimary },
  heroStatLabel: { fontSize: 11, color: COLORS.textMuted, fontWeight: '500' },

  // ── Sections ──
  section: {
    maxWidth: 1200,
    width: '100%',
    alignSelf: 'center',
    paddingHorizontal: 40,
    paddingTop: 72,
    paddingBottom: 8,
  },
  sectionAlt: { paddingTop: 40 },
  sectionEyebrow: {
    fontSize: 12,
    fontWeight: '800',
    color: COLORS.accent,
    letterSpacing: 1.6,
    marginBottom: 12,
  },
  sectionHeadline: {
    fontSize: 36,
    fontWeight: '800',
    color: COLORS.textPrimary,
    lineHeight: 42,
    letterSpacing: -0.6,
    marginBottom: 12,
    maxWidth: 720,
  },
  sectionHeadlineMobile: { fontSize: 28, lineHeight: 34 },
  sectionLead: {
    fontSize: 15,
    color: COLORS.textSecondary,
    lineHeight: 24,
    maxWidth: 640,
    marginBottom: 40,
  },

  // Feature grid — 3 across desktop, 2 tablet, 1 mobile
  featureGrid: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    gap: 20,
  },
  featureGridTablet: {},
  featureGridMobile: { gap: 14 },
  featureCard: {
    // 3 columns: (100% - 2*gap) / 3
    // @ts-ignore
    width: 'calc((100% - 40px) / 3)',
    minWidth: 220,
    padding: 24,
    backgroundColor: COLORS.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
    // @ts-ignore web-only hover elevation
    transition: 'transform 200ms ease, box-shadow 200ms ease, border-color 200ms ease',
    // @ts-ignore
    ':hover': { transform: 'translateY(-3px)', borderColor: COLORS.accentBorder },
  },
  featureIconWrap: {
    width: 44, height: 44, borderRadius: 10,
    backgroundColor: COLORS.accentSoft,
    alignItems: 'center', justifyContent: 'center',
    marginBottom: 16,
    borderWidth: 1, borderColor: COLORS.accentBorder,
  },
  featureTitle: { fontSize: 16, fontWeight: '700', color: COLORS.textPrimary, marginBottom: 6 },
  featureBody: { fontSize: 13, color: COLORS.textSecondary, lineHeight: 20 },

  // Steps
  stepsRow: { flexDirection: 'row', gap: 20 },
  stepsRowMobile: { flexDirection: 'column' },
  stepCard: {
    flex: 1,
    padding: 24,
    backgroundColor: COLORS.surface,
    borderRadius: 14,
    borderWidth: 1,
    borderColor: COLORS.border,
    minWidth: 220,
  },
  stepNumRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 16 },
  stepNum: {
    width: 28, height: 28, borderRadius: 14,
    backgroundColor: COLORS.accent,
    alignItems: 'center', justifyContent: 'center',
  },
  stepNumText: { color: '#FFFFFF', fontSize: 13, fontWeight: '800' },
  stepIconWrap: {
    width: 32, height: 32, borderRadius: 8,
    backgroundColor: COLORS.accentSoft,
    alignItems: 'center', justifyContent: 'center',
    borderWidth: 1, borderColor: COLORS.accentBorder,
  },
  stepTitle: { fontSize: 15, fontWeight: '700', color: COLORS.textPrimary, marginBottom: 6 },
  stepBody: { fontSize: 13, color: COLORS.textSecondary, lineHeight: 20 },

  // Workspace strip
  workspaceStrip: {
    maxWidth: 1200,
    width: '100%',
    alignSelf: 'center',
    marginTop: 40,
    marginHorizontal: 40,
    borderRadius: 20,
    overflow: 'hidden',
    position: 'relative' as any,
    minHeight: 260,
    justifyContent: 'center',
    padding: 40,
  },
  workspaceStripMobile: { marginHorizontal: 20, padding: 28, minHeight: 220 },
  workspaceImg: {
    position: 'absolute',
    top: 0, left: 0, right: 0, bottom: 0,
    width: '100%', height: '100%',
  },
  workspaceOverlay: {
    position: 'absolute', top: 0, left: 0, right: 0, bottom: 0,
    // @ts-ignore
    backgroundImage:
      'linear-gradient(135deg, rgba(40,53,147,0.92) 0%, rgba(63,76,159,0.88) 55%, rgba(92,107,192,0.82) 100%)',
  },
  workspaceBody: { position: 'relative' as any, maxWidth: 640 },
  workspaceEyebrow: {
    fontSize: 12,
    fontWeight: '800',
    color: 'rgba(255,255,255,0.85)',
    letterSpacing: 1.6,
    marginBottom: 10,
  },
  workspaceHeadline: {
    fontSize: 30,
    fontWeight: '800',
    color: '#FFFFFF',
    lineHeight: 36,
    marginBottom: 10,
    letterSpacing: -0.4,
  },
  workspaceLead: {
    fontSize: 15,
    color: 'rgba(255,255,255,0.9)',
    lineHeight: 24,
    marginBottom: 24,
    maxWidth: 560,
  },
  workspaceCtaRow: { marginBottom: 0 },
  secondaryCtaLight: {
    paddingHorizontal: 22,
    paddingVertical: 14,
    borderRadius: 10,
    backgroundColor: 'rgba(255,255,255,0.12)',
    borderWidth: 1, borderColor: 'rgba(255,255,255,0.35)',
    minHeight: 48,
    alignItems: 'center', justifyContent: 'center',
  },
  secondaryCtaLightText: { color: '#FFFFFF', fontSize: 15, fontWeight: '600' },
});
