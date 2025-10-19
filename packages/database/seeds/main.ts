import { createClient } from '@supabase/supabase-js';
import { fakerJA as faker } from '@faker-js/faker';


// TEMPORARY: Hardcoding values to bypass environment variable issues.
const supabaseUrl = 'http://127.0.0.1:54321';
const supabaseServiceKey = 'sb_secret_N7UND0UgjKTVK-Uodkm0Hg_xSvEMPvz';

if (!supabaseUrl || !supabaseServiceKey) {
  throw new Error('Hardcoded Supabase URL or Service Key is missing!');
}

// RLSをバイパスするためにService Roleキーでクライアントを初期化
const supabaseAdmin = createClient(supabaseUrl, supabaseServiceKey);

const LOTTERY_TYPES = ['LOTO6', 'NUMBERS4', 'NUMBERS3'];
const USER_COUNT = 100;
const PREDICTION_POST_COUNT = 5000;

// --- Helper Functions ---

// 指定された範囲のランダムな整数を生成
const getRandomInt = (min: number, max: number) => Math.floor(Math.random() * (max - min + 1)) + min;

// 配列からランダムな要素を1つ選択
const getRandomElement = <T>(arr: T[]): T => arr[Math.floor(Math.random() * arr.length)];

// ナンバーズの数字を生成 (例: "1234")
const generateNumbers = (count: number) => {
  let numbers = '';
  for (let i = 0; i < count; i++) {
    numbers += getRandomInt(0, 9).toString();
  }
  return numbers;
};

// ロト6の数字を生成 (例: [1, 10, 22, 33, 40, 41])
const generateLoto6Numbers = () => {
  const numbers = new Set<number>();
  while (numbers.size < 6) {
    numbers.add(getRandomInt(1, 43));
  }
  return Array.from(numbers).sort((a, b) => a - b);
};

// --- Main Seeding Logic ---

async function main() {
  console.log('🌱 Starting database seeding...');

  // 1. Clean up existing data
  console.log('🧹 Deleting existing data...');
  const tables = ['predictions', 'prediction_posts', 'comments', 'likes', 'draws', 'users'];
  for (const table of tables) {
    const { error } = await supabaseAdmin.from(table).delete().neq('id', '00000000-0000-0000-0000-000000000000');
    if (error) console.error(`Error deleting from ${table}:`, error.message);
  }
  // Auth usersの削除 (よりクリーンな状態にするため)
  const { data: { users: authUsers } } = await supabaseAdmin.auth.admin.listUsers();
  for (const user of authUsers) {
    if (user.email !== 'test@example.com') { // 保護したいユーザーがいれば指定
      await supabaseAdmin.auth.admin.deleteUser(user.id);
    }
  }
  console.log('✅ Data deleted.');

  // 2. Create Users
  console.log(`👤 Creating ${USER_COUNT} users...`);
  const createdUserIds: string[] = [];
  for (let i = 0; i < USER_COUNT; i++) {
    const email = faker.internet.email();
    const password = 'password123';
    const { data: authData, error: authError } = await supabaseAdmin.auth.signUp({ email, password });
    if (authError || !authData.user) {
      console.error(`Failed to create auth user ${i + 1}:`, authError?.message);
      continue;
    }
    const userId = authData.user.id;
    createdUserIds.push(userId);

    const { error: userError } = await supabaseAdmin.from('users').insert({
      id: userId,
      email: email,
      username: faker.internet.userName(),
      displayName: faker.person.fullName(),
      bio: faker.lorem.sentence(),
    });
    if (userError) console.error(`Failed to create db user ${i + 1}:`, userError.message);
  }
  console.log(`✅ ${createdUserIds.length} users created.`);

  // 3. Create Draws
  console.log('🎲 Creating draws...');
  const createdDrawIds: { id: string, type: string }[] = [];
  let drawNumberCounter = { LOTO6: 1800, NUMBERS4: 6300, NUMBERS3: 6300 };
  for (let i = -365; i < 5; i++) { // 過去1年分 + 未来5日分
    const date = new Date();
    date.setDate(date.getDate() + i);
    const day = date.getDay(); // 0:Sun, 1:Mon, ..., 6:Sat

    const createDraw = async (type: 'LOTO6' | 'NUMBERS4' | 'NUMBERS3') => {
      const { data, error } = await supabaseAdmin.from('draws').insert({
        lotteryType: type,
        drawNumber: drawNumberCounter[type]++,
        drawDate: date.toISOString(),
      }).select('id').single();
      if (error) console.error(`Failed to create draw for ${type}:`, error.message);
      if (data) createdDrawIds.push({ id: data.id, type });
    };

    if (day === 1 || day === 4) { // 月・木
      await createDraw('LOTO6');
    }
    if (day >= 1 && day <= 5) { // 月〜金
      await createDraw('NUMBERS4');
      await createDraw('NUMBERS3');
    }
  }
  console.log(`✅ ${createdDrawIds.length} draws created.`);

  // 4. Create Prediction Posts
  console.log(`✍️ Creating ${PREDICTION_POST_COUNT} prediction posts...`);
  for (let i = 0; i < PREDICTION_POST_COUNT; i++) {
    const randomUser = getRandomElement(createdUserIds);
    const randomDraw = getRandomElement(createdDrawIds);

    const { data: post, error: postError } = await supabaseAdmin.from('prediction_posts').insert({
      userId: randomUser,
      drawId: randomDraw.id,
    }).select('id').single();

    if (postError || !post) {
      console.error(`Failed to create prediction post ${i + 1}:`, postError?.message);
      continue;
    }

    const predictionCount = getRandomInt(1, 5);
    const predictions = [];
    for (let j = 0; j < predictionCount; j++) {
      let numbers;
      if (randomDraw.type === 'LOTO6') {
        numbers = generateLoto6Numbers();
      } else if (randomDraw.type === 'NUMBERS4') {
        numbers = generateNumbers(4);
      } else {
        numbers = generateNumbers(3);
      }
      predictions.push({ predictionPostId: post.id, numbers: { numbers } });
    }
    const { error: predError } = await supabaseAdmin.from('predictions').insert(predictions);
    if (predError) console.error(`Failed to create predictions for post ${post.id}:`, predError.message);
  }
  console.log(`✅ ${PREDICTION_POST_COUNT} prediction posts created.`);

  console.log(' seeding finished! 🎉');
}

main().catch(e => {
  console.error('An error occurred during seeding:', e);
  process.exit(1);
});
