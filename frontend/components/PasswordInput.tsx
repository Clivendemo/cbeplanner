/**
 * Reusable password input with a show/hide eye toggle.
 *
 * Thin wrapper around React Native's TextInput — pass through any TextInput
 * prop; pass your style on `inputStyle` (applied to the inner TextInput) and
 * `containerStyle` (applied to the outer row).
 *
 * Forwards its ref to the inner TextInput so focus() works in focus chains.
 */
import React, { forwardRef, useState } from 'react';
import { View, TextInput, TouchableOpacity, StyleSheet, TextInputProps, ViewStyle, TextStyle, StyleProp } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface PasswordInputProps extends Omit<TextInputProps, 'secureTextEntry' | 'style'> {
  containerStyle?: StyleProp<ViewStyle>;
  inputStyle?: StyleProp<TextStyle>;
  iconColor?: string;
  testIDPrefix?: string;
}

export const PasswordInput = forwardRef<TextInput, PasswordInputProps>(({
  containerStyle,
  inputStyle,
  iconColor = '#6B7280',
  testIDPrefix = 'password',
  testID,
  ...textInputProps
}, ref) => {
  const [visible, setVisible] = useState(false);
  return (
    <View style={[styles.row, containerStyle]}>
      <TextInput
        ref={ref}
        {...textInputProps}
        testID={testID || `${testIDPrefix}-input`}
        secureTextEntry={!visible}
        style={[styles.input, inputStyle]}
      />
      <TouchableOpacity
        accessibilityRole="button"
        accessibilityLabel={visible ? 'Hide password' : 'Show password'}
        onPress={() => setVisible((v) => !v)}
        hitSlop={{ top: 10, bottom: 10, left: 10, right: 10 }}
        style={styles.toggleBtn}
        testID={`${testIDPrefix}-toggle`}
      >
        <Ionicons
          name={visible ? 'eye-off-outline' : 'eye-outline'}
          size={20}
          color={iconColor}
        />
      </TouchableOpacity>
    </View>
  );
});

PasswordInput.displayName = 'PasswordInput';

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
    flex: 1,
    minWidth: 0,
  },
  input: {
    flex: 1,
    minWidth: 0,
  },
  toggleBtn: {
    paddingHorizontal: 8,
    paddingVertical: 6,
    alignItems: 'center',
    justifyContent: 'center',
    minWidth: 36,
  },
});

export default PasswordInput;
