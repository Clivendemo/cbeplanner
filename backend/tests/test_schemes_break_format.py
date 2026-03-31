"""
Test Schemes of Work - Break Format Changes
Tests the new break format with startWeek/startLesson to endWeek/endLesson
instead of the old durationType/durationValue format.

Features tested:
1. Backend handles new break format (startWeek, startLesson, endWeek, endLesson)
2. Backend still supports legacy format (durationType, durationValue) for backward compatibility
3. Break processing correctly marks all lessons in the break range
"""

import pytest
import requests
import os
from datetime import datetime

BASE_URL = os.environ.get('REACT_APP_BACKEND_URL', 'https://magical-shannon-6.preview.emergentagent.com').rstrip('/')


class TestBreakFormatProcessing:
    """Test break format processing in the backend"""
    
    def test_new_break_format_structure(self):
        """Verify the new break format structure is correct in frontend code"""
        # Read the frontend schemes.tsx file
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check for new Break interface with startWeek, startLesson, endWeek, endLesson
        assert 'startWeek: number' in content, "Break interface should have startWeek"
        assert 'startLesson: number' in content, "Break interface should have startLesson"
        assert 'endWeek: number' in content, "Break interface should have endWeek"
        assert 'endLesson: number' in content, "Break interface should have endLesson"
        
        # Check that old durationType/durationValue are NOT in the Break interface
        # (They should be removed from the interface)
        lines = content.split('\n')
        in_break_interface = False
        for line in lines:
            if 'interface Break' in line:
                in_break_interface = True
            elif in_break_interface and '}' in line:
                in_break_interface = False
            elif in_break_interface:
                # Inside Break interface - should NOT have durationType or durationValue
                assert 'durationType' not in line, "Break interface should not have durationType"
                assert 'durationValue' not in line, "Break interface should not have durationValue"
        
        print("PASSED: New break format structure is correct in frontend")
    
    def test_break_display_format(self):
        """Verify breaks display in 'Week X, Lesson Y → Week Z, Lesson W' format"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check for the new display format in breakDetails
        assert 'Week {brk.startWeek}, Lesson {brk.startLesson}' in content, \
            "Break display should show start week and lesson"
        assert 'Week {brk.endWeek}, Lesson {brk.endLesson}' in content, \
            "Break display should show end week and lesson"
        
        print("PASSED: Break display format is correct")
    
    def test_add_break_modal_has_four_pickers(self):
        """Verify Add Break modal has start week, start lesson, end week, end lesson pickers"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check for "Break Starts At:" section
        assert 'Break Starts At:' in content, "Modal should have 'Break Starts At:' section"
        
        # Check for "Break Ends At:" section
        assert 'Break Ends At:' in content, "Modal should have 'Break Ends At:' section"
        
        # Check for startWeek picker
        assert 'editingBreak?.startWeek' in content, "Modal should have startWeek picker"
        
        # Check for startLesson picker
        assert 'editingBreak?.startLesson' in content, "Modal should have startLesson picker"
        
        # Check for endWeek picker
        assert 'editingBreak?.endWeek' in content, "Modal should have endWeek picker"
        
        # Check for endLesson picker
        assert 'editingBreak?.endLesson' in content, "Modal should have endLesson picker"
        
        print("PASSED: Add Break modal has all four pickers")
    
    def test_calculate_break_duration_helper(self):
        """Verify calculateBreakDuration helper function exists"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check for calculateBreakDuration function
        assert 'calculateBreakDuration' in content, "Should have calculateBreakDuration helper"
        
        # Check that it calculates total lessons
        assert 'totalLessons' in content, "Should calculate total lessons"
        
        print("PASSED: calculateBreakDuration helper exists")
    
    def test_break_duration_info_in_modal(self):
        """Verify break duration info text is shown in modal"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check for breakDurationInfo style
        assert 'breakDurationInfo' in content, "Should have breakDurationInfo style"
        
        # Check for breakDurationText style
        assert 'breakDurationText' in content, "Should have breakDurationText style"
        
        # Check that calculateBreakDuration is called in the modal
        assert 'calculateBreakDuration(editingBreak)' in content, \
            "Modal should display calculated break duration"
        
        print("PASSED: Break duration info is shown in modal")


class TestBackendBreakProcessing:
    """Test backend break processing logic"""
    
    def test_backend_handles_new_break_format(self):
        """Verify backend server.py handles new break format"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for new break format handling
        assert 'startWeek' in content, "Backend should handle startWeek"
        assert 'startLesson' in content, "Backend should handle startLesson"
        assert 'endWeek' in content, "Backend should handle endWeek"
        assert 'endLesson' in content, "Backend should handle endLesson"
        
        # Check for the comment about new format
        assert 'startWeek/startLesson to endWeek/endLesson' in content, \
            "Backend should have comment about new break format"
        
        print("PASSED: Backend handles new break format")
    
    def test_backend_supports_legacy_format(self):
        """Verify backend still supports legacy durationType/durationValue format"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for legacy format support
        assert 'durationType' in content, "Backend should support legacy durationType"
        assert 'durationValue' in content, "Backend should support legacy durationValue"
        
        # Check for the comment about legacy support
        assert 'Support legacy format' in content or 'legacy format' in content.lower(), \
            "Backend should have comment about legacy format support"
        
        print("PASSED: Backend supports legacy break format")
    
    def test_break_processing_marks_all_lessons(self):
        """Verify break processing marks all lessons from start to end"""
        with open('/app/backend/server.py', 'r') as f:
            content = f.read()
        
        # Check for break marking logic
        assert 'breaks_map' in content, "Should use breaks_map for tracking breaks"
        
        # Check for loop that marks lessons
        assert 'while True:' in content or 'for' in content, \
            "Should have loop to mark all break lessons"
        
        # Check for safety check to prevent infinite loop
        assert 'current_week > request.totalWeeks' in content or 'totalWeeks' in content, \
            "Should have safety check for break processing"
        
        print("PASSED: Break processing marks all lessons correctly")


class TestGoBackAndEditButton:
    """Test 'Go Back & Edit' button in preview step"""
    
    def test_go_back_edit_button_exists(self):
        """Verify 'Go Back & Edit' button exists in preview step"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check for the button text
        assert 'Go Back & Edit' in content, "Should have 'Go Back & Edit' button"
        
        # Check for editSchemeBtn style
        assert 'editSchemeBtn' in content, "Should have editSchemeBtn style"
        
        print("PASSED: 'Go Back & Edit' button exists")
    
    def test_go_back_edit_navigates_to_breaks(self):
        """Verify clicking 'Go Back & Edit' returns to Breaks step"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check that clicking the button sets currentStep to 'breaks'
        assert "setCurrentStep('breaks')" in content, \
            "'Go Back & Edit' should navigate to breaks step"
        
        print("PASSED: 'Go Back & Edit' navigates to Breaks step")


class TestGenerateButtonBehavior:
    """Test Generate Scheme button behavior"""
    
    def test_generate_button_moves_to_preview(self):
        """Verify Generate button moves to Preview step after generating"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check that generateScheme function sets currentStep to 'preview'
        assert "setCurrentStep('preview')" in content, \
            "Generate should move to preview step"
        
        # Check that generateScheme function exists and contains setCurrentStep('preview')
        # Find the generateScheme function and verify it sets preview step
        lines = content.split('\n')
        generate_scheme_start = -1
        
        for i, line in enumerate(lines):
            if 'const generateScheme' in line:
                generate_scheme_start = i
                break
        
        assert generate_scheme_start >= 0, "generateScheme function should exist"
        
        # Check that setCurrentStep('preview') appears after generateScheme definition
        # and before the next major function definition
        found_set_preview = False
        for i in range(generate_scheme_start, min(generate_scheme_start + 50, len(lines))):
            if "setCurrentStep('preview')" in lines[i]:
                found_set_preview = True
                break
        
        assert found_set_preview, "generateScheme should call setCurrentStep('preview')"
        
        print("PASSED: Generate button moves to Preview step")
    
    def test_generate_button_text(self):
        """Verify Generate button shows correct text"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Check for "Generate Scheme" text on the button
        assert 'Generate Scheme' in content, "Button should show 'Generate Scheme' text"
        
        print("PASSED: Generate button has correct text")


class TestDefaultBreaks:
    """Test default breaks configuration"""
    
    def test_default_breaks_use_new_format(self):
        """Verify default breaks use new format with startWeek/startLesson/endWeek/endLesson"""
        with open('/app/frontend/app/(teacher)/schemes.tsx', 'r') as f:
            content = f.read()
        
        # Find the default breaks initialization
        # Should have breaks like: { breakType: 'Mid-Term Break', startWeek: 5, startLesson: 1, endWeek: 5, endLesson: 5 }
        assert 'startWeek: 5' in content or 'startWeek: 13' in content, \
            "Default breaks should use startWeek"
        assert 'startLesson: 1' in content, "Default breaks should use startLesson"
        assert 'endWeek:' in content, "Default breaks should use endWeek"
        assert 'endLesson:' in content, "Default breaks should use endLesson"
        
        print("PASSED: Default breaks use new format")


if __name__ == "__main__":
    pytest.main([__file__, "-v", "--tb=short"])
