import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

interface SchemeLesson {
  week: number;
  lesson?: string | number;
  lessonNumber?: number;
  isBreak?: boolean;
  isDouble?: boolean;
  breakType?: string | null;
  breakDescription?: string | null;
  strand?: string;
  substrand?: string;
  slo?: string;
  keyInquiryQuestions?: string[] | string;
  learningExperiences?: string[] | string;
  learningResources?: string[] | string;
  assessmentMethods?: string[] | string;
  competencies?: string[] | string;
  values?: string[] | string;
  coreCompetencies?: string[] | string;
  coreValues?: string[] | string;
  pcis?: string[] | string;
}

interface SchemeDisplayProps {
  scheme: {
    schoolName?: string;
    gradeName: string;
    subjectName: string;
    term: number;
    year: number;
    totalWeeks?: number;
    lessonsPerWeek?: number;
    lessons: SchemeLesson[];
    createdAt?: string;
  };
}

export const SchemeDisplay: React.FC<SchemeDisplayProps> = ({ scheme }) => {
  const lessons = scheme.lessons || [];

  const toList = (val?: string[] | string): string[] => {
    if (!val) return [];
    if (Array.isArray(val)) return val.filter(Boolean);
    // Legacy schemes stored these as comma/newline separated strings
    return String(val)
      .split(/\n|,|;/)
      .map((s) => s.trim())
      .filter(Boolean);
  };

  const renderList = (val?: string[] | string) => {
    const items = toList(val);
    if (items.length === 0) return '—';
    return items.map((i) => `• ${i}`).join('\n');
  };

  const lessonLabel = (l: SchemeLesson): string => {
    if (l.lesson !== undefined && l.lesson !== null) return String(l.lesson);
    if (l.lessonNumber !== undefined && l.lessonNumber !== null) return String(l.lessonNumber);
    return '';
  };

  return (
    <ScrollView style={styles.container} contentContainerStyle={styles.content}>
      {/* Document Header */}
      <View style={styles.documentHeader}>
        <Text style={styles.documentTitle}>REPUBLIC OF KENYA</Text>
        <Text style={styles.documentSubtitle}>COMPETENCY-BASED CURRICULUM</Text>
        <Text style={styles.documentType}>SCHEME OF WORK</Text>
      </View>

      {/* Meta block */}
      <View style={styles.metaBlock}>
        <View style={styles.metaRow}>
          <Text style={styles.metaLabel}>School</Text>
          <Text style={styles.metaValue}>{scheme.schoolName || '—'}</Text>
        </View>
        <View style={styles.metaRow}>
          <Text style={styles.metaLabel}>Grade</Text>
          <Text style={styles.metaValue}>{scheme.gradeName}</Text>
        </View>
        <View style={styles.metaRow}>
          <Text style={styles.metaLabel}>Subject</Text>
          <Text style={styles.metaValue}>{scheme.subjectName}</Text>
        </View>
        <View style={styles.metaRow}>
          <Text style={styles.metaLabel}>Term</Text>
          <Text style={styles.metaValue}>
            Term {scheme.term}, {scheme.year}
          </Text>
        </View>
        {scheme.totalWeeks ? (
          <View style={styles.metaRow}>
            <Text style={styles.metaLabel}>Duration</Text>
            <Text style={styles.metaValue}>
              {scheme.totalWeeks} weeks · {scheme.lessonsPerWeek || '—'} lessons/week
            </Text>
          </View>
        ) : null}
      </View>

      {/* Scheme table */}
      <ScrollView horizontal showsHorizontalScrollIndicator={true} style={styles.tableScroll}>
        <View style={styles.table}>
          {/* Header row */}
          <View style={[styles.row, styles.headerRow]}>
            <View style={[styles.cell, styles.colWeek]}><Text style={styles.headerText}>WK</Text></View>
            <View style={[styles.cell, styles.colLesson]}><Text style={styles.headerText}>LSN</Text></View>
            <View style={[styles.cell, styles.colStrand]}><Text style={styles.headerText}>Strand</Text></View>
            <View style={[styles.cell, styles.colSubstrand]}><Text style={styles.headerText}>Sub-strand</Text></View>
            <View style={[styles.cell, styles.colSlo]}><Text style={styles.headerText}>Specific Learning Outcomes</Text></View>
            <View style={[styles.cell, styles.colInquiry]}><Text style={styles.headerText}>Key Inquiry Question(s)</Text></View>
            <View style={[styles.cell, styles.colExp]}><Text style={styles.headerText}>Learning Experiences</Text></View>
            <View style={[styles.cell, styles.colRes]}><Text style={styles.headerText}>Learning Resources</Text></View>
            <View style={[styles.cell, styles.colAssess]}><Text style={styles.headerText}>Assessment</Text></View>
            <View style={[styles.cell, styles.colRef, styles.lastCell]}><Text style={styles.headerText}>Ref.</Text></View>
          </View>

          {/* Body rows */}
          {lessons.map((l, idx) => {
            if (l.isBreak) {
              return (
                <View key={idx} style={[styles.row, styles.breakRow]}>
                  <View style={[styles.cell, styles.colWeek]}>
                    <Text style={styles.breakText}>{l.week}</Text>
                  </View>
                  <View style={[styles.cell, styles.colLesson]}>
                    <Text style={styles.breakText}>{lessonLabel(l)}</Text>
                  </View>
                  <View style={[styles.cell, styles.breakContent, styles.lastCell]}>
                    <Text style={styles.breakLabel}>
                      {l.breakType || l.breakDescription || 'Break'}
                    </Text>
                  </View>
                </View>
              );
            }

            return (
              <View key={idx} style={[styles.row, idx % 2 === 1 && styles.zebraRow]}>
                <View style={[styles.cell, styles.colWeek]}>
                  <Text style={styles.cellText}>{l.week}</Text>
                </View>
                <View style={[styles.cell, styles.colLesson]}>
                  <Text style={styles.cellText}>
                    {lessonLabel(l)}
                    {l.isDouble ? '\n(Dbl)' : ''}
                  </Text>
                </View>
                <View style={[styles.cell, styles.colStrand]}>
                  <Text style={styles.cellText}>{l.strand || '—'}</Text>
                </View>
                <View style={[styles.cell, styles.colSubstrand]}>
                  <Text style={styles.cellText}>{l.substrand || '—'}</Text>
                </View>
                <View style={[styles.cell, styles.colSlo]}>
                  <Text style={styles.cellText}>{l.slo || '—'}</Text>
                </View>
                <View style={[styles.cell, styles.colInquiry]}>
                  <Text style={styles.cellText}>{renderList(l.keyInquiryQuestions)}</Text>
                </View>
                <View style={[styles.cell, styles.colExp]}>
                  <Text style={styles.cellText}>{renderList(l.learningExperiences)}</Text>
                </View>
                <View style={[styles.cell, styles.colRes]}>
                  <Text style={styles.cellText}>{renderList(l.learningResources)}</Text>
                </View>
                <View style={[styles.cell, styles.colAssess]}>
                  <Text style={styles.cellText}>{renderList(l.assessmentMethods)}</Text>
                </View>
                <View style={[styles.cell, styles.colRef, styles.lastCell]}>
                  <Text style={styles.cellText}>—</Text>
                </View>
              </View>
            );
          })}
        </View>
      </ScrollView>

      {/* Footer */}
      <View style={styles.footerNote}>
        <Text style={styles.footerText}>
          Swipe table horizontally to view all columns · KICD-aligned scheme of work
        </Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
  },
  content: {
    paddingBottom: 40,
  },
  documentHeader: {
    alignItems: 'center',
    paddingVertical: 18,
    backgroundColor: '#1E3A8A',
  },
  documentTitle: {
    color: '#FFFFFF',
    fontSize: 13,
    fontWeight: '700',
    letterSpacing: 2,
  },
  documentSubtitle: {
    color: '#BFDBFE',
    fontSize: 11,
    fontWeight: '600',
    letterSpacing: 1.5,
    marginTop: 2,
  },
  documentType: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '800',
    letterSpacing: 3,
    marginTop: 10,
  },
  metaBlock: {
    padding: 16,
    backgroundColor: '#F9FAFB',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
  },
  metaRow: {
    flexDirection: 'row',
    paddingVertical: 4,
  },
  metaLabel: {
    width: 90,
    fontSize: 12,
    fontWeight: '600',
    color: '#6B7280',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  metaValue: {
    flex: 1,
    fontSize: 13,
    color: '#111827',
    fontWeight: '500',
  },
  tableScroll: {
    marginTop: 8,
  },
  table: {
    borderWidth: 1,
    borderColor: '#D1D5DB',
    borderRightWidth: 0,
    marginHorizontal: 8,
  },
  row: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#D1D5DB',
  },
  headerRow: {
    backgroundColor: '#1E40AF',
  },
  zebraRow: {
    backgroundColor: '#F9FAFB',
  },
  breakRow: {
    backgroundColor: '#FEF3C7',
  },
  cell: {
    borderRightWidth: 1,
    borderRightColor: '#D1D5DB',
    paddingHorizontal: 8,
    paddingVertical: 8,
    justifyContent: 'flex-start',
  },
  lastCell: {
    borderRightWidth: 1,
  },
  headerText: {
    color: '#FFFFFF',
    fontSize: 11,
    fontWeight: '700',
    textAlign: 'center',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  cellText: {
    fontSize: 11,
    color: '#111827',
    lineHeight: 16,
  },
  colWeek: { width: 40, alignItems: 'center' },
  colLesson: { width: 50, alignItems: 'center' },
  colStrand: { width: 110 },
  colSubstrand: { width: 120 },
  colSlo: { width: 200 },
  colInquiry: { width: 180 },
  colExp: { width: 200 },
  colRes: { width: 170 },
  colAssess: { width: 150 },
  colRef: { width: 70 },
  breakContent: {
    flex: 1,
    alignItems: 'center',
    justifyContent: 'center',
  },
  breakText: {
    color: '#92400E',
    fontSize: 11,
    fontWeight: '700',
  },
  breakLabel: {
    color: '#92400E',
    fontSize: 12,
    fontWeight: '700',
    textTransform: 'uppercase',
    letterSpacing: 0.5,
  },
  footerNote: {
    padding: 12,
    alignItems: 'center',
  },
  footerText: {
    fontSize: 11,
    color: '#9CA3AF',
    fontStyle: 'italic',
  },
});
