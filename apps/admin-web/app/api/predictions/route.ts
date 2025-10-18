import { NextRequest, NextResponse } from 'next/server';
import { createPublicClient } from '@/lib/supabase';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const lotteryType = searchParams.get('lotteryType');
    const userId = searchParams.get('userId');
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('pageSize') || '20');

    const supabase = createPublicClient();

    // クエリの構築
    let query = supabase
      .from('predictions')
      .select(`
        *,
        users!predictions_userId_fkey (
          id,
          username,
          displayName,
          avatarUrl
        ),
        likes(count),
        comments(count)
      `)
      .eq('isPublic', true)
      .eq('isHidden', false)
      .order('createdAt', { ascending: false })
      .range((page - 1) * pageSize, page * pageSize - 1);

    if (lotteryType) {
      query = query.eq('lotteryType', lotteryType);
    }

    if (userId) {
      query = query.eq('userId', userId);
    }

    const { data: predictions, error: predictionsError } = await query;

    if (predictionsError) {
      throw predictionsError;
    }

    // 総数を取得
    let countQuery = supabase
      .from('predictions')
      .select('*', { count: 'exact', head: true })
      .eq('isPublic', true)
      .eq('isHidden', false);

    if (lotteryType) {
      countQuery = countQuery.eq('lotteryType', lotteryType);
    }

    if (userId) {
      countQuery = countQuery.eq('userId', userId);
    }

    const { count, error: countError } = await countQuery;

    if (countError) {
      throw countError;
    }

    return NextResponse.json({
      predictions: predictions?.map((p) => ({
        ...p,
        likeCount: p.likes?.[0]?.count || 0,
        commentCount: p.comments?.[0]?.count || 0,
      })) || [],
      total: count || 0,
      page,
      pageSize,
    });
  } catch (error) {
    console.error('Error fetching predictions:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const supabase = createPublicClient();
    
    // 認証チェック
    const { data: { user }, error: authError } = await supabase.auth.getUser();
    
    if (authError || !user) {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }

    const body = await request.json();

    const { data: prediction, error } = await supabase
      .from('predictions')
      .insert({
        userId: user.id,
        lotteryType: body.lotteryType,
        numbers: body.numbers,
        bonusNumber: body.bonusNumber,
        confidence: body.confidence,
        reasoning: body.reasoning,
        targetDrawNumber: body.targetDrawNumber,
        targetDrawDate: body.targetDrawDate ? new Date(body.targetDrawDate).toISOString() : null,
        isPublic: body.isPublic ?? true,
      })
      .select(`
        *,
        users!predictions_userId_fkey (
          id,
          username,
          displayName,
          avatarUrl
        )
      `)
      .single();

    if (error) {
      throw error;
    }

    return NextResponse.json(prediction, { status: 201 });
  } catch (error) {
    console.error('Error creating prediction:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
