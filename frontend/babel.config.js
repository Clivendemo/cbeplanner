// ==============================================================================
// BABEL CONFIGURATION - Production Ready
// ==============================================================================
// IMPORTANT: react-native-reanimated/plugin MUST be listed LAST
// ==============================================================================

module.exports = function (api) {
  api.cache(true);
  
  return {
    presets: ['babel-preset-expo'],
    plugins: [
      // Add any other plugins BEFORE reanimated
      
      // MUST BE LAST - React Native Reanimated plugin
      'react-native-reanimated/plugin',
    ],
  };
};
