import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

interface LessonPlanDisplayProps {
  lessonPlan: any;
}

export const LessonPlanDisplay: React.FC<LessonPlanDisplayProps> = ({ lessonPlan }) => {
  const TableRow = ({ label, value }: { label: string; value: string }) => (
    <View style={styles.tableRow}>
      <Text style={styles.tableLabel}>{label}</Text>
      <Text style={styles.tableValue}>{value || 'N/A'}</Text>
    </View>
  );

  const SectionHeader = ({ title }: { title: string }) => (
    <View style={styles.sectionHeader}>
      <Text style={styles.sectionHeaderText}>{title}</Text>
    </View>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Header */}
      <View style={styles.header}>
        <Text style={styles.documentTitle}>COMPETENCY-BASED EDUCATION</Text>
        <Text style={styles.documentSubtitle}>LESSON PLAN</Text>
        <Text style={styles.documentInfo}>Republic of Kenya</Text>
      </View>

      {/* Teacher & School Information */}
      <View style={styles.section}>
        <TableRow label="Teacher's Name" value={lessonPlan.teacherName} />
        <TableRow label="School Name" value={lessonPlan.schoolName} />
        <TableRow label="Date" value={new Date().toLocaleDateString('en-GB')} />
      </View>

      {/* Lesson Details */}
      <SectionHeader title="LESSON DETAILS" />
      <View style={styles.section}>
        <TableRow label="Grade/Class" value={lessonPlan.gradeName} />
        <TableRow label="Learning Area" value={lessonPlan.subjectName} />
        <TableRow label="Strand" value={lessonPlan.strandName} />
        <TableRow label="Sub-Strand" value={lessonPlan.substrandName} />
        <TableRow label="Duration" value={`${lessonPlan.duration} minutes`} />
      </View>

      {/* Specific Learning Outcomes */}
      <SectionHeader title="SPECIFIC LEARNING OUTCOMES (SLOs)" />
      <View style={styles.section}>
        <Text style={styles.sloMainText}>{lessonPlan.sloName}</Text>
        <Text style={styles.sloDescription}>{lessonPlan.sloDescription}</Text>
        
        <View style={styles.sloCategory}>
          <Text style={styles.sloCategoryTitle}>Knowledge:</Text>
          {lessonPlan.knowledge?.map((item: string, i: number) => (
            <Text key={i} style={styles.sloBullet}>• {item}</Text>
          )) || <Text style={styles.emptyState}>No knowledge outcomes specified</Text>}
        </View>

        <View style={styles.sloCategory}>
          <Text style={styles.sloCategoryTitle}>Skills:</Text>
          {lessonPlan.skills?.map((item: string, i: number) => (
            <Text key={i} style={styles.sloBullet}>• {item}</Text>
          )) || <Text style={styles.emptyState}>No skill outcomes specified</Text>}
        </View>

        <View style={styles.sloCategory}>
          <Text style={styles.sloCategoryTitle}>Attitudes:</Text>
          {lessonPlan.attitudes?.map((item: string, i: number) => (
            <Text key={i} style={styles.sloBullet}>• {item}</Text>
          )) || <Text style={styles.emptyState}>No attitude outcomes specified</Text>}
        </View>
      </View>

      {/* Learning Resources */}
      <SectionHeader title="LEARNING RESOURCES" />
      <View style={styles.section}>
        {lessonPlan.learningResources?.length > 0 ? (
          lessonPlan.learningResources.map((resource: string, i: number) => (
            <Text key={i} style={styles.listItem}>• {resource}</Text>
          ))
        ) : (
          <Text style={styles.emptyState}>No learning resources specified</Text>
        )}
      </View>

      {/* Core Competencies */}
      <SectionHeader title="CORE COMPETENCIES" />
      <View style={styles.section}>
        {lessonPlan.competencies?.length > 0 ? (
          lessonPlan.competencies.map((comp: any, i: number) => (
            <View key={i} style={styles.competencyItem}>
              <Text style={styles.competencyName}>{i + 1}. {comp.name}</Text>
              <Text style={styles.competencyDescription}>{comp.description}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyState}>No core competencies specified</Text>
        )}
      </View>

      {/* Core Values */}
      <SectionHeader title="CORE VALUES" />
      <View style={styles.section}>
        {lessonPlan.values?.length > 0 ? (
          lessonPlan.values.map((value: any, i: number) => (
            <View key={i} style={styles.competencyItem}>
              <Text style={styles.competencyName}>{i + 1}. {value.name}</Text>
              <Text style={styles.competencyDescription}>{value.description}</Text>
            </View>
          ))
        ) : (
          <Text style={styles.emptyState}>No core values specified</Text>
        )}
      </View>

      {/* Pertinent & Contemporary Issues */}
      {lessonPlan.pcis && lessonPlan.pcis.length > 0 && (
        <>
          <SectionHeader title="PERTINENT & CONTEMPORARY ISSUES (PCIs)" />
          <View style={styles.section}>
            {lessonPlan.pcis.map((pci: any, i: number) => (
              <View key={i} style={styles.competencyItem}>
                <Text style={styles.competencyName}>{i + 1}. {pci.name}</Text>
                <Text style={styles.competencyDescription}>{pci.description}</Text>
              </View>
            ))}
          </View>
        </>
      )}

      {/* Lesson Procedure */}
      <SectionHeader title="LESSON PROCEDURE" />
      <View style={styles.section}>
        <View style={styles.procedureStep}>
          <Text style={styles.procedureTitle}>STEP 1: INTRODUCTION</Text>
          <Text style={styles.procedureContent}>{lessonPlan.introduction || 'No introduction content specified'}</Text>
        </View>

        <View style={styles.procedureStep}>
          <Text style={styles.procedureTitle}>STEP 2: LESSON DEVELOPMENT</Text>
          <Text style={styles.procedureContent}>{lessonPlan.lessonDevelopment || 'No lesson development content specified'}</Text>
        </View>

        {lessonPlan.extendedActivity && (
          <View style={styles.procedureStep}>
            <Text style={styles.procedureTitle}>STEP 3: EXTENDED ACTIVITY</Text>
            <Text style={styles.procedureContent}>{lessonPlan.extendedActivity}</Text>
          </View>
        )}

        <View style={styles.procedureStep}>
          <Text style={styles.procedureTitle}>
            {lessonPlan.extendedActivity ? 'STEP 4: CONCLUSION' : 'STEP 3: CONCLUSION'}
          </Text>
          <Text style={styles.procedureContent}>{lessonPlan.conclusion || 'No conclusion content specified'}</Text>
        </View>
      </View>

      {/* Assessment */}
      <SectionHeader title="ASSESSMENT" />
      <View style={styles.section}>
        <Text style={styles.assessmentContent}>{lessonPlan.assessment || 'No assessment methods specified'}</Text>
      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <View style={styles.signatureSection}>
          <Text style={styles.signatureLabel}>Teacher's Signature: ___________________</Text>
          <Text style={styles.signatureLabel}>Date: ___________________</Text>
        </View>
        <View style={styles.signatureSection}>
          <Text style={styles.signatureLabel}>Head Teacher's Signature: ___________________</Text>
          <Text style={styles.signatureLabel}>Date: ___________________</Text>
        </View>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 16
  },
  header: {
    alignItems: 'center',
    borderBottomWidth: 2,
    borderBottomColor: '#000000',
    paddingBottom: 16,
    marginBottom: 16
  },
  documentTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#000000',
    textAlign: 'center'
  },
  documentSubtitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#000000',
    marginTop: 4
  },
  documentInfo: {
    fontSize: 12,
    color: '#666666',
    marginTop: 4
  },
  sectionHeader: {
    backgroundColor: '#E5E7EB',
    padding: 10,
    marginTop: 16,
    marginBottom: 8,
    borderLeftWidth: 4,
    borderLeftColor: '#4338CA'
  },
  sectionHeaderText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1F2937'
  },
  section: {
    marginBottom: 8
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#E5E7EB',
    paddingVertical: 8
  },
  tableLabel: {
    width: '40%',
    fontSize: 13,
    fontWeight: '600',
    color: '#374151'
  },
  tableValue: {
    width: '60%',
    fontSize: 13,
    color: '#1F2937'
  },
  sloMainText: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8
  },
  sloDescription: {
    fontSize: 13,
    color: '#4B5563',
    marginBottom: 12,
    fontStyle: 'italic'
  },
  sloCategory: {
    marginBottom: 12
  },
  sloCategoryTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#374151',
    marginBottom: 4
  },
  sloBullet: {
    fontSize: 13,
    color: '#1F2937',
    marginLeft: 8,
    marginBottom: 2
  },
  listItem: {
    fontSize: 13,
    color: '#1F2937',
    marginBottom: 6
  },
  competencyItem: {
    marginBottom: 12,
    paddingLeft: 8
  },
  competencyName: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4
  },
  competencyDescription: {
    fontSize: 12,
    color: '#6B7280',
    lineHeight: 18
  },
  procedureStep: {
    marginBottom: 16,
    backgroundColor: '#F9FAFB',
    padding: 12,
    borderLeftWidth: 3,
    borderLeftColor: '#6366F1'
  },
  procedureTitle: {
    fontSize: 13,
    fontWeight: 'bold',
    color: '#1F2937',
    marginBottom: 8
  },
  procedureContent: {
    fontSize: 13,
    color: '#374151',
    lineHeight: 20
  },
  assessmentContent: {
    fontSize: 13,
    color: '#1F2937',
    lineHeight: 20,
    padding: 8
  },
  emptyState: {
    fontSize: 12,
    color: '#9CA3AF',
    fontStyle: 'italic',
    marginLeft: 8
  },
  footer: {
    marginTop: 32,
    paddingTop: 16,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB'
  },
  signatureSection: {
    marginBottom: 24
  },
  signatureLabel: {
    fontSize: 12,
    color: '#374151',
    marginBottom: 8
  }
});
