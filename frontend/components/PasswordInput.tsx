/**
 * Reusable password input with a show/hide eye toggle.
 *
 * Thin wrapper around React Native's TextInput — pass through any TextInput
 * prop; pass your style on `inputStyle` (applied to the inner TextInput) and
 * `containerStyle` (applied to the outer row).
 *
 * Used in login, signup, and reset-password screens.
 */
import React, { useState } from 'react';
import { View, TextInput, Pressable, StyleSheet, TextInputProps, ViewStyle, TextStyle, StyleProp } from 'react-native';
import { Ionicons } from '@expo/vector-icons';

interface PasswordInputProps extends Omit<TextInputProps, 'secureTextEntry' | 'style'> {
  containerStyle?: StyleProp<ViewStyle>;
  inputStyle?: StyleProp<TextStyle>;
  iconColor?: string;
  testIDPrefix?: string;
}

export const PasswordInput: React.FC<PasswordInputProps> = ({
  containerStyle,
  inputStyle,
  iconColor = '#6B7280',
  testIDPrefix = 'password',
  ...textInputProps
}) => {
  const [visible, setVisible] = useState(false);
  return (
    <View style={[styles.row, containerStyle]}>
      <TextInput
        {...textInputProps}
        secureTextEntry={!visible}
        style={[styles.input, inputStyle]}
        data-testid={`${testIDPrefix}-input`}
      />
      <Pressable
        accessibilityRole="button"
        accessibilityLabel={visible ? 'Hide password' : 'Show password'}
        onPress={() => setVisible((v) => !v)}
        hitSlop={10}
        style={styles.toggleBtn}
        data-testid={`${testIDPrefix}-toggle`}
      >
        <Ionicons
          name={visible ? 'eye-off-outline' : 'eye-outline'}
          size={20}
          color={iconColor}
        />
      </Pressable>
    </View>
  );
};

const styles = StyleSheet.create({
  row: {
    flexDirection: 'row',
    alignItems: 'center',
  },
  input: {
    flex: 1,
    minWidth: 0,
  },
  toggleBtn: {
    paddingHorizontal: 12,
    paddingVertical: 8,
    justifyContent: 'center',
  },
});

export default PasswordInput;
