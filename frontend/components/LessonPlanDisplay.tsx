import React from 'react';
import { View, Text, StyleSheet, ScrollView } from 'react-native';

interface LessonPlanDisplayProps {
  lessonPlan: any;
}

export const LessonPlanDisplay: React.FC<LessonPlanDisplayProps> = ({ lessonPlan }) => {
  // Table cell component with borders
  const TableCell = ({ children, isHeader = false, colSpan = 1, width = '50%' }: { 
    children: React.ReactNode; 
    isHeader?: boolean; 
    colSpan?: number;
    width?: string;
  }) => (
    <View style={[
      styles.tableCell, 
      isHeader && styles.headerCell,
      { width: colSpan === 2 ? '100%' : width }
    ]}>
      {typeof children === 'string' ? (
        <Text style={[styles.cellText, isHeader && styles.headerText]}>{children}</Text>
      ) : children}
    </View>
  );

  // Table row component
  const TableRow = ({ children }: { children: React.ReactNode }) => (
    <View style={styles.tableRow}>{children}</View>
  );

  // Full width header row
  const HeaderRow = ({ title }: { title: string }) => (
    <TableRow>
      <TableCell isHeader colSpan={2}>{title}</TableCell>
    </TableRow>
  );

  // Label-value row
  const DataRow = ({ label, value }: { label: string; value: string }) => (
    <TableRow>
      <TableCell width="35%">
        <Text style={styles.labelText}>{label}</Text>
      </TableCell>
      <TableCell width="65%">
        <Text style={styles.valueText}>{value || 'N/A'}</Text>
      </TableCell>
    </TableRow>
  );

  return (
    <ScrollView style={styles.container}>
      {/* Document Header */}
      <View style={styles.documentHeader}>
        <Text style={styles.documentTitle}>REPUBLIC OF KENYA</Text>
        <Text style={styles.documentSubtitle}>COMPETENCY-BASED CURRICULUM</Text>
        <Text style={styles.documentType}>LESSON PLAN</Text>
      </View>

      {/* Main Table Container */}
      <View style={styles.tableContainer}>
        
        {/* Section 1: Teacher & School Information */}
        <HeaderRow title="TEACHER & SCHOOL INFORMATION" />
        <DataRow label="Teacher's Name" value={lessonPlan.teacherName} />
        <DataRow label="School Name" value={lessonPlan.schoolName} />
        <DataRow label="Date" value={new Date().toLocaleDateString('en-GB', { 
          day: '2-digit', month: 'long', year: 'numeric' 
        })} />

        {/* Section 2: Lesson Details */}
        <HeaderRow title="LESSON DETAILS" />
        <DataRow label="Grade/Class" value={lessonPlan.gradeName} />
        <DataRow label="Learning Area/Subject" value={lessonPlan.subjectName} />
        <DataRow label="Strand" value={lessonPlan.strandName} />
        <DataRow label="Sub-Strand" value={lessonPlan.substrandName} />
        <DataRow label="Lesson Duration" value={`${lessonPlan.duration} Minutes`} />
        <DataRow label="Number of Learners" value="As per class" />

        {/* Section 3: Specific Learning Outcomes */}
        <HeaderRow title="SPECIFIC LEARNING OUTCOMES (SLOs)" />
        <TableRow>
          <TableCell colSpan={2}>
            <View style={styles.sloContainer}>
              <Text style={styles.sloTitle}>By the end of the lesson, the learner should be able to:</Text>
              <Text style={styles.sloMain}>{lessonPlan.sloName}</Text>
              {lessonPlan.sloDescription && (
                <Text style={styles.sloDescription}>{lessonPlan.sloDescription}</Text>
              )}
            </View>
          </TableCell>
        </TableRow>

        {/* SLO Domains Table */}
        <TableRow>
          <View style={[styles.tableCell, styles.domainCell, { width: '33.33%' }]}>
            <Text style={styles.domainHeader}>KNOWLEDGE</Text>
            {lessonPlan.knowledge?.map((item: string, i: number) => (
              <Text key={i} style={styles.domainItem}>• {item}</Text>
            )) || <Text style={styles.emptyText}>-</Text>}
          </View>
          <View style={[styles.tableCell, styles.domainCell, { width: '33.33%' }]}>
            <Text style={styles.domainHeader}>SKILLS</Text>
            {lessonPlan.skills?.map((item: string, i: number) => (
              <Text key={i} style={styles.domainItem}>• {item}</Text>
            )) || <Text style={styles.emptyText}>-</Text>}
          </View>
          <View style={[styles.tableCell, styles.domainCell, { width: '33.34%' }]}>
            <Text style={styles.domainHeader}>ATTITUDES</Text>
            {lessonPlan.attitudes?.map((item: string, i: number) => (
              <Text key={i} style={styles.domainItem}>• {item}</Text>
            )) || <Text style={styles.emptyText}>-</Text>}
          </View>
        </TableRow>

        {/* Section 4: Key Inquiry Questions */}
        <HeaderRow title="KEY INQUIRY QUESTION(S)" />
        <TableRow>
          <TableCell colSpan={2}>
            <Text style={styles.inquiryText}>
              • What do you understand by {lessonPlan.substrandName}?{'\n'}
              • How can we apply {lessonPlan.sloName?.toLowerCase()} in real life?{'\n'}
              • Why is it important to learn about {lessonPlan.strandName}?
            </Text>
          </TableCell>
        </TableRow>

        {/* Section 5: Learning Resources */}
        <HeaderRow title="LEARNING RESOURCES" />
        <TableRow>
          <TableCell colSpan={2}>
            <View style={styles.resourcesContainer}>
              {lessonPlan.learningResources?.length > 0 ? (
                lessonPlan.learningResources.map((resource: string, i: number) => (
                  <Text key={i} style={styles.resourceItem}>• {resource}</Text>
                ))
              ) : (
                <Text style={styles.resourceItem}>• Textbooks, Charts, Real objects, Digital resources</Text>
              )}
            </View>
          </TableCell>
        </TableRow>

        {/* Section 6: Core Competencies & Values */}
        <HeaderRow title="CORE COMPETENCIES TO BE DEVELOPED" />
        <TableRow>
          <TableCell colSpan={2}>
            <View style={styles.competenciesContainer}>
              {lessonPlan.competencies?.length > 0 ? (
                lessonPlan.competencies.map((comp: any, i: number) => (
                  <View key={i} style={styles.competencyRow}>
                    <Text style={styles.competencyName}>✓ {comp.name}</Text>
                    <Text style={styles.competencyDesc}>{comp.description}</Text>
                  </View>
                ))
              ) : (
                <Text style={styles.emptyText}>Communication, Critical Thinking, Collaboration</Text>
              )}
            </View>
          </TableCell>
        </TableRow>

        <HeaderRow title="CORE VALUES TO BE DEVELOPED" />
        <TableRow>
          <TableCell colSpan={2}>
            <View style={styles.valuesContainer}>
              {lessonPlan.values?.length > 0 ? (
                lessonPlan.values.map((value: any, i: number) => (
                  <View key={i} style={styles.valueRow}>
                    <Text style={styles.valueName}>✓ {value.name}</Text>
                    <Text style={styles.valueDesc}>{value.description}</Text>
                  </View>
                ))
              ) : (
                <Text style={styles.emptyText}>Responsibility, Respect, Integrity</Text>
              )}
            </View>
          </TableCell>
        </TableRow>

        {/* Section 7: PCIs */}
        {lessonPlan.pcis && lessonPlan.pcis.length > 0 && (
          <>
            <HeaderRow title="PERTINENT & CONTEMPORARY ISSUES (PCIs)" />
            <TableRow>
              <TableCell colSpan={2}>
                <View style={styles.pcisContainer}>
                  {lessonPlan.pcis.map((pci: any, i: number) => (
                    <Text key={i} style={styles.pciItem}>• {pci.name}: {pci.description}</Text>
                  ))}
                </View>
              </TableCell>
            </TableRow>
          </>
        )}

        {/* Section 8: Lesson Procedure - Main Table */}
        <HeaderRow title="LESSON PROCEDURE / LEARNING ACTIVITIES" />
        
        {/* Procedure Table Header */}
        <TableRow>
          <View style={[styles.tableCell, styles.procedureHeader, { width: '15%' }]}>
            <Text style={styles.procedureHeaderText}>STAGE</Text>
          </View>
          <View style={[styles.tableCell, styles.procedureHeader, { width: '15%' }]}>
            <Text style={styles.procedureHeaderText}>TIME</Text>
          </View>
          <View style={[styles.tableCell, styles.procedureHeader, { width: '35%' }]}>
            <Text style={styles.procedureHeaderText}>TEACHER'S ACTIVITIES</Text>
          </View>
          <View style={[styles.tableCell, styles.procedureHeader, { width: '35%' }]}>
            <Text style={styles.procedureHeaderText}>LEARNER'S ACTIVITIES</Text>
          </View>
        </TableRow>

        {/* Introduction Row */}
        <TableRow>
          <View style={[styles.tableCell, styles.stageCell, { width: '15%' }]}>
            <Text style={styles.stageText}>Introduction</Text>
          </View>
          <View style={[styles.tableCell, { width: '15%' }]}>
            <Text style={styles.timeText}>
              {lessonPlan.duration <= 40 ? '5 min' : lessonPlan.duration <= 60 ? '7 min' : '10 min'}
            </Text>
          </View>
          <View style={[styles.tableCell, { width: '35%' }]}>
            <Text style={styles.activityText}>{lessonPlan.introduction || 'Teacher introduces the topic and activates prior knowledge.'}</Text>
          </View>
          <View style={[styles.tableCell, { width: '35%' }]}>
            <Text style={styles.activityText}>• Learners listen attentively{'\n'}• Share prior knowledge{'\n'}• Ask clarifying questions</Text>
          </View>
        </TableRow>

        {/* Lesson Development Row */}
        <TableRow>
          <View style={[styles.tableCell, styles.stageCell, { width: '15%' }]}>
            <Text style={styles.stageText}>Lesson Development</Text>
          </View>
          <View style={[styles.tableCell, { width: '15%' }]}>
            <Text style={styles.timeText}>
              {lessonPlan.duration <= 40 ? `${lessonPlan.duration - 15} min` : lessonPlan.duration <= 60 ? `${Math.floor((lessonPlan.duration - 20) * 0.6)} min` : `${Math.floor((lessonPlan.duration - 25) * 0.45)} min`}
            </Text>
          </View>
          <View style={[styles.tableCell, { width: '35%' }]}>
            <Text style={styles.activityText}>{lessonPlan.lessonDevelopment || 'Teacher explains concepts with examples and guides activities.'}</Text>
          </View>
          <View style={[styles.tableCell, { width: '35%' }]}>
            <Text style={styles.activityText}>• Participate in discussions{'\n'}• Take notes{'\n'}• Practice with exercises{'\n'}• Work in groups</Text>
          </View>
        </TableRow>

        {/* Extended Activity Row (if applicable) */}
        {lessonPlan.extendedActivity && (
          <TableRow>
            <View style={[styles.tableCell, styles.stageCell, { width: '15%' }]}>
              <Text style={styles.stageText}>Extended Activity</Text>
            </View>
            <View style={[styles.tableCell, { width: '15%' }]}>
              <Text style={styles.timeText}>
                {Math.floor((lessonPlan.duration - 25) * 0.35)} min
              </Text>
            </View>
            <View style={[styles.tableCell, { width: '35%' }]}>
              <Text style={styles.activityText}>{lessonPlan.extendedActivity}</Text>
            </View>
            <View style={[styles.tableCell, { width: '35%' }]}>
              <Text style={styles.activityText}>• Work on extended tasks{'\n'}• Present findings{'\n'}• Peer collaboration</Text>
            </View>
          </TableRow>
        )}

        {/* Conclusion Row */}
        <TableRow>
          <View style={[styles.tableCell, styles.stageCell, { width: '15%' }]}>
            <Text style={styles.stageText}>Conclusion</Text>
          </View>
          <View style={[styles.tableCell, { width: '15%' }]}>
            <Text style={styles.timeText}>
              {lessonPlan.duration <= 40 ? '5 min' : lessonPlan.duration <= 60 ? '8 min' : '10 min'}
            </Text>
          </View>
          <View style={[styles.tableCell, { width: '35%' }]}>
            <Text style={styles.activityText}>{lessonPlan.conclusion || 'Teacher summarizes key points and checks understanding.'}</Text>
          </View>
          <View style={[styles.tableCell, { width: '35%' }]}>
            <Text style={styles.activityText}>• Summarize learning{'\n'}• Ask questions{'\n'}• Reflect on lesson</Text>
          </View>
        </TableRow>

        {/* Section 9: Assessment */}
        <HeaderRow title="ASSESSMENT" />
        <TableRow>
          <View style={[styles.tableCell, { width: '30%' }]}>
            <Text style={styles.labelText}>Assessment Methods</Text>
          </View>
          <View style={[styles.tableCell, { width: '70%' }]}>
            <Text style={styles.assessmentText}>{lessonPlan.assessment || 'Oral questions, Observation, Written exercises'}</Text>
          </View>
        </TableRow>

        {/* Section 10: Reflection */}
        <HeaderRow title="TEACHER'S REFLECTION" />
        <TableRow>
          <TableCell colSpan={2}>
            <View style={styles.reflectionContainer}>
              <Text style={styles.reflectionLabel}>What went well:</Text>
              <View style={styles.reflectionLine} />
              <View style={styles.reflectionLine} />
              <Text style={styles.reflectionLabel}>Areas for improvement:</Text>
              <View style={styles.reflectionLine} />
              <View style={styles.reflectionLine} />
            </View>
          </TableCell>
        </TableRow>

        {/* Signatures Section */}
        <HeaderRow title="VERIFICATION" />
        <TableRow>
          <View style={[styles.tableCell, { width: '50%' }]}>
            <View style={styles.signatureBox}>
              <Text style={styles.signatureLabel}>Teacher's Signature:</Text>
              <View style={styles.signatureLine} />
              <Text style={styles.signatureLabel}>Date:</Text>
              <View style={styles.signatureLine} />
            </View>
          </View>
          <View style={[styles.tableCell, { width: '50%' }]}>
            <View style={styles.signatureBox}>
              <Text style={styles.signatureLabel}>HOD/Deputy's Signature:</Text>
              <View style={styles.signatureLine} />
              <Text style={styles.signatureLabel}>Date:</Text>
              <View style={styles.signatureLine} />
            </View>
          </View>
        </TableRow>

      </View>

      {/* Footer */}
      <View style={styles.footer}>
        <Text style={styles.footerText}>Generated by CBE Planner | KICD-Aligned Competency Based Curriculum</Text>
        <Text style={styles.footerText}>© {new Date().getFullYear()} Republic of Kenya - Ministry of Education</Text>
      </View>
    </ScrollView>
  );
};

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#FFFFFF',
    padding: 12
  },
  documentHeader: {
    alignItems: 'center',
    paddingVertical: 16,
    borderWidth: 2,
    borderColor: '#1F2937',
    marginBottom: 12,
    backgroundColor: '#F8FAFC'
  },
  documentTitle: {
    fontSize: 16,
    fontWeight: 'bold',
    color: '#1F2937',
    letterSpacing: 1
  },
  documentSubtitle: {
    fontSize: 14,
    fontWeight: 'bold',
    color: '#374151',
    marginTop: 4
  },
  documentType: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#1F2937',
    marginTop: 8,
    textDecorationLine: 'underline'
  },
  tableContainer: {
    borderWidth: 2,
    borderColor: '#1F2937'
  },
  tableRow: {
    flexDirection: 'row',
    borderBottomWidth: 1,
    borderBottomColor: '#1F2937'
  },
  tableCell: {
    borderRightWidth: 1,
    borderRightColor: '#1F2937',
    padding: 10,
    justifyContent: 'center'
  },
  headerCell: {
    backgroundColor: '#1E3A5F',
    padding: 12
  },
  cellText: {
    fontSize: 13,
    color: '#1F2937'
  },
  headerText: {
    color: '#FFFFFF',
    fontWeight: 'bold',
    fontSize: 13,
    textAlign: 'center'
  },
  labelText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#374151'
  },
  valueText: {
    fontSize: 12,
    color: '#1F2937'
  },
  sloContainer: {
    padding: 4
  },
  sloTitle: {
    fontSize: 12,
    fontStyle: 'italic',
    color: '#4B5563',
    marginBottom: 8
  },
  sloMain: {
    fontSize: 13,
    fontWeight: '600',
    color: '#1F2937',
    marginBottom: 4
  },
  sloDescription: {
    fontSize: 12,
    color: '#4B5563',
    lineHeight: 18
  },
  domainCell: {
    backgroundColor: '#F1F5F9',
    borderRightWidth: 1,
    borderRightColor: '#1F2937'
  },
  domainHeader: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#1E3A5F',
    marginBottom: 8,
    textAlign: 'center',
    textDecorationLine: 'underline'
  },
  domainItem: {
    fontSize: 11,
    color: '#374151',
    marginBottom: 4,
    lineHeight: 16
  },
  emptyText: {
    fontSize: 11,
    color: '#9CA3AF',
    fontStyle: 'italic'
  },
  inquiryText: {
    fontSize: 12,
    color: '#374151',
    lineHeight: 20
  },
  resourcesContainer: {
    padding: 4
  },
  resourceItem: {
    fontSize: 12,
    color: '#374151',
    marginBottom: 4
  },
  competenciesContainer: {
    padding: 4
  },
  competencyRow: {
    marginBottom: 8
  },
  competencyName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1F2937'
  },
  competencyDesc: {
    fontSize: 11,
    color: '#4B5563',
    marginLeft: 16
  },
  valuesContainer: {
    padding: 4
  },
  valueRow: {
    marginBottom: 8
  },
  valueName: {
    fontSize: 12,
    fontWeight: '600',
    color: '#1F2937'
  },
  valueDesc: {
    fontSize: 11,
    color: '#4B5563',
    marginLeft: 16
  },
  pcisContainer: {
    padding: 4
  },
  pciItem: {
    fontSize: 12,
    color: '#374151',
    marginBottom: 4,
    lineHeight: 18
  },
  procedureHeader: {
    backgroundColor: '#E2E8F0',
    padding: 8
  },
  procedureHeaderText: {
    fontSize: 11,
    fontWeight: 'bold',
    color: '#1E3A5F',
    textAlign: 'center'
  },
  stageCell: {
    backgroundColor: '#F1F5F9'
  },
  stageText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#1E3A5F',
    textAlign: 'center'
  },
  timeText: {
    fontSize: 11,
    color: '#374151',
    textAlign: 'center'
  },
  activityText: {
    fontSize: 11,
    color: '#374151',
    lineHeight: 16
  },
  assessmentText: {
    fontSize: 12,
    color: '#374151',
    lineHeight: 18
  },
  reflectionContainer: {
    padding: 8
  },
  reflectionLabel: {
    fontSize: 11,
    fontWeight: '600',
    color: '#374151',
    marginTop: 8,
    marginBottom: 4
  },
  reflectionLine: {
    borderBottomWidth: 1,
    borderBottomColor: '#9CA3AF',
    height: 24
  },
  signatureBox: {
    padding: 8
  },
  signatureLabel: {
    fontSize: 11,
    color: '#374151',
    marginBottom: 4
  },
  signatureLine: {
    borderBottomWidth: 1,
    borderBottomColor: '#374151',
    marginBottom: 12,
    height: 20
  },
  footer: {
    marginTop: 16,
    alignItems: 'center',
    paddingVertical: 12,
    borderTopWidth: 1,
    borderTopColor: '#E5E7EB'
  },
  footerText: {
    fontSize: 10,
    color: '#6B7280',
    marginBottom: 2
  }
});
