import { View, Text, ScrollView, TouchableOpacity } from 'react-native';
import { Settings, LogOut } from 'lucide-react-native';

export default function ProfileScreen() {
  return (
    <ScrollView className="flex-1 bg-white">
      <View className="p-4">
        {/* Profile Header */}
        <View className="items-center mb-8">
          <View className="w-24 h-24 bg-blue-500 rounded-full mb-4" />
          <Text className="text-2xl font-bold mb-1">ユーザー名</Text>
          <Text className="text-gray-500">user@example.com</Text>
        </View>

        {/* Stats */}
        <View className="flex-row justify-around mb-8 bg-gray-50 rounded-lg p-4">
          <View className="items-center">
            <Text className="text-2xl font-bold">0</Text>
            <Text className="text-sm text-gray-600">投稿</Text>
          </View>
          <View className="items-center">
            <Text className="text-2xl font-bold">0</Text>
            <Text className="text-sm text-gray-600">いいね</Text>
          </View>
          <View className="items-center">
            <Text className="text-2xl font-bold">0</Text>
            <Text className="text-sm text-gray-600">的中</Text>
          </View>
        </View>

        {/* My Predictions */}
        <Text className="text-xl font-bold mb-4">マイ予測</Text>
        <View className="items-center py-8 bg-gray-50 rounded-lg mb-6">
          <Text className="text-gray-500">まだ予測を投稿していません</Text>
        </View>

        {/* Actions */}
        <TouchableOpacity className="flex-row items-center bg-gray-50 rounded-lg p-4 mb-3">
          <Settings size={20} color="#000" />
          <Text className="ml-3 text-base font-semibold">設定</Text>
        </TouchableOpacity>

        <TouchableOpacity className="flex-row items-center bg-red-50 rounded-lg p-4 mb-3">
          <LogOut size={20} color="#DC2626" />
          <Text className="ml-3 text-base font-semibold text-red-600">ログアウト</Text>
        </TouchableOpacity>

        <View className="mt-6 p-4 bg-blue-50 rounded-lg border border-blue-200">
          <Text className="text-sm text-blue-800">
            💡 Supabase認証実装後にログイン機能が有効になります
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}
