import { View, Text, TextInput, ScrollView, TouchableOpacity } from 'react-native';
import { useState } from 'react';

export default function CreateScreen() {
  const [lotteryType, setLotteryType] = useState<'NUMBERS3' | 'NUMBERS4' | 'LOTO6'>('NUMBERS4');
  const [numbers, setNumbers] = useState('');
  const [reasoning, setReasoning] = useState('');

  return (
    <ScrollView className="flex-1 bg-white">
      <View className="p-4">
        <Text className="text-2xl font-bold mb-6">予測を投稿</Text>

        {/* Lottery Type Selection */}
        <Text className="text-sm font-semibold mb-2 text-gray-700">抽選タイプ</Text>
        <View className="flex-row gap-2 mb-6">
          <TouchableOpacity
            className={`px-4 py-3 rounded-lg ${lotteryType === 'NUMBERS3' ? 'bg-blue-500' : 'bg-gray-200'}`}
            onPress={() => setLotteryType('NUMBERS3')}
          >
            <Text className={`font-semibold ${lotteryType === 'NUMBERS3' ? 'text-white' : 'text-gray-700'}`}>
              Numbers3
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            className={`px-4 py-3 rounded-lg ${lotteryType === 'NUMBERS4' ? 'bg-blue-500' : 'bg-gray-200'}`}
            onPress={() => setLotteryType('NUMBERS4')}
          >
            <Text className={`font-semibold ${lotteryType === 'NUMBERS4' ? 'text-white' : 'text-gray-700'}`}>
              Numbers4
            </Text>
          </TouchableOpacity>
          <TouchableOpacity
            className={`px-4 py-3 rounded-lg ${lotteryType === 'LOTO6' ? 'bg-blue-500' : 'bg-gray-200'}`}
            onPress={() => setLotteryType('LOTO6')}
          >
            <Text className={`font-semibold ${lotteryType === 'LOTO6' ? 'text-white' : 'text-gray-700'}`}>
              Loto6
            </Text>
          </TouchableOpacity>
        </View>

        {/* Numbers Input */}
        <Text className="text-sm font-semibold mb-2 text-gray-700">予測番号</Text>
        <TextInput
          className="border border-gray-300 rounded-lg p-3 mb-6 text-base"
          placeholder={
            lotteryType === 'NUMBERS3'
              ? '例: 123, 456, 789'
              : lotteryType === 'NUMBERS4'
              ? '例: 1234, 5678, 9012'
              : '例: 1, 5, 12, 23, 35, 42'
          }
          value={numbers}
          onChangeText={setNumbers}
          multiline
        />

        {/* Reasoning */}
        <Text className="text-sm font-semibold mb-2 text-gray-700">理由・根拠</Text>
        <TextInput
          className="border border-gray-300 rounded-lg p-3 mb-6 text-base min-h-[100px]"
          placeholder="この予測の理由や分析内容を入力してください"
          value={reasoning}
          onChangeText={setReasoning}
          multiline
          textAlignVertical="top"
        />

        {/* Submit Button */}
        <TouchableOpacity className="bg-blue-500 rounded-lg py-4 items-center">
          <Text className="text-white font-bold text-base">投稿する</Text>
        </TouchableOpacity>

        <View className="mt-6 p-4 bg-yellow-50 rounded-lg border border-yellow-200">
          <Text className="text-sm text-yellow-800">
            💡 API実装後に投稿機能が有効になります
          </Text>
        </View>
      </View>
    </ScrollView>
  );
}
