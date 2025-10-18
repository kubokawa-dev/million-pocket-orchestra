import { View, Text, ScrollView, TouchableOpacity, ActivityIndicator } from 'react-native';
import { useRouter } from 'expo-router';

export default function HomeScreen() {
  const router = useRouter();

  return (
    <ScrollView className="flex-1 bg-white">
      <View className="p-4">
        <Text className="text-2xl font-bold mb-4">予測一覧</Text>
        
        {/* Lottery type filter */}
        <View className="flex-row gap-2 mb-4">
          <TouchableOpacity className="px-4 py-2 bg-blue-500 rounded-lg">
            <Text className="text-white font-semibold">すべて</Text>
          </TouchableOpacity>
          <TouchableOpacity className="px-4 py-2 bg-gray-200 rounded-lg">
            <Text className="text-gray-700 font-semibold">Numbers3</Text>
          </TouchableOpacity>
          <TouchableOpacity className="px-4 py-2 bg-gray-200 rounded-lg">
            <Text className="text-gray-700 font-semibold">Numbers4</Text>
          </TouchableOpacity>
          <TouchableOpacity className="px-4 py-2 bg-gray-200 rounded-lg">
            <Text className="text-gray-700 font-semibold">Loto6</Text>
          </TouchableOpacity>
        </View>

        {/* Placeholder for predictions list */}
        <View className="space-y-4">
          <View className="bg-gray-50 rounded-lg p-4 border border-gray-200">
            <View className="flex-row items-center mb-2">
              <View className="w-10 h-10 bg-blue-500 rounded-full mr-3" />
              <View>
                <Text className="font-semibold">ユーザー名</Text>
                <Text className="text-xs text-gray-500">2時間前</Text>
              </View>
            </View>
            <Text className="text-sm text-gray-600 mb-2">Numbers4 予測</Text>
            <Text className="text-lg font-bold mb-2">1234, 5678, 9012</Text>
            <Text className="text-sm text-gray-600 mb-3">
              過去のデータから分析した結果、この組み合わせが有望です。
            </Text>
            <View className="flex-row items-center gap-4">
              <View className="flex-row items-center">
                <Text className="text-sm text-gray-600">❤️ 12</Text>
              </View>
              <View className="flex-row items-center">
                <Text className="text-sm text-gray-600">💬 5</Text>
              </View>
            </View>
          </View>

          <View className="items-center py-8">
            <Text className="text-gray-500">
              API実装後に予測一覧が表示されます
            </Text>
          </View>
        </View>
      </View>
    </ScrollView>
  );
}
