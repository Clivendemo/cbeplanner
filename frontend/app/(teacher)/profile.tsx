import React, { useState, useEffect, useCallback } from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Alert,
  ActivityIndicator,
  Modal,
  TextInput,
  KeyboardAvoidingView,
  Platform,
  RefreshControl,
  Share,
  Linking
} from 'react-native';
import { useAuth } from '../../contexts/AuthContext';
import { useRouter } from 'expo-router';
import { Ionicons } from '@expo/vector-icons';
import axios from 'axios';
import { getErrorMessage, isRateLimitError } from '../../utils/errorHandler';

const BACKEND_URL = process.env.EXPO_PUBLIC_BACKEND_URL;
const PLAY_STORE_URL = 'https://play.google.com/store/apps/details?id=com.legitlab.cbeplanner';

interface Transaction {
  id: string;
  tx_ref: string;
  amount: number;
  status: string;
  type: string;
  phoneNumber: string;
  mpesaReceiptNumber?: string;
  createdAt: string;
}

export default function Profile() {
  const { user, firebaseUser, signOut, refreshProfile, isAdmin } = useAuth();
  const router = useRouter();
  
  // About modal state
  const [showAboutModal, setShowAboutModal] = useState(false);
  
  // M-Pesa Top-up state
  const [showTopUpModal, setShowTopUpModal] = useState(false);
  const [phoneNumber, setPhoneNumber] = useState('');
  const [amount, setAmount] = useState('');
  const [topUpLoading, setTopUpLoading] = useState(false);
  const [checkingStatus, setCheckingStatus] = useState(false);
  const [pendingCheckoutId, setPendingCheckoutId] = useState<string | null>(null);
  
  // Transaction history state
  const [showTransactions, setShowTransactions] = useState(false);
  const [transactions, setTransactions] = useState<Transaction[]>([]);
  const [loadingTransactions, setLoadingTransactions] = useState(false);
  const [refreshing, setRefreshing] = useState(false);

  // Fetch transaction history
  const fetchTransactions = useCallback(async () => {
    if (!firebaseUser) return;
    
    setLoadingTransactions(true);
    try {
      const token = await firebaseUser.getIdToken();
      const response = await axios.get(`${BACKEND_URL}/api/payments/transactions`, {
        headers: { Authorization: `Bearer ${token}` }
      });
      
      if (response.data.success) {
        setTransactions(response.data.transactions);
      }
    } catch (error) {
      
    } finally {
      setLoadingTransactions(false);
    }
  }, [firebaseUser]);

  useEffect(() => {
    if (showTransactions) {
      fetchTransactions();
    }
  }, [showTransactions, fetchTransactions]);

  const onRefresh = async () => {
    setRefreshing(true);
    await refreshProfile();
    if (showTransactions) {
      await fetchTransactions();
    }
    setRefreshing(false);
  };

  // Handle M-Pesa top-up
  const handleTopUp = async () => {
    if (!phoneNumber || phoneNumber.length < 9) {
      Alert.alert('Error', 'Please enter a valid phone number');
      return;
    }
    
    const amountNum = parseInt(amount);
    if (!amount || isNaN(amountNum) || amountNum < 50) {
      Alert.alert('Error', 'Minimum top-up amount is 50 KES');
      return;
    }
    
    if (amountNum > 150000) {
      Alert.alert('Error', 'Maximum top-up amount is 150,000 KES');
      return;
    }

    setTopUpLoading(true);
    try {
      const token = await firebaseUser?.getIdToken();
      const response = await axios.post(
        `${BACKEND_URL}/api/payments/mpesa/initiate`,
        {
          phoneNumber: phoneNumber,
          amount: amountNum
        },
        { headers: { Authorization: `Bearer ${token}` } }
      );

      if (response.data.success) {
        setPendingCheckoutId(response.data.checkoutRequestID);
        Alert.alert(
          'M-Pesa Request Sent',
          'Please check your phone and enter your M-Pesa PIN to complete the payment.',
          [
            {
              text: 'Check Status',
              onPress: () => checkPaymentStatus(response.data.checkoutRequestID)
            }
          ]
        );
        setShowTopUpModal(false);
      }
    } catch (error: any) {
      const errorMsg = getErrorMessage(error);
      if (isRateLimitError(error)) {
        Alert.alert('Too Many Attempts', errorMsg);
      } else {
        Alert.alert('Payment Failed', errorMsg);
      }
    } finally {
      setTopUpLoading(false);
    }
  };

  const checkPaymentStatus = async (checkoutId: string) => {
    setCheckingStatus(true);
    let attempts = 0;
    const maxAttempts = 12;
    
    const pollStatus = async () => {
      try {
        const token = await firebaseUser?.getIdToken();
        const response = await axios.get(
          `${BACKEND_URL}/api/payments/mpesa/status/${checkoutId}`,
          { headers: { Authorization: `Bearer ${token}` } }
        );

        if (response.data.status === 'successful') {
          await refreshProfile();
          Alert.alert(
            'Payment Successful! 🎉',
            `KES ${response.data.amount} has been added to your wallet.`,
            [{ text: 'OK' }]
          );
          setPendingCheckoutId(null);
          setCheckingStatus(false);
          setPhoneNumber('');
          setAmount('');
          fetchTransactions();
          return true;
        } else if (response.data.status === 'failed' || response.data.status === 'cancelled') {
          Alert.alert(
            'Payment Not Completed',
            response.data.message || 'The payment was not completed. Please try again.'
          );
          setPendingCheckoutId(null);
          setCheckingStatus(false);
          return true;
        } else if (response.data.status === 'pending') {
          attempts++;
          if (attempts < maxAttempts) {
            setTimeout(pollStatus, 5000);
            return false;
          } else {
            Alert.alert(
              'Payment Pending',
              'Your payment is still being processed. Please check your transaction history later.',
              [
                { text: 'OK' },
                { text: 'Check Again', onPress: () => checkPaymentStatus(checkoutId) }
              ]
            );
            setCheckingStatus(false);
            return true;
          }
        }
      } catch (error) {
        
        attempts++;
        if (attempts < maxAttempts) {
          setTimeout(pollStatus, 5000);
          return false;
        }
        setCheckingStatus(false);
        Alert.alert('Error', 'Could not verify payment status. Please check your transaction history.');
        return true;
      }
    };

    pollStatus();
  };

  const handleSignOut = async () => {
    if (Platform.OS === 'web') {
      const confirmed = window.confirm('Are you sure you want to sign out?');
      if (confirmed) {
        try {
          await signOut();
          router.replace('/auth/login');
        } catch (error) {
          
          router.replace('/auth/login');
        }
      }
    } else {
      Alert.alert(
        'Sign Out',
        'Are you sure you want to sign out?',
        [
          { text: 'Cancel', style: 'cancel' },
          {
            text: 'Sign Out',
            style: 'destructive',
            onPress: async () => {
              try {
                await signOut();
                setTimeout(() => {
                  router.replace('/auth/login');
                }, 100);
              } catch (error) {
                
                router.replace('/auth/login');
              }
            }
          }
        ]
      );
    }
  };

  const formatDate = (dateString: string) => {
    const date = new Date(dateString);
    return date.toLocaleDateString('en-GB', {
      day: '2-digit',
      month: 'short',
      year: 'numeric',
      hour: '2-digit',
      minute: '2-digit'
    });
  };

  // Share app with others
  const handleShareApp = async () => {
    try {
      const message = `📚 Check out CBE Lesson Planner!\n\nA great app for Kenyan teachers to create KICD-aligned lesson plans, study notes, and schemes of work.\n\n✅ Easy to use\n✅ Curriculum aligned\n✅ Saves time\n\nDownload now: ${PLAY_STORE_URL}`;
      
      const result = await Share.share({
        message: message,
        title: 'Share CBE Lesson Planner'
      });
      
      if (result.action === Share.sharedAction) {
        
      }
    } catch (error: any) {
      // Fallback: Open Play Store link
      Linking.openURL(PLAY_STORE_URL).catch(() => {
        Alert.alert('Error', 'Could not open Play Store link');
      });
    }
  };

  const renderTransaction = (item: Transaction) => (
    <View key={item.id} style={styles.transactionItem}>
      <View style={styles.transactionLeft}>
        <View style={[
          styles.transactionIcon,
          item.status === 'successful' ? styles.successIcon :
          item.status === 'failed' ? styles.failedIcon : styles.pendingIcon
        ]}>
          <Ionicons 
            name={
              item.status === 'successful' ? 'checkmark' :
              item.status === 'failed' ? 'close' : 'time'
            } 
            size={16} 
            color="#FFFFFF" 
          />
        </View>
        <View>
          <Text style={styles.transactionType}>
            {item.type === 'topup' ? 'Wallet Top-up' : item.type}
          </Text>
          <Text style={styles.transactionDate}>{formatDate(item.createdAt)}</Text>
          {item.mpesaReceiptNumber && (
            <Text style={styles.transactionReceipt}>Ref: {item.mpesaReceiptNumber}</Text>
          )}
        </View>
      </View>
      <View style={styles.transactionRight}>
        <Text style={[
          styles.transactionAmount,
          item.status === 'successful' ? styles.successAmount : styles.pendingAmount
        ]}>
          {item.status === 'successful' ? '+' : ''}{item.amount} KES
        </Text>
        <Text style={[
          styles.transactionStatus,
          item.status === 'successful' ? styles.successStatus :
          item.status === 'failed' ? styles.failedStatus : styles.pendingStatus
        ]}>
          {item.status.charAt(0).toUpperCase() + item.status.slice(1)}
        </Text>
      </View>
    </View>
  );

  return (
    <ScrollView 
      style={styles.container} 
      contentContainerStyle={styles.content}
      refreshControl={
        <RefreshControl refreshing={refreshing} onRefresh={onRefresh} colors={['#6366F1']} />
      }
    >
      <View style={styles.header}>
        <View style={styles.avatarContainer}>
          <Ionicons name="person" size={48} color="#FFFFFF" />
        </View>
        <Text style={styles.name}>{user?.firstName} {user?.lastName}</Text>
        <Text style={styles.email}>{user?.email}</Text>
        <View style={styles.roleBadge}>
          <Text style={styles.roleText}>{user?.role?.toUpperCase()}</Text>
        </View>
      </View>

      {/* Wallet Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Wallet</Text>
        <View style={styles.walletCard}>
          <View style={styles.walletInfo}>
            <Ionicons name="wallet" size={32} color="#6366F1" />
            <View style={styles.walletDetails}>
              <Text style={styles.balanceLabel}>Available Balance</Text>
              <Text style={styles.balanceAmount}>{user?.walletBalance || 0} KES</Text>
            </View>
          </View>
          
          <TouchableOpacity 
            style={styles.topUpButton}
            onPress={() => setShowTopUpModal(true)}
          >
            <Ionicons name="phone-portrait-outline" size={20} color="#FFFFFF" />
            <Text style={styles.topUpButtonText}>Top Up via M-Pesa</Text>
          </TouchableOpacity>
          
          {pendingCheckoutId && (
            <TouchableOpacity 
              style={styles.checkStatusButton}
              onPress={() => checkPaymentStatus(pendingCheckoutId)}
              disabled={checkingStatus}
            >
              {checkingStatus ? (
                <ActivityIndicator size="small" color="#6366F1" />
              ) : (
                <>
                  <Ionicons name="refresh" size={16} color="#6366F1" />
                  <Text style={styles.checkStatusText}>Check Payment Status</Text>
                </>
              )}
            </TouchableOpacity>
          )}
          
          <TouchableOpacity 
            style={styles.historyButton}
            onPress={() => setShowTransactions(!showTransactions)}
          >
            <Ionicons name="receipt-outline" size={16} color="#6B7280" />
            <Text style={styles.historyButtonText}>
              {showTransactions ? 'Hide' : 'View'} Transaction History
            </Text>
            <Ionicons 
              name={showTransactions ? 'chevron-up' : 'chevron-down'} 
              size={16} 
              color="#6B7280" 
            />
          </TouchableOpacity>
        </View>

        {showTransactions && (
          <View style={styles.transactionsContainer}>
            {loadingTransactions ? (
              <ActivityIndicator size="small" color="#6366F1" style={{ marginVertical: 20 }} />
            ) : transactions.length > 0 ? (
              transactions.map(renderTransaction)
            ) : (
              <Text style={styles.noTransactions}>No transactions yet</Text>
            )}
          </View>
        )}

        {/* Free Lessons Card */}
        <View style={styles.freeLessonCard}>
          <View style={styles.freeLessonRow}>
            <Ionicons name="gift" size={24} color="#10B981" />
            <View style={styles.freeLessonInfo}>
              <Text style={styles.freeLessonLabel}>Free Lessons</Text>
              <Text style={styles.freeLessonStatus}>
                {user?.freeLessonsRemaining ?? 0} remaining
              </Text>
            </View>
            <View style={styles.priceBadge}>
              <Text style={styles.priceText}>KES 2/plan</Text>
            </View>
          </View>
        </View>

        <View style={styles.freeNotesCard}>
          <View style={styles.freeLessonRow}>
            <Ionicons name="gift" size={24} color="#3B82F6" />
            <View style={styles.freeLessonInfo}>
              <Text style={styles.freeLessonLabel}>Free Notes</Text>
              <Text style={styles.freeNotesStatus}>
                {user?.freeNotesUsed ? 'Used' : 'Available'}
              </Text>
            </View>
          </View>
        </View>
      </View>

      {/* Account Section */}
      <View style={styles.section}>
        <Text style={styles.sectionTitle}>Account</Text>
        
        <TouchableOpacity 
          style={styles.menuItem}
          onPress={() => setShowAboutModal(true)}
          data-testid="about-cbe-planner-btn"
        >
          <Ionicons name="information-circle-outline" size={24} color="#6B7280" />
          <Text style={styles.menuText}>About CBE Planner</Text>
          <Ionicons name="chevron-forward" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        <TouchableOpacity 
          style={styles.menuItem}
          onPress={() => Linking.openURL('mailto:legitlabs@outlook.com?subject=CBE%20Planner%20Support')}
          data-testid="help-support-btn"
        >
          <Ionicons name="help-circle-outline" size={24} color="#6B7280" />
          <View style={styles.menuTextContainer}>
            <Text style={styles.menuText}>Help & Support</Text>
            <Text style={styles.supportEmailText}>legitlabs@outlook.com</Text>
          </View>
          <Ionicons name="mail-outline" size={20} color="#9CA3AF" />
        </TouchableOpacity>

        {/* Share App Button */}
        <TouchableOpacity 
          style={[styles.menuItem, styles.shareAppButton]}
          onPress={handleShareApp}
          data-testid="share-app-btn"
        >
          <Ionicons name="share-social-outline" size={24} color="#10B981" />
          <Text style={[styles.menuText, styles.shareAppText]}>Share App with Colleagues</Text>
          <Ionicons name="chevron-forward" size={20} color="#10B981" />
        </TouchableOpacity>

        {/* Admin Panel - ONLY for mail2clive@gmail.com */}
        {isAdmin && (
          <TouchableOpacity 
            style={[styles.menuItem, styles.adminButton]} 
            onPress={() => router.push('/(admin)/dashboard')}
          >
            <Ionicons name="shield-checkmark-outline" size={24} color="#F59E0B" />
            <Text style={[styles.menuText, styles.adminText]}>Admin Panel</Text>
            <Ionicons name="chevron-forward" size={20} color="#F59E0B" />
          </TouchableOpacity>
        )}

        <TouchableOpacity style={[styles.menuItem, styles.signOutButton]} onPress={handleSignOut}>
          <Ionicons name="log-out-outline" size={24} color="#EF4444" />
          <Text style={[styles.menuText, styles.signOutText]}>Sign Out</Text>
        </TouchableOpacity>

        {/* Developer Credit */}
        <View style={styles.developerCredit}>
          <Text style={styles.developerText}>Developed by LEGIT LAB</Text>
          <Text style={styles.versionText}>Version 1.0.0</Text>
        </View>
      </View>

      {/* M-Pesa Top-up Modal */}
      <Modal
        visible={showTopUpModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowTopUpModal(false)}
      >
        <KeyboardAvoidingView 
          behavior={Platform.OS === 'ios' ? 'padding' : 'height'}
          style={styles.modalOverlay}
        >
          <View style={styles.modalContent}>
            <View style={styles.modalHeader}>
              <Text style={styles.modalTitle}>Top Up via M-Pesa</Text>
              <TouchableOpacity onPress={() => setShowTopUpModal(false)}>
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            <ScrollView
              showsVerticalScrollIndicator={false}
              contentContainerStyle={{ paddingBottom: 20 }}
              style={{ maxHeight: '80%' }}
            >

            <View style={styles.mpesaLogoContainer}>
              <View style={styles.mpesaLogo}>
                <Ionicons name="phone-portrait" size={32} color="#00A859" />
              </View>
              <Text style={styles.mpesaText}>M-PESA</Text>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>M-Pesa Phone Number</Text>
              <View style={styles.phoneInputContainer}>
                <Text style={styles.countryCode}>+254</Text>
                <TextInput
                  style={styles.phoneInput}
                  placeholder="712345678"
                  placeholderTextColor="#9CA3AF"
                  keyboardType="phone-pad"
                  value={phoneNumber}
                  onChangeText={setPhoneNumber}
                  maxLength={10}
                />
              </View>
              <Text style={styles.inputHint}>Enter phone number registered with M-Pesa</Text>
            </View>

            <View style={styles.inputGroup}>
              <Text style={styles.inputLabel}>Amount (KES)</Text>
              <View style={styles.amountInputContainer}>
                <Text style={styles.currencyLabel}>KES</Text>
                <TextInput
                  style={styles.amountInput}
                  placeholder="100"
                  placeholderTextColor="#9CA3AF"
                  keyboardType="number-pad"
                  value={amount}
                  onChangeText={setAmount}
                />
              </View>
              <Text style={styles.inputHint}>Minimum: 50 KES • Maximum: 150,000 KES</Text>
            </View>

            <View style={styles.quickAmounts}>
              {[100, 200, 500, 1000].map((amt) => (
                <TouchableOpacity
                  key={amt}
                  style={[
                    styles.quickAmountBtn,
                    amount === String(amt) && styles.quickAmountBtnActive
                  ]}
                  onPress={() => setAmount(String(amt))}
                >
                  <Text style={[
                    styles.quickAmountText,
                    amount === String(amt) && styles.quickAmountTextActive
                  ]}>
                    {amt}
                  </Text>
                </TouchableOpacity>
              ))}
            </View>

            <TouchableOpacity
              style={[styles.payButton, topUpLoading && styles.payButtonDisabled]}
              onPress={handleTopUp}
              disabled={topUpLoading}
            >
              {topUpLoading ? (
                <ActivityIndicator size="small" color="#FFFFFF" />
              ) : (
                <>
                  <Ionicons name="lock-closed" size={20} color="#FFFFFF" />
                  <Text style={styles.payButtonText}>
                    Pay {amount ? `KES ${amount}` : ''} with M-Pesa
                  </Text>
                </>
              )}
            </TouchableOpacity>

            <View style={styles.secureTextContainer}>
              <Ionicons name="shield-checkmark" size={14} color="#10B981" />
              <Text style={styles.secureText}> Secure payment via Safaricom M-Pesa</Text>
            </View>

            {/* Manual Buy Goods fallback — shown when STK push fails to arrive */}
            <View style={styles.mpesaFallback}>
              <View style={styles.mpesaFallbackHeader}>
                <Ionicons name="information-circle" size={16} color="#00A859" />
                <Text style={styles.mpesaFallbackTitle}>STK push didn't arrive?</Text>
              </View>
              <Text style={styles.mpesaFallbackSub}>
                Pay manually via Buy Goods on M-Pesa:
              </Text>

              <View style={styles.tillBlock}>
                <Text style={styles.tillLabel}>TILL NUMBER</Text>
                <Text style={styles.tillNumber}>8336258</Text>
                <View style={styles.buyGoodsBadge}>
                  <Text style={styles.buyGoodsBadgeText}>BUY GOODS</Text>
                </View>
              </View>

              <View style={styles.stepsBlock}>
                {[
                  'Open MPesa on your phone',
                  'Select Lipa na MPesa',
                  'Select Buy Goods & Services',
                  'Enter Till No. 8336258',
                  'Enter amount & your M-PIN',
                ].map((step, idx) => (
                  <View key={idx} style={styles.stepRow}>
                    <View style={styles.stepNumber}>
                      <Text style={styles.stepNumberText}>{idx + 1}</Text>
                    </View>
                    <Text style={styles.stepText}>{step}</Text>
                  </View>
                ))}
              </View>

              <Text style={styles.mpesaFallbackFooter}>
                After payment, refresh the page or contact{' '}
                <Text
                  style={styles.mpesaFallbackEmail}
                  onPress={() => Linking.openURL('mailto:legitlabs@outlook.com?subject=M-Pesa%20Payment%20Confirmation')}
                >
                  legitlabs@outlook.com
                </Text>
                {' '}with your transaction code.
              </Text>
            </View>
            </ScrollView>
          </View>
        </KeyboardAvoidingView>
      </Modal>

      {/* About Modal */}
      <Modal
        visible={showAboutModal}
        animationType="slide"
        transparent={true}
        onRequestClose={() => setShowAboutModal(false)}
      >
        <View style={styles.aboutModalOverlay}>
          <View style={styles.aboutModalContent}>
            <View style={styles.aboutModalHeader}>
              <Text style={styles.aboutModalTitle}>About CBE Lesson Planner</Text>
              <TouchableOpacity 
                onPress={() => setShowAboutModal(false)}
                data-testid="close-about-modal-btn"
              >
                <Ionicons name="close" size={24} color="#6B7280" />
              </TouchableOpacity>
            </View>

            <ScrollView 
              style={styles.aboutScrollView}
              showsVerticalScrollIndicator={false}
            >
              {/* Hero Section */}
              <View style={styles.aboutHero}>
                <View style={styles.aboutLogoContainer}>
                  <Ionicons name="book" size={40} color="#FFFFFF" />
                </View>
                <Text style={styles.aboutHeroTitle}>CBE Lesson Planner</Text>
                <Text style={styles.aboutHeroSubtitle}>Empowering Kenyan Educators</Text>
              </View>

              {/* Introduction */}
              <View style={styles.aboutSection}>
                <Text style={styles.aboutText}>
                  CBE Lesson Planner is a curriculum-based learning platform designed specifically for Kenyan teachers. 
                  It helps educators create KICD-aligned lesson plans, study notes, and schemes of work that follow 
                  the Competency-Based Curriculum (CBC) framework.
                </Text>
              </View>

              {/* Who It's For */}
              <View style={styles.aboutSection}>
                <Text style={styles.aboutSectionTitle}>Who Is It For?</Text>
                <View style={styles.aboutUserCard}>
                  <View style={styles.aboutUserIcon}>
                    <Ionicons name="school-outline" size={24} color="#6366F1" />
                  </View>
                  <View style={styles.aboutUserInfo}>
                    <Text style={styles.aboutUserTitle}>Teachers and Educators</Text>
                    <Text style={styles.aboutUserDesc}>
                      Save time creating structured, curriculum-aligned lesson materials
                    </Text>
                  </View>
                </View>
                <View style={styles.aboutUserCard}>
                  <View style={styles.aboutUserIcon}>
                    <Ionicons name="people-outline" size={24} color="#10B981" />
                  </View>
                  <View style={styles.aboutUserInfo}>
                    <Text style={styles.aboutUserTitle}>School Administrators</Text>
                    <Text style={styles.aboutUserDesc}>
                      Ensure teaching materials meet national curriculum standards
                    </Text>
                  </View>
                </View>
              </View>

              {/* Key Features */}
              <View style={styles.aboutSection}>
                <Text style={styles.aboutSectionTitle}>Key Features</Text>
                
                <View style={styles.aboutFeatureItem}>
                  <View style={styles.aboutFeatureBullet}>
                    <Ionicons name="document-text-outline" size={18} color="#6366F1" />
                  </View>
                  <View style={styles.aboutFeatureContent}>
                    <Text style={styles.aboutFeatureTitle}>Lesson Plan Generator</Text>
                    <Text style={styles.aboutFeatureDesc}>
                      Create detailed, time-aware lesson plans (25-80 minutes) aligned with specific learning outcomes
                    </Text>
                  </View>
                </View>

                <View style={styles.aboutFeatureItem}>
                  <View style={styles.aboutFeatureBullet}>
                    <Ionicons name="library-outline" size={18} color="#10B981" />
                  </View>
                  <View style={styles.aboutFeatureContent}>
                    <Text style={styles.aboutFeatureTitle}>Study Notes Generator</Text>
                    <Text style={styles.aboutFeatureDesc}>
                      Generate comprehensive teaching notes for any topic in your curriculum
                    </Text>
                  </View>
                </View>

                <View style={styles.aboutFeatureItem}>
                  <View style={styles.aboutFeatureBullet}>
                    <Ionicons name="calendar-outline" size={18} color="#F59E0B" />
                  </View>
                  <View style={styles.aboutFeatureContent}>
                    <Text style={styles.aboutFeatureTitle}>Schemes of Work</Text>
                    <Text style={styles.aboutFeatureDesc}>
                      Plan your entire term with structured schemes including breaks and assessments
                    </Text>
                  </View>
                </View>

                <View style={styles.aboutFeatureItem}>
                  <View style={styles.aboutFeatureBullet}>
                    <Ionicons name="git-branch-outline" size={18} color="#EC4899" />
                  </View>
                  <View style={styles.aboutFeatureContent}>
                    <Text style={styles.aboutFeatureTitle}>Structured Curriculum Mapping</Text>
                    <Text style={styles.aboutFeatureDesc}>
                      Content organized by Grades, Subjects, Strands, Sub-Strands, and Specific Learning Outcomes (SLOs)
                    </Text>
                  </View>
                </View>

                <View style={styles.aboutFeatureItem}>
                  <View style={styles.aboutFeatureBullet}>
                    <Ionicons name="analytics-outline" size={18} color="#3B82F6" />
                  </View>
                  <View style={styles.aboutFeatureContent}>
                    <Text style={styles.aboutFeatureTitle}>Competency & Values Integration</Text>
                    <Text style={styles.aboutFeatureDesc}>
                      Each SLO is mapped to core competencies, values, and pertinent and contemporary issues (PCIs)
                    </Text>
                  </View>
                </View>
              </View>

              {/* Benefits */}
              <View style={styles.aboutSection}>
                <Text style={styles.aboutSectionTitle}>How It Helps</Text>
                <View style={styles.aboutBenefitsList}>
                  <View style={styles.aboutBenefitItem}>
                    <Ionicons name="time-outline" size={20} color="#10B981" />
                    <Text style={styles.aboutBenefitText}>Save hours of lesson preparation time</Text>
                  </View>
                  <View style={styles.aboutBenefitItem}>
                    <Ionicons name="checkmark-circle-outline" size={20} color="#10B981" />
                    <Text style={styles.aboutBenefitText}>Ensure KICD curriculum alignment</Text>
                  </View>
                  <View style={styles.aboutBenefitItem}>
                    <Ionicons name="trending-up-outline" size={20} color="#10B981" />
                    <Text style={styles.aboutBenefitText}>Improve teaching consistency and quality</Text>
                  </View>
                  <View style={styles.aboutBenefitItem}>
                    <Ionicons name="phone-portrait-outline" size={20} color="#10B981" />
                    <Text style={styles.aboutBenefitText}>Access materials anytime, anywhere</Text>
                  </View>
                </View>
              </View>

              {/* Mission */}
              <View style={styles.aboutMission}>
                <Ionicons name="flag-outline" size={24} color="#6366F1" style={{ marginBottom: 12 }} />
                <Text style={styles.aboutMissionTitle}>Our Mission</Text>
                <Text style={styles.aboutMissionText}>
                  To empower Kenyan educators with tools that simplify lesson planning, 
                  ensure curriculum compliance, and ultimately improve learning outcomes for students across the nation.
                </Text>
              </View>

              {/* Developer Credit */}
              <View style={styles.aboutFooter}>
                <Text style={styles.aboutDeveloper}>Developed by LEGIT LAB</Text>
                <Text style={styles.aboutVersion}>Version 1.0.0</Text>
                <Text style={styles.aboutCopyright}>2025 LEGIT LAB. All rights reserved.</Text>
              </View>
            </ScrollView>
          </View>
        </View>
      </Modal>
    </ScrollView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F9FAFB'
  },
  content: {
    padding: 16
  },
  header: {
    alignItems: 'center',
    paddingVertical: 32,
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    marginBottom: 24
  },
  avatarContainer: {
    width: 96,
    height: 96,
    borderRadius: 48,
    backgroundColor: '#6366F1',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16
  },
  name: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4
  },
  email: {
    fontSize: 14,
    color: '#6B7280',
    marginBottom: 12
  },
  roleBadge: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 16,
    paddingVertical: 6,
    borderRadius: 16
  },
  roleText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6366F1'
  },
  section: {
    marginBottom: 24
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12
  },
  walletCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 12
  },
  walletInfo: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 16
  },
  walletDetails: {
    marginLeft: 12
  },
  balanceLabel: {
    fontSize: 12,
    color: '#6B7280'
  },
  balanceAmount: {
    fontSize: 24,
    fontWeight: 'bold',
    color: '#111827'
  },
  topUpButton: {
    backgroundColor: '#00A859',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 14,
    borderRadius: 8,
    marginBottom: 8
  },
  topUpButtonText: {
    color: '#FFFFFF',
    fontSize: 16,
    fontWeight: '600',
    marginLeft: 8
  },
  checkStatusButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 10,
    backgroundColor: '#EEF2FF',
    borderRadius: 8,
    marginBottom: 8
  },
  checkStatusText: {
    color: '#6366F1',
    fontSize: 14,
    fontWeight: '500',
    marginLeft: 6
  },
  historyButton: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 8
  },
  historyButtonText: {
    color: '#6B7280',
    fontSize: 14,
    marginHorizontal: 6
  },
  transactionsContainer: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 12,
    marginBottom: 12
  },
  transactionItem: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    paddingVertical: 12,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  transactionLeft: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  transactionIcon: {
    width: 32,
    height: 32,
    borderRadius: 16,
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  successIcon: {
    backgroundColor: '#10B981'
  },
  failedIcon: {
    backgroundColor: '#EF4444'
  },
  pendingIcon: {
    backgroundColor: '#F59E0B'
  },
  transactionType: {
    fontSize: 14,
    fontWeight: '500',
    color: '#111827'
  },
  transactionDate: {
    fontSize: 12,
    color: '#6B7280'
  },
  transactionReceipt: {
    fontSize: 11,
    color: '#9CA3AF'
  },
  transactionRight: {
    alignItems: 'flex-end'
  },
  transactionAmount: {
    fontSize: 14,
    fontWeight: '600'
  },
  successAmount: {
    color: '#10B981'
  },
  pendingAmount: {
    color: '#6B7280'
  },
  transactionStatus: {
    fontSize: 12
  },
  successStatus: {
    color: '#10B981'
  },
  failedStatus: {
    color: '#EF4444'
  },
  pendingStatus: {
    color: '#F59E0B'
  },
  noTransactions: {
    textAlign: 'center',
    color: '#9CA3AF',
    paddingVertical: 20
  },
  freeLessonCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 8
  },
  freeLessonRow: {
    flexDirection: 'row',
    alignItems: 'center'
  },
  freeLessonInfo: {
    marginLeft: 12,
    flex: 1
  },
  freeLessonLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151'
  },
  freeLessonStatus: {
    fontSize: 12,
    color: '#10B981'
  },
  priceBadge: {
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12
  },
  priceText: {
    fontSize: 11,
    fontWeight: '600',
    color: '#6366F1'
  },
  freeNotesCard: {
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16
  },
  freeNotesStatus: {
    fontSize: 12,
    color: '#3B82F6'
  },
  menuItem: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#FFFFFF',
    padding: 16,
    borderRadius: 8,
    marginBottom: 8
  },
  menuText: {
    flex: 1,
    marginLeft: 12,
    fontSize: 16,
    color: '#374151'
  },
  menuTextContainer: {
    flex: 1,
    marginLeft: 12
  },
  supportEmailText: {
    fontSize: 12,
    color: '#6366F1',
    marginTop: 2
  },
  signOutButton: {
    marginTop: 8
  },
  signOutText: {
    color: '#EF4444'
  },
  adminButton: {
    marginTop: 8,
    borderWidth: 1,
    borderColor: '#F59E0B'
  },
  adminText: {
    color: '#F59E0B'
  },
  shareAppButton: {
    backgroundColor: '#F0FDF4',
    borderWidth: 1,
    borderColor: '#BBF7D0'
  },
  shareAppText: {
    color: '#10B981'
  },
  modalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end'
  },
  modalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    padding: 24,
    paddingBottom: 40
  },
  modalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    marginBottom: 20
  },
  modalTitle: {
    fontSize: 20,
    fontWeight: 'bold',
    color: '#111827'
  },
  mpesaLogoContainer: {
    alignItems: 'center',
    marginBottom: 24
  },
  mpesaLogo: {
    width: 64,
    height: 64,
    borderRadius: 32,
    backgroundColor: '#E8F5E9',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 8
  },
  mpesaText: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#00A859'
  },
  inputGroup: {
    marginBottom: 16
  },
  inputLabel: {
    fontSize: 14,
    fontWeight: '500',
    color: '#374151',
    marginBottom: 8
  },
  phoneInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    backgroundColor: '#F9FAFB'
  },
  countryCode: {
    paddingHorizontal: 12,
    paddingVertical: 14,
    fontSize: 16,
    color: '#374151',
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB'
  },
  phoneInput: {
    flex: 1,
    paddingHorizontal: 12,
    paddingVertical: 14,
    fontSize: 16,
    color: '#111827'
  },
  inputHint: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4
  },
  amountInputContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    borderWidth: 1,
    borderColor: '#E5E7EB',
    borderRadius: 8,
    backgroundColor: '#F9FAFB'
  },
  currencyLabel: {
    paddingHorizontal: 12,
    paddingVertical: 14,
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    borderRightWidth: 1,
    borderRightColor: '#E5E7EB'
  },
  amountInput: {
    flex: 1,
    paddingHorizontal: 12,
    paddingVertical: 14,
    fontSize: 20,
    fontWeight: '600',
    color: '#111827'
  },
  quickAmounts: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    marginBottom: 20
  },
  quickAmountBtn: {
    flex: 1,
    paddingVertical: 10,
    marginHorizontal: 4,
    borderRadius: 8,
    borderWidth: 1,
    borderColor: '#E5E7EB',
    alignItems: 'center'
  },
  quickAmountBtnActive: {
    borderColor: '#00A859',
    backgroundColor: '#E8F5E9'
  },
  quickAmountText: {
    fontSize: 14,
    fontWeight: '500',
    color: '#6B7280'
  },
  quickAmountTextActive: {
    color: '#00A859'
  },
  payButton: {
    backgroundColor: '#00A859',
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center',
    paddingVertical: 16,
    borderRadius: 12,
    marginBottom: 12
  },
  payButtonDisabled: {
    backgroundColor: '#9CA3AF'
  },
  payButtonText: {
    color: '#FFFFFF',
    fontSize: 18,
    fontWeight: '600',
    marginLeft: 8
  },
  secureTextContainer: {
    flexDirection: 'row',
    alignItems: 'center',
    justifyContent: 'center'
  },
  secureText: {
    fontSize: 12,
    color: '#6B7280'
  },
  // ===== M-Pesa manual Buy Goods fallback =====
  mpesaFallback: {
    marginTop: 20,
    backgroundColor: '#F0FDF4',
    borderWidth: 1,
    borderColor: '#86EFAC',
    borderRadius: 12,
    padding: 14,
  },
  mpesaFallbackHeader: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 6,
    marginBottom: 6,
  },
  mpesaFallbackTitle: {
    fontSize: 13,
    fontWeight: '700',
    color: '#00A859',
  },
  mpesaFallbackSub: {
    fontSize: 12,
    color: '#166534',
    marginBottom: 12,
  },
  tillBlock: {
    backgroundColor: '#00A859',
    borderRadius: 10,
    paddingVertical: 12,
    paddingHorizontal: 14,
    alignItems: 'center',
    marginBottom: 12,
    borderWidth: 2,
    borderColor: '#13BC3F',
  },
  tillLabel: {
    fontSize: 10,
    fontWeight: '700',
    color: '#A7F3D0',
    letterSpacing: 1.5,
    marginBottom: 2,
  },
  tillNumber: {
    fontSize: 28,
    fontWeight: '800',
    color: '#FFFFFF',
    letterSpacing: 2,
    marginVertical: 2,
  },
  buyGoodsBadge: {
    backgroundColor: '#FFFFFF',
    paddingHorizontal: 10,
    paddingVertical: 3,
    borderRadius: 20,
    marginTop: 6,
  },
  buyGoodsBadgeText: {
    fontSize: 10,
    fontWeight: '700',
    color: '#00A859',
    letterSpacing: 0.8,
  },
  stepsBlock: {
    gap: 6,
    marginBottom: 12,
  },
  stepRow: {
    flexDirection: 'row',
    alignItems: 'center',
    gap: 10,
  },
  stepNumber: {
    width: 22,
    height: 22,
    borderRadius: 11,
    backgroundColor: '#00A859',
    alignItems: 'center',
    justifyContent: 'center',
  },
  stepNumberText: {
    fontSize: 11,
    fontWeight: '700',
    color: '#FFFFFF',
  },
  stepText: {
    flex: 1,
    fontSize: 12,
    color: '#1F2937',
    lineHeight: 16,
  },
  mpesaFallbackFooter: {
    fontSize: 11,
    color: '#166534',
    lineHeight: 16,
    marginTop: 4,
  },
  mpesaFallbackEmail: {
    color: '#00A859',
    fontWeight: '700',
    textDecorationLine: 'underline',
  },
  developerCredit: {
    alignItems: 'center',
    paddingVertical: 20,
    marginTop: 8
  },
  developerText: {
    fontSize: 12,
    fontWeight: '600',
    color: '#6366F1'
  },
  versionText: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 4
  },
  // About Modal Styles
  aboutModalOverlay: {
    flex: 1,
    backgroundColor: 'rgba(0, 0, 0, 0.5)',
    justifyContent: 'flex-end'
  },
  aboutModalContent: {
    backgroundColor: '#FFFFFF',
    borderTopLeftRadius: 24,
    borderTopRightRadius: 24,
    maxHeight: '90%'
  },
  aboutModalHeader: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'center',
    padding: 20,
    borderBottomWidth: 1,
    borderBottomColor: '#F3F4F6'
  },
  aboutModalTitle: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#111827'
  },
  aboutScrollView: {
    paddingHorizontal: 20
  },
  aboutHero: {
    alignItems: 'center',
    paddingVertical: 24,
    marginBottom: 8
  },
  aboutLogoContainer: {
    width: 72,
    height: 72,
    borderRadius: 36,
    backgroundColor: '#6366F1',
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 16
  },
  aboutHeroTitle: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#111827',
    marginBottom: 4
  },
  aboutHeroSubtitle: {
    fontSize: 14,
    color: '#6366F1',
    fontWeight: '500'
  },
  aboutSection: {
    marginBottom: 24
  },
  aboutSectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 12
  },
  aboutText: {
    fontSize: 14,
    color: '#4B5563',
    lineHeight: 22
  },
  aboutUserCard: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#F9FAFB',
    borderRadius: 12,
    padding: 14,
    marginBottom: 10
  },
  aboutUserIcon: {
    width: 44,
    height: 44,
    borderRadius: 22,
    backgroundColor: '#FFFFFF',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  aboutUserInfo: {
    flex: 1
  },
  aboutUserTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 2
  },
  aboutUserDesc: {
    fontSize: 13,
    color: '#6B7280'
  },
  aboutFeatureItem: {
    flexDirection: 'row',
    marginBottom: 16
  },
  aboutFeatureBullet: {
    width: 32,
    height: 32,
    borderRadius: 16,
    backgroundColor: '#F3F4F6',
    justifyContent: 'center',
    alignItems: 'center',
    marginRight: 12
  },
  aboutFeatureContent: {
    flex: 1
  },
  aboutFeatureTitle: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginBottom: 2
  },
  aboutFeatureDesc: {
    fontSize: 13,
    color: '#6B7280',
    lineHeight: 19
  },
  aboutBenefitsList: {
    backgroundColor: '#F0FDF4',
    borderRadius: 12,
    padding: 16
  },
  aboutBenefitItem: {
    flexDirection: 'row',
    alignItems: 'center',
    marginBottom: 12
  },
  aboutBenefitText: {
    fontSize: 14,
    color: '#166534',
    marginLeft: 10,
    flex: 1
  },
  aboutMission: {
    backgroundColor: '#EEF2FF',
    borderRadius: 12,
    padding: 20,
    alignItems: 'center',
    marginBottom: 24
  },
  aboutMissionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#4338CA',
    marginBottom: 8
  },
  aboutMissionText: {
    fontSize: 14,
    color: '#4B5563',
    textAlign: 'center',
    lineHeight: 22
  },
  aboutFooter: {
    alignItems: 'center',
    paddingVertical: 24,
    borderTopWidth: 1,
    borderTopColor: '#F3F4F6',
    marginBottom: 20
  },
  aboutDeveloper: {
    fontSize: 13,
    fontWeight: '600',
    color: '#6366F1'
  },
  aboutVersion: {
    fontSize: 12,
    color: '#9CA3AF',
    marginTop: 4
  },
  aboutCopyright: {
    fontSize: 11,
    color: '#9CA3AF',
    marginTop: 4
  }
});
