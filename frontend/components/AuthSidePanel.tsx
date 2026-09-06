/**
 * AuthSidePanel — the panel shown beside the login/signup card on wide
 * screens (desktop auth shell, replaces the old LoginShellWidgets grid).
 *
 * Deliberately reuses the homepage's own visual language (palette, tip
 * copy, trust labels) so the auth pages read as part of the same product
 * instead of a disconnected mini-dashboard:
 *   - Brand mark + one-line positioning (mirrors the hero eyebrow/headline)
 *   - Trust / identity strip (same labels used in the homepage's Kenyan
 *     identity band)
 *   - A single rotating teaching tip, styled like the homepage's tip card
 *
 * Kept intentionally light — one panel, not five widgets — so it fills
 * the space without competing with the auth form for attention.
 */
import React, { useRef, useState } from 'react';
import { View, Text, Pressable, StyleSheet, Animated, useWindowDimensions } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

// Mirrors app/index.tsx's COLORS so the auth shell matches the homepage.
// Kept as a local copy rather than a shared import to keep this change
// scoped to the auth flow (see app/index.tsx's own COLORS for the source
// of truth on the homepage itself).
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
};

// Same copy as the homepage's TEACHING_TIPS, so a teacher sees consistent
// content whether they're browsing the landing page or signing in.
const TEACHING_TIPS = [
  'Start each lesson with a real-life scenario relevant to learners\u2019 environment to boost engagement.',
  'Use differentiated tasks \u2014 a guided example, paired practice, then an independent challenge.',
  'Align your learning outcomes to KICD strand competencies before writing your lesson plan.',
  'Group work boosts competency development \u2014 assign roles so every learner participates actively.',
  'Formative assessment doesn\u2019t need to be formal \u2014 exit slips or a quick Q&A work just as well.',
  'Celebrate small wins in class \u2014 positive reinforcement improves learner confidence and attendance.',
  'CBC emphasises values, skills and competencies over rote memorization \u2014 plan accordingly.',
  'Review your scheme of work weekly and align it with KICD guidelines to stay on track.',
];

const KENYA_LABELS: { icon: keyof typeof Ionicons.glyphMap; text: string }[] = [
  { icon: 'flag-outline', text: 'Kenyan Teachers' },
  { icon: 'school-outline', text: 'CBC / CBE' },
  { icon: 'library-outline', text: 'KICD-Aligned' },
];

const RotatingTip: React.FC = () => {
  const [idx, setIdx] = useState(() => Math.floor(Math.random() * TEACHING_TIPS.length));
  const fade = useRef(new Animated.Value(1)).current;

  const go = (dir: 1 | -1) => {
    Animated.timing(fade, { toValue: 0, duration: 160, useNativeDriver: true }).start(() => {
      setIdx((i) => (i + dir + TEACHING_TIPS.length) % TEACHING_TIPS.length);
      Animated.timing(fade, { toValue: 1, duration: 240, useNativeDriver: true }).start();
    });
  };

  return (
    <View style={s.tipCard}>
      <Text style={s.tipQuoteMark}>&ldquo;</Text>

      <View style={s.tipHeader}>
        <View style={s.tipIconWrap}>
          <Ionicons name="bulb-outline" size={20} color="#FFFFFF" />
        </View>
        <View style={{ flex: 1 }}>
          <Text style={s.tipEyebrow}>TEACHING TIP</Text>
          <Text style={s.tipCounter}>
            {idx + 1} / {TEACHING_TIPS.length}
          </Text>
        </View>
      </View>

      <Animated.Text style={[s.tipBody, { opacity: fade }]}>{TEACHING_TIPS[idx]}</Animated.Text>

      <View style={s.tipFooter}>
        <View style={s.tipDots}>
          {TEACHING_TIPS.map((_, i) => (
            <Pressable key={i} onPress={() => setIdx(i)} hitSlop={6}>
              <View style={[s.tipDot, i === idx && s.tipDotActive]} />
            </Pressable>
          ))}
        </View>
        <View style={{ flexDirection: 'row', gap: 8 }}>
          <Pressable style={s.tipNavBtn} onPress={() => go(-1)} hitSlop={6}>
            <Ionicons name="chevron-back" size={16} color={COLORS.textSecondary} />
          </Pressable>
          <Pressable style={s.tipNavBtn} onPress={() => go(1)} hitSlop={6}>
            <Ionicons name="chevron-forward" size={16} color={COLORS.textSecondary} />
          </Pressable>
        </View>
      </View>
    </View>
  );
};

export const AuthSidePanel: React.FC = () => {
  const { width } = useWindowDimensions();
  const compact = width < 1400;

  return (
    <View style={[s.panel, compact && s.panelCompact]}>
      <View style={s.brandRow}>
        <View style={s.brandMark}>
          <Ionicons name="school" size={20} color="#FFFFFF" />
        </View>
        <Text style={s.brandName}>CBE Planner</Text>
      </View>

      <Text style={s.headline}>Curriculum planning built for the Kenyan classroom.</Text>
      <Text style={s.lead}>
        Schemes of work, lesson plans, teaching notes and revision resources — aligned to CBC/CBE and ready in
        minutes.
      </Text>

      <View style={s.trustRow}>
        {KENYA_LABELS.map((l) => (
          <View key={l.text} style={s.trustPill}>
            <Ionicons name={l.icon} size={13} color={COLORS.accent} />
            <Text style={s.trustText}>{l.text}</Text>
          </View>
        ))}
      </View>

      <RotatingTip />
    </View>
  );
};

const s = StyleSheet.create({
  panel: {
    flex: 1,
    maxWidth: 520,
    justifyContent: 'center',
    paddingVertical: 20,
  },
  panelCompact: { maxWidth: 420 },

  brandRow: { flexDirection: 'row', alignItems: 'center', gap: 10, marginBottom: 22 },
  brandMark: {
    width: 34,
    height: 34,
    borderRadius: 9,
    backgroundColor: COLORS.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  brandName: { fontSize: 16, fontWeight: '700', color: COLORS.textPrimary },

  headline: {
    fontSize: 26,
    fontWeight: '800',
    color: COLORS.textPrimary,
    lineHeight: 33,
    letterSpacing: -0.4,
    marginBottom: 12,
  },
  lead: {
    fontSize: 14,
    color: COLORS.textSecondary,
    lineHeight: 21,
    marginBottom: 22,
    maxWidth: 440,
  },

  trustRow: { flexDirection: 'row', flexWrap: 'wrap', gap: 8, marginBottom: 28 },
  trustPill: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    paddingHorizontal: 11,
    paddingVertical: 7,
    borderRadius: 999,
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.accentBorder,
  },
  trustText: { fontSize: 12, fontWeight: '600', color: COLORS.textPrimary },

  // Tip card — mirrors app/index.tsx's tipCard treatment at a smaller scale.
  tipCard: {
    padding: 24,
    borderRadius: 16,
    backgroundColor: COLORS.surface,
    borderWidth: 1,
    borderColor: COLORS.border,
    // @ts-ignore web-only
    boxShadow: '0 10px 28px rgba(17,24,39,0.06)',
    position: 'relative',
    overflow: 'hidden',
  },
  tipQuoteMark: {
    position: 'absolute',
    top: 6,
    right: 16,
    fontSize: 72,
    lineHeight: 60,
    color: COLORS.accentSoft,
    fontWeight: '800',
    // @ts-ignore web-only
    userSelect: 'none',
  },
  tipHeader: { flexDirection: 'row', alignItems: 'center', gap: 12, marginBottom: 14 },
  tipIconWrap: {
    width: 36,
    height: 36,
    borderRadius: 10,
    backgroundColor: COLORS.accent,
    alignItems: 'center',
    justifyContent: 'center',
  },
  tipEyebrow: { fontSize: 10, fontWeight: '800', letterSpacing: 1.4, color: COLORS.accent },
  tipCounter: { fontSize: 11, fontWeight: '700', color: COLORS.textMuted, marginTop: 2 },
  tipBody: { fontSize: 15, lineHeight: 23, color: COLORS.textPrimary, fontWeight: '500', marginBottom: 18 },
  tipFooter: { flexDirection: 'row', alignItems: 'center', justifyContent: 'space-between' },
  tipDots: { flexDirection: 'row', gap: 6 },
  tipDot: { width: 6, height: 6, borderRadius: 999, backgroundColor: COLORS.accentBorder },
  tipDotActive: { backgroundColor: COLORS.accent, width: 16 },
  tipNavBtn: {
    width: 30,
    height: 30,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: COLORS.border,
    alignItems: 'center',
    justifyContent: 'center',
  },
});

export default AuthSidePanel;
