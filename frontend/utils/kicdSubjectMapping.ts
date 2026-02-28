/**
 * KICD CBC Subject Mapping - Single Source of Truth
 * 
 * This file contains the official KICD subject lists for each grade band.
 * Used to filter subjects shown in the dropdown based on selected grade.
 * 
 * NO DATABASE CHANGES - filtering happens purely in frontend code.
 */

// Grade band definitions
export type GradeBand = 'lower_primary' | 'upper_primary' | 'junior_secondary' | 'senior_school';

// KICD Subject Lists by Grade Band
export const KICD_SUBJECTS_BY_BAND: Record<GradeBand, string[]> = {
  // Grades 1-3 (Lower Primary)
  lower_primary: [
    'Literacy',
    'Literacy Activities',
    'Kiswahili Language Activities',
    'Kenya Sign Language',
    'English Language Activities',
    'Indigenous Language Activities',
    'Mathematical Activities',
    'Environmental Activities',
    'Hygiene and Nutrition Activities',
    'Religious Education Activities',
    'Movement and Creative Activities'
  ],

  // Grades 4-6 (Upper Primary)
  upper_primary: [
    'English',
    'Kiswahili',
    'Mathematics',
    'Science & Technology',
    'Science and Technology',
    'Social Studies',
    'Creative Arts',
    'Agriculture',
    'Religious Education',
    'Christian Religious Education',
    'CRE',
    'Islamic Religious Education',
    'IRE',
    'Hindu Religious Education',
    'HRE',
    'Indigenous Language',
    'Indigenous Language Activities',
    'Arabic',
    'French',
    'German',
    'Mandarin',
    'Mandarin Chinese'
  ],

  // Grades 7-9 (Junior Secondary)
  junior_secondary: [
    'English',
    'Kiswahili',
    'Mathematics',
    'Integrated Science',
    'Social Studies',
    'Pre-Technical Studies',
    'Creative Arts',
    'Agriculture',
    'Religious Education',
    'Christian Religious Education',
    'CRE',
    'Islamic Religious Education',
    'IRE',
    'Hindu Religious Education',
    'HRE',
    'Indigenous Language',
    'Indigenous Language Activities',
    'Arabic',
    'French',
    'German',
    'Mandarin',
    'Mandarin Chinese'
  ],

  // Grades 10-12 (Senior School)
  senior_school: [
    'English',
    'Kiswahili',
    'Kiswahili / KSL',
    'Kiswahili Lugha',
    'Fasihi ya Kiswahili',
    'Community Service Learning',
    'Community Service Learning (CSL)',
    'CSL',
    'Physical Education',
    'Physical Education (PE)',
    'PE',
    'ICT Skills',
    'ICT',
    'Computer Studies',
    'Core Mathematics',
    'Essential Mathematics',
    'Mathematics',
    'Biology',
    'Chemistry',
    'Physics',
    'General Science',
    'Agriculture',
    'Home Science',
    'Drawing & Design',
    'Drawing and Design',
    'Aviation Technology',
    'Building & Construction',
    'Building and Construction',
    'Building Construction',
    'Electricity',
    'Electrical Technology',
    'Metalwork',
    'Power Mechanic',
    'Power Mechanics',
    'Woodwork',
    'Media Technology',
    'Marine & Fisheries Technology',
    'Marine and Fisheries Technology',
    'Literature in English',
    'Indigenous Language',
    'Indigenous Language Activities',
    'Kenya Sign Language',
    'KSL',
    'Arabic',
    'French',
    'German',
    'Mandarin',
    'Mandarin Chinese',
    'History & Citizenship',
    'History and Citizenship',
    'Geography',
    'Christian Religious Education',
    'CRE',
    'Islamic Religious Education',
    'IRE',
    'Hindu Religious Education',
    'HRE',
    'Business Studies',
    'Sports & Recreation',
    'Sports and Recreation',
    'Music & Dance',
    'Music and Dance',
    'Theatre & Film',
    'Theatre and Film',
    'Fine Arts'
  ]
};

/**
 * Get the grade band for a given grade number or name
 */
export function getGradeBand(gradeInput: string | number): GradeBand | null {
  let gradeNum: number;

  if (typeof gradeInput === 'number') {
    gradeNum = gradeInput;
  } else {
    // Extract number from grade name (e.g., "Grade 5" -> 5)
    const match = gradeInput.match(/(\d+)/);
    if (!match) return null;
    gradeNum = parseInt(match[1], 10);
  }

  if (gradeNum >= 1 && gradeNum <= 3) return 'lower_primary';
  if (gradeNum >= 4 && gradeNum <= 6) return 'upper_primary';
  if (gradeNum >= 7 && gradeNum <= 9) return 'junior_secondary';
  if (gradeNum >= 10 && gradeNum <= 12) return 'senior_school';

  return null;
}

/**
 * Get KICD subjects for a given grade
 */
export function getKicdSubjectsForGrade(gradeInput: string | number): string[] {
  const band = getGradeBand(gradeInput);
  if (!band) return [];
  return KICD_SUBJECTS_BY_BAND[band];
}

/**
 * Normalize subject name for comparison
 * Handles: case differences, & vs "and", extra spaces, punctuation
 */
export function normalizeSubjectName(name: string): string {
  return name
    .toLowerCase()
    .trim()
    .replace(/\s+/g, ' ')           // Multiple spaces to single
    .replace(/&/g, 'and')           // & to "and"
    .replace(/[()]/g, '')           // Remove parentheses
    .replace(/[/:]/g, ' ')          // Replace / and : with space
    .replace(/\s+/g, ' ')           // Clean up spaces again
    .trim();
}

/**
 * Check if a database subject matches any KICD subject for the grade
 */
export function isSubjectValidForGrade(
  dbSubjectName: string,
  gradeInput: string | number
): boolean {
  const kicdSubjects = getKicdSubjectsForGrade(gradeInput);
  if (kicdSubjects.length === 0) return true; // No filtering if grade not recognized

  const normalizedDbName = normalizeSubjectName(dbSubjectName);

  return kicdSubjects.some(kicdSubject => {
    const normalizedKicd = normalizeSubjectName(kicdSubject);
    
    // Exact match after normalization
    if (normalizedDbName === normalizedKicd) return true;
    
    // Check if one contains the other (for partial matches)
    if (normalizedDbName.includes(normalizedKicd) || normalizedKicd.includes(normalizedDbName)) {
      return true;
    }

    // Special case mappings
    const specialMappings: Record<string, string[]> = {
      'cre': ['christian religious education', 'cre'],
      'ire': ['islamic religious education', 'ire'],
      'hre': ['hindu religious education', 'hre'],
      'csl': ['community service learning', 'csl'],
      'pe': ['physical education', 'pe'],
      'ict': ['ict skills', 'ict', 'computer studies'],
      'ksl': ['kenya sign language', 'ksl', 'kiswahili ksl'],
    };

    for (const [key, aliases] of Object.entries(specialMappings)) {
      if (aliases.includes(normalizedDbName) && aliases.includes(normalizedKicd)) {
        return true;
      }
    }

    return false;
  });
}

/**
 * Filter subjects array based on grade
 * Returns only subjects that match the KICD list for that grade band
 */
export function filterSubjectsByGrade(
  subjects: Array<{ id: string; name: string; [key: string]: any }>,
  gradeInput: string | number
): Array<{ id: string; name: string; [key: string]: any }> {
  const band = getGradeBand(gradeInput);
  
  // If grade not recognized, return all subjects
  if (!band) {
    console.warn('[KICD] Grade not recognized, showing all subjects:', gradeInput);
    return subjects;
  }

  const filtered = subjects.filter(subject => 
    isSubjectValidForGrade(subject.name, gradeInput)
  );

  console.log(`[KICD] Grade ${gradeInput} (${band}): ${filtered.length}/${subjects.length} subjects match`);
  
  // Log which subjects were filtered out (for debugging)
  const filteredOut = subjects.filter(s => !filtered.includes(s));
  if (filteredOut.length > 0) {
    console.log('[KICD] Filtered out:', filteredOut.map(s => s.name).join(', '));
  }

  return filtered;
}

/**
 * Get grade band display name
 */
export function getGradeBandDisplayName(band: GradeBand): string {
  const names: Record<GradeBand, string> = {
    lower_primary: 'Lower Primary (Grades 1-3)',
    upper_primary: 'Upper Primary (Grades 4-6)',
    junior_secondary: 'Junior Secondary (Grades 7-9)',
    senior_school: 'Senior School (Grades 10-12)'
  };
  return names[band];
}
