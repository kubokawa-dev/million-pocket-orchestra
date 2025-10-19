import { supabase } from '../lib/supabase';
import { LotteryType } from './drawService'; // drawServiceからLotteryTypeをインポート

// --- Types ---
type PredictionInput = {
  numbers: number[];
};

type CreatePredictionPostInput = {
  userId: string;
  drawId: string;
  predictions: PredictionInput[];
};

type GetPredictionPostsParams = {
  lotteryType?: string;
  userId?: string;
  page?: string;
  limit?: string;
};

// --- Service Functions ---

/**
 * 予測投稿を作成する
 */
export const createPredictionPost = async (input: CreatePredictionPostInput) => {
  const { userId, drawId, predictions } = input;

  if (predictions.length === 0 || predictions.length > 5) {
    throw new Error('A post must contain between 1 and 5 predictions.');
  }

  // 1. Create the main post
  const { data: postData, error: postError } = await supabase
    .from('prediction_posts')
    .insert({ userId, drawId })
    .select()
    .single();

  if (postError) {
    console.error('Supabase error creating post:', postError);
    throw new Error(postError.message);
  }

  // 2. Create the individual predictions linked to the main post
  const predictionData = predictions.map(p => ({
    predictionPostId: postData.id,
    numbers: p.numbers,
  }));

  const { error: predictionsError } = await supabase
    .from('predictions')
    .insert(predictionData);

  if (predictionsError) {
    // Cleanup: delete the created post if predictions fail
    console.error('Supabase error creating predictions:', predictionsError);
    await supabase.from('prediction_posts').delete().eq('id', postData.id);
    throw new Error(predictionsError.message);
  }

  return { ...postData, predictions: predictionData };
};

/**
 * 予測投稿の一覧を取得する
 */
export const getPredictionPosts = async (params: GetPredictionPostsParams) => {
  const { lotteryType, userId, page = '1', limit = '20' } = params;
  const pageNum = parseInt(page, 10) || 1;
  const limitNum = parseInt(limit, 10) || 20;
  const from = (pageNum - 1) * limitNum;
  const to = from + limitNum - 1;

  // SupabaseではJOINしたテーブルのフィルタリングが複雑なため、RPC (Remote Procedure Call)
  // を使うのが一般的ですが、ここではクライアントサイドでJOINとフィルタリングを模倣します。
  // パフォーマンスが重要な場合は、DBに関数を作成することを検討してください。

  let query = supabase.from('prediction_posts').select(`
    *,
    user:users!inner(id, username, avatarUrl),
    draw:draws!inner(id, lotteryType, drawNumber),
    predictions(numbers),
    likes(count),
    comments(count)
  `, { count: 'exact' });

  if (userId) {
    query = query.eq('userId', userId);
  }
  if (lotteryType) {
    query = query.eq('draw.lotteryType', lotteryType);
  }

  const { data, error, count } = await query
    .order('createdAt', { ascending: false })
    .range(from, to);

  if (error) {
    console.error('Supabase error in getPredictionPosts:', error);
    throw new Error(error.message);
  }

  // Supabaseのネストされた結果を整形
  const formattedData = data?.map(p => ({
    ...p,
    likes_count: p.likes[0]?.count || 0,
    comments_count: p.comments[0]?.count || 0,
  }))

  return {
    data: formattedData || [],
    total: count || 0,
    page: pageNum,
    totalPages: Math.ceil((count || 0) / limitNum),
  };
};

/**
 * IDで特定の予測投稿を取得する
 */
export const getPredictionPostById = async (postId: string) => {
  const { data, error } = await supabase
    .from('prediction_posts')
    .select(`
      *,
      user:users(id, username, avatarUrl),
      draw:draws(*),
      predictions(*),
      likes(userId),
      comments(*, user:users(id, username, avatarUrl))
    `)
    .eq('id', postId)
    .single();

  if (error && error.code !== 'PGRST116') {
    console.error('Supabase error in getPredictionPostById:', error);
    throw new Error(error.message);
  }

  return data;
};

/**
 * 投稿に「いいね」する
 */
export const likePredictionPost = async (postId: string, userId: string) => {
  const { data, error } = await supabase
    .from('likes')
    .insert({ userId, predictionPostId: postId });

  if (error) {
    // 23505 is the code for unique constraint violation
    if (error.code === '23505') {
      throw new Error('You have already liked this post.');
    }
    throw new Error(error.message);
  }
  return data;
};

/**
 * 投稿の「いいね」を取り消す
 */
export const unlikePredictionPost = async (postId: string, userId: string) => {
  const { error } = await supabase
    .from('likes')
    .delete()
    .eq('predictionPostId', postId)
    .eq('userId', userId);

  if (error) {
    throw new Error(error.message);
  }
};

/**
 * コメントを投稿する
 */
export const createComment = async (postId: string, userId: string, content: string) => {
  const { data, error } = await supabase
    .from('comments')
    .insert({ userId, predictionPostId: postId, content })
    .select('*, user:users(id, username, avatarUrl)')
    .single();

  if (error) {
    throw new Error(error.message);
  }
  return data;
};
