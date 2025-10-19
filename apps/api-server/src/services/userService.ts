import { supabase } from '../lib/supabase';

/**
 * ユーザーの公開プロフィールを取得する
 */
export const getUserProfile = async (userId: string) => {
  const { data, error } = await supabase
    .from('users')
    .select(`
      id, username, displayName, avatarUrl, bio, createdAt,
      prediction_posts(count)
    `)
    .eq('id', userId)
    .single();

  if (error) {
    console.error('Supabase error in getUserProfile:', error);
    throw new Error(error.message);
  }

  // 整形
  const userProfile = data ? {
    ...data,
    predictionPostsCount: data.prediction_posts[0]?.count || 0,
  } : null;
  
  // @ts-ignore
  delete userProfile?.prediction_posts;

  return userProfile;
};

/**
 * ユーザーの予測成績を分析する
 * @param userId - ユーザーID
 */
export const analyzeUserPredictions = async (userId: string) => {
  const { data: user, error: userError } = await supabase
    .from('users')
    .select('id, username')
    .eq('id', userId)
    .single();

  if (userError || !user) {
    throw new Error('User not found');
  }

  const { data: posts, error: postsError } = await supabase
    .from('prediction_posts')
    .select(`
      draw:draws!inner(lotteryType, winningNumbers),
      predictions(numbers)
    `)
    .eq('userId', userId);

  if (postsError) {
    throw new Error(postsError.message);
  }

  // TODO: 宝くじの種類ごとに、予測と当選番号を照合して的中率などを計算する
  //       複雑なロジックになるため、ここではダミーデータを返す
  const analysis = {
    loto6: {
      totalPredictions: posts.filter(p => (p.draw as any).lotteryType === 'LOTO6').length,
      totalWins: 0, // placeholder
      winRate: 0, // placeholder
      breakdown: [], // placeholder
    },
    numbers4: {
      totalPredictions: posts.filter(p => (p.draw as any).lotteryType === 'NUMBERS4').length,
      totalWins: 0, // placeholder
      winRate: 0, // placeholder
      breakdown: [], // placeholder
    },
    numbers3: {
      totalPredictions: posts.filter(p => (p.draw as any).lotteryType === 'NUMBERS3').length,
      totalWins: 0, // placeholder
      winRate: 0, // placeholder
      breakdown: [], // placeholder
    },
  };

  return {
    userId: user.id,
    username: user.username,
    analysis,
  };
};
