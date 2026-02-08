import React from 'react';
import {
  View,
  Text,
  ScrollView,
  TouchableOpacity,
  StyleSheet,
  Dimensions
} from 'react-native';
import { useRouter } from 'expo-router';
import { useAuth } from '../../contexts/AuthContext';
import { Ionicons } from '@expo/vector-icons';
import { SafeAreaView } from 'react-native-safe-area-context';

const { width } = Dimensions.get('window');
const tileWidth = (width - 48) / 2;

interface TileProps {
  title: string;
  subtitle: string;
  icon: string;
  color: string;
  onPress: () => void;
  disabled?: boolean;
  badge?: string;
}

const Tile: React.FC<TileProps> = ({ title, subtitle, icon, color, onPress, disabled, badge }) => (
  <TouchableOpacity
    style={[
      styles.tile,
      { borderLeftColor: color },
      disabled && styles.tileDisabled
    ]}
    onPress={onPress}
    disabled={disabled}
    activeOpacity={0.7}
  >
    <View style={[styles.tileIconContainer, { backgroundColor: color + '15' }]}>
      <Ionicons name={icon as any} size={32} color={color} />
    </View>
    <Text style={styles.tileTitle}>{title}</Text>
    <Text style={styles.tileSubtitle}>{subtitle}</Text>
    {badge && (
      <View style={[styles.badge, { backgroundColor: color }]}>
        <Text style={styles.badgeText}>{badge}</Text>
      </View>
    )}
    {disabled && (
      <View style={styles.comingSoonBadge}>
        <Text style={styles.comingSoonText}>Coming Soon</Text>
      </View>
    )}
  </TouchableOpacity>
);

export default function Dashboard() {
  const router = useRouter();
  const { user } = useAuth();

  const tiles = [
    {
      title: 'Create Lesson Plan',
      subtitle: 'Generate KICD-aligned lesson plans',
      icon: 'document-text',
      color: '#6366F1',
      route: '/(teacher)/home',
      disabled: false,
      badge: user?.freeLessonUsed ? undefined : '1 Free'
    },
    {
      title: 'Generate Notes',
      subtitle: 'Create learner-friendly notes',
      icon: 'create',
      color: '#10B981',
      route: '/(teacher)/notes',
      disabled: false,
      badge: user?.freeNotesUsed ? undefined : '1 Free'
    },
    {
      title: 'My Lesson Plans',
      subtitle: 'View your saved plans',
      icon: 'folder-open',
      color: '#F59E0B',
      route: '/(teacher)/lessons',
      disabled: false
    },
    {
      title: 'Schemes of Work',
      subtitle: 'Term planning documents',
      icon: 'calendar',
      color: '#8B5CF6',
      route: '/(teacher)/schemes',
      disabled: false
    },
    {
      title: 'Revision Papers',
      subtitle: 'Assessment materials',
      icon: 'school',
      color: '#EF4444',
      route: '/(teacher)/revision',
      disabled: true
    },
    {
      title: 'My Profile',
      subtitle: 'Settings & account',
      icon: 'person-circle',
      color: '#06B6D4',
      route: '/(teacher)/profile',
      disabled: false
    }
  ];

  return (
    <SafeAreaView style={styles.container} edges={['bottom']}>
      <ScrollView 
        contentContainerStyle={styles.scrollContent}
        showsVerticalScrollIndicator={false}
      >
        {/* Welcome Section */}
        <View style={styles.welcomeSection}>
          <View style={styles.welcomeContent}>
            <Text style={styles.welcomeText}>Welcome back,</Text>
            <Text style={styles.userName}>{user?.firstName} {user?.lastName}</Text>
            <View style={styles.schoolBadge}>
              <Ionicons name="business" size={14} color="#6366F1" />
              <Text style={styles.schoolName}>{user?.schoolName}</Text>
            </View>
          </View>
          <View style={styles.walletCard}>
            <Text style={styles.walletLabel}>Wallet Balance</Text>
            <Text style={styles.walletAmount}>KES {user?.walletBalance || 0}</Text>
          </View>
        </View>

        {/* Quick Stats */}
        <View style={styles.statsRow}>
          <View style={styles.statItem}>
            <Ionicons name="checkmark-circle" size={20} color="#10B981" />
            <Text style={styles.statValue}>{user?.freeLessonUsed ? 'Used' : 'Available'}</Text>
            <Text style={styles.statLabel}>Free Lesson</Text>
          </View>
          <View style={styles.statDivider} />
          <View style={styles.statItem}>
            <Ionicons name="checkmark-circle" size={20} color="#3B82F6" />
            <Text style={styles.statValue}>{user?.freeNotesUsed ? 'Used' : 'Available'}</Text>
            <Text style={styles.statLabel}>Free Notes</Text>
          </View>
        </View>

        {/* Tiles Grid */}
        <Text style={styles.sectionTitle}>What would you like to do?</Text>
        <View style={styles.tilesContainer}>
          {tiles.map((tile, index) => (
            <Tile
              key={index}
              title={tile.title}
              subtitle={tile.subtitle}
              icon={tile.icon}
              color={tile.color}
              onPress={() => router.push(tile.route as any)}
              disabled={tile.disabled}
              badge={tile.badge}
            />
          ))}
        </View>

        {/* Footer */}
        <View style={styles.footer}>
          <Text style={styles.footerText}>KICD-Aligned Competency Based Education</Text>
          <Text style={styles.footerSubtext}>For Kenyan Teachers</Text>
        </View>
      </ScrollView>
    </SafeAreaView>
  );
}

const styles = StyleSheet.create({
  container: {
    flex: 1,
    backgroundColor: '#F3F4F6'
  },
  scrollContent: {
    padding: 16
  },
  welcomeSection: {
    flexDirection: 'row',
    justifyContent: 'space-between',
    alignItems: 'flex-start',
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 16
  },
  welcomeContent: {
    flex: 1
  },
  welcomeText: {
    fontSize: 14,
    color: '#6B7280'
  },
  userName: {
    fontSize: 22,
    fontWeight: 'bold',
    color: '#111827',
    marginTop: 4
  },
  schoolBadge: {
    flexDirection: 'row',
    alignItems: 'center',
    backgroundColor: '#EEF2FF',
    paddingHorizontal: 10,
    paddingVertical: 4,
    borderRadius: 12,
    marginTop: 8,
    alignSelf: 'flex-start'
  },
  schoolName: {
    fontSize: 12,
    color: '#6366F1',
    marginLeft: 4,
    fontWeight: '500'
  },
  walletCard: {
    backgroundColor: '#6366F1',
    borderRadius: 12,
    padding: 12,
    alignItems: 'center',
    minWidth: 100
  },
  walletLabel: {
    fontSize: 10,
    color: '#C7D2FE',
    textTransform: 'uppercase'
  },
  walletAmount: {
    fontSize: 18,
    fontWeight: 'bold',
    color: '#FFFFFF',
    marginTop: 2
  },
  statsRow: {
    flexDirection: 'row',
    backgroundColor: '#FFFFFF',
    borderRadius: 12,
    padding: 16,
    marginBottom: 20,
    alignItems: 'center'
  },
  statItem: {
    flex: 1,
    alignItems: 'center'
  },
  statDivider: {
    width: 1,
    height: 40,
    backgroundColor: '#E5E7EB'
  },
  statValue: {
    fontSize: 14,
    fontWeight: '600',
    color: '#111827',
    marginTop: 4
  },
  statLabel: {
    fontSize: 12,
    color: '#6B7280',
    marginTop: 2
  },
  sectionTitle: {
    fontSize: 16,
    fontWeight: '600',
    color: '#374151',
    marginBottom: 12
  },
  tilesContainer: {
    flexDirection: 'row',
    flexWrap: 'wrap',
    justifyContent: 'space-between'
  },
  tile: {
    width: tileWidth,
    backgroundColor: '#FFFFFF',
    borderRadius: 16,
    padding: 16,
    marginBottom: 12,
    borderLeftWidth: 4,
    position: 'relative'
  },
  tileDisabled: {
    opacity: 0.7
  },
  tileIconContainer: {
    width: 56,
    height: 56,
    borderRadius: 14,
    justifyContent: 'center',
    alignItems: 'center',
    marginBottom: 12
  },
  tileTitle: {
    fontSize: 14,
    fontWeight: '700',
    color: '#111827',
    marginBottom: 4
  },
  tileSubtitle: {
    fontSize: 11,
    color: '#6B7280',
    lineHeight: 15
  },
  badge: {
    position: 'absolute',
    top: 10,
    right: 10,
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10
  },
  badgeText: {
    fontSize: 10,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  comingSoonBadge: {
    position: 'absolute',
    top: 10,
    right: 10,
    backgroundColor: '#9CA3AF',
    paddingHorizontal: 8,
    paddingVertical: 3,
    borderRadius: 10
  },
  comingSoonText: {
    fontSize: 9,
    fontWeight: '600',
    color: '#FFFFFF'
  },
  footer: {
    marginTop: 20,
    alignItems: 'center',
    paddingVertical: 16
  },
  footerText: {
    fontSize: 12,
    color: '#9CA3AF',
    fontWeight: '500'
  },
  footerSubtext: {
    fontSize: 11,
    color: '#D1D5DB',
    marginTop: 2
  }
});
