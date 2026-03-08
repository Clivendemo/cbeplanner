import React from 'react';
import {
  View,
  Text,
  Modal,
  TouchableOpacity,
  StyleSheet,
  Dimensions
} from 'react-native';
import { Ionicons } from '@expo/vector-icons';
import { BlurView } from 'expo-blur';

interface WalletCreditsPopupProps {
  visible: boolean;
  currentBalance: number;
  freeLessonsRemaining: number;
  onAddCredits: () => void;
  onClose: () => void;
}

export const WalletCreditsPopup: React.FC<WalletCreditsPopupProps> = ({
  visible,
  currentBalance,
  freeLessonsRemaining,
  onAddCredits,
  onClose
}) => {
  // Calculate total available credits
  const totalCredits = freeLessonsRemaining > 0 
    ? freeLessonsRemaining 
    : Math.floor(currentBalance / 2); // KES 2 per lesson

  return (
    <Modal
      visible={visible}
      transparent={true}
      animationType="fade"
      onRequestClose={onClose}
    >
      <View style={styles.overlay}>
        <View style={styles.popupContainer}>
          {/* Decorative Header */}
          <View style={styles.headerDecoration}>
            <View style={styles.iconCircle}>
              <Ionicons name="wallet-outline" size={40} color="#6366F1" />
            </View>
          </View>

          {/* Content */}
          <View style={styles.content}>
            {/* Title */}
            <Text style={styles.title}>You're Almost There!</Text>

            {/* Message */}
            <Text style={styles.message}>
              It looks like your wallet credits have been used up.{'\n'}
              Top up your wallet to continue generating lesson plans and keep your teaching workflow running smoothly.
            </Text>

            {/* Balance Display */}
            <View style={styles.balanceCard}>
              <Ionicons name="information-circle" size={20} color="#6366F1" />
              <Text style={styles.balanceText}>
                Current Balance: {freeLessonsRemaining > 0 
                  ? `${freeLessonsRemaining} free lesson${freeLessonsRemaining !== 1 ? 's' : ''}`
                  : `KES ${currentBalance.toFixed(0)}`
                }
              </Text>
            </View>

            {/* Encouragement */}
            <Text style={styles.encouragement}>
              Add more credits now and continue creating high-quality lesson plans in seconds.
            </Text>

            {/* Buttons */}
            <View style={styles.buttonContainer}>
              <TouchableOpacity
                style={styles.primaryButton}
                onPress={onAddCredits}
                activeOpacity={0.8}
                data-testid="add-credits-btn"
              >
                <Ionicons name="add-circle" size={20} color="#FFFFFF" />
                <Text style={styles.primaryButtonText}>Add Credits</Text>
              </TouchableOpacity>

              <TouchableOpacity
                style={styles.secondaryButton}
                onPress={onClose}
                activeOpacity={0.8}
                data-testid="maybe-later-btn"
              >
                <Text style={styles.secondaryButtonText}>Maybe Later</Text>
              </TouchableOpacity>
            </View>
          </View>

          {/* Decorative sparkles */}
          <View style={[styles.sparkle, styles.sparkle1]}>
            <Ionicons name="sparkles" size={16} color="#F59E0B" />
          </View>
          <View style={[styles.sparkle, styles.sparkle2]}>
            <Ionicons name="star" size={14} color="#10B981" />
          </View>
          <View style={[styles.sparkle, styles.sparkle3]}>
            <Ionicons name="heart" size={12} color="#EC4899" />
          </View>
        </View>
      </View>
    </Modal>
  );
};

const { width } = Dimensions.get('window');
const popupWidth = Math.min(width * 0.9, 400);

const styles = StyleSheet.create({
  overlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'center',
    alignItems: 'center',
    padding: 20
  },
  popupContainer: {
    width: popupWidth,
    backgroundColor: '#FFFFFF',
    borderRadius: 24,
    overflow: 'hidden',
    shadowColor: '#000',
    shadowOffset: { width: 0, height: 10 },
    shadowOpacity: 0.25,
    shadowRadius: 20,
    elevation: 10,
    position: 'relative'
  },
  headerDecoration: {
    backgroundColor: '#EEF2FF',
    paddingVertical: 30,
    alignItems: 'center',
    borderBottomLeftRadius: 50,
    borderBottomRightRadius: 50
  },
  iconCircle: {
    width: 80,
    height: 80,
    borderRadius: 40,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.2,
    shadowRadius: 8,
    elevation: 5
  },
  content: {
    padding: 24,
    alignItems: 'center'
  },
  title: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827',
    textAlign: 'center',
    marginBottom: 12
  },
  message: {
    fontSize: 15,
    color: '#4B5563',
    textAlign: 'center',
    lineHeight: 22,
    marginBottom: 16
  },
  balanceCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F3F4F6',
    paddingVertical: 12,
    paddingHorizontal: 20,
    borderRadius: 12,
    marginBottom: 16,
    gap: 8
  },
  balanceText: {
    fontSize: 15,
    fontWeight: '600',
    color: '#374151'
  },
  encouragement: {
    fontSize: 14,
    color: '#6366F1',
    textAlign: 'center',
    fontStyle: 'italic',
    marginBottom: 24,
    paddingHorizontal: 10
  },
  buttonContainer: {
    width: '100%',
    gap: 12
  },
  primaryButton: {
    flexDirection: 'row',
    backgroundColor: '#6366F1',
    paddingVertical: 16,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    gap: 8,
    shadowColor: '#6366F1',
    shadowOffset: { width: 0, height: 4 },
    shadowOpacity: 0.3,
    shadowRadius: 8,
    elevation: 4
  },
  primaryButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '700'
  },
  secondaryButton: {
    paddingVertical: 14,
    borderRadius: 12,
    alignItems: 'center',
    justifyContent: 'center',
    backgroundColor: '#F3F4F6'
  },
  secondaryButtonText: {
    color: '#6B7280',
    fontSize: 15,
    fontWeight: '600'
  },
  // Decorative sparkles
  sparkle: {
    position: 'absolute'
  },
  sparkle1: {
    top: 20,
    right: 25
  },
  sparkle2: {
    top: 50,
    left: 20
  },
  sparkle3: {
    bottom: 100,
    right: 30
  }
});

export default WalletCreditsPopup;
