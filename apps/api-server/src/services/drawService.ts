import { supabase } from '../lib/supabase';

// Prisma Clientが不要になるため、LotteryTypeをここで定義
// 本来は src/types/index.ts などに集約するのが望ましい
export enum LotteryType {
  NUMBERS3 = 'NUMBERS3',
  NUMBERS4 = 'NUMBERS4',
  LOTO6 = 'LOTO6',
  BINGO5 = 'BINGO5',
  LOTO7 = 'LOTO7',
  MINILOTO = 'MINILOTO',
}

/**
 * 抽選情報の一覧を取得する
 */
export const getDraws = async (lotteryType?: string, page: string = '1', limit: string = '20') => {
  const pageNum = parseInt(page, 10) || 1;
  const limitNum = parseInt(limit, 10) || 20;
  const from = (pageNum - 1) * limitNum;
  const to = from + limitNum - 1;

  let query = supabase.from('draws').select('*', { count: 'exact' });

  if (lotteryType) {
    query = query.eq('lotteryType', lotteryType);
  }

  const { data, error, count } = await query
    .order('drawDate', { ascending: false })
    .range(from, to);

  if (error) {
    console.error('Supabase error in getDraws:', error);
    throw new Error(error.message);
  }

  return {
    data: data || [],
    total: count || 0,
    page: pageNum,
    totalPages: Math.ceil((count || 0) / limitNum),
  };
};

/**
 * 各宝くじの、現在投稿可能な（最も近い未来の）抽選情報を取得する
 */
export const getUpcomingDraws = async () => {
  const now = new Date().toISOString();
  const lotteryTypes = Object.values(LotteryType);

  const queries = lotteryTypes.map(type =>
    supabase
      .from('draws')
      .select('*')
      .eq('lotteryType', type)
      .gte('drawDate', now)
      .order('drawDate', { ascending: true })
      .limit(1)
      .single()
  );

  const results = await Promise.all(queries);

  const upcomingDraws = results.reduce((acc, { data }) => {
    if (data) {
      acc[data.lotteryType as LotteryType] = data;
    }
    return acc;
  }, {} as Record<LotteryType, any>);

  return upcomingDraws;
};

/**
 * IDで特定の抽選情報を取得する
 * @param drawId - 抽選ID
 */
export const getDrawById = async (drawId: string) => {
  const { data, error } = await supabase
    .from('draws')
    .select('*')
    .eq('id', drawId)
    .single();

  if (error && error.code !== 'PGRST116') { // PGRST116: no rows found
    console.error('Supabase error in getDrawById:', error);
    throw new Error(error.message);
  }

  return data;
};

