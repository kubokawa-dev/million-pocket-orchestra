import { NextRequest, NextResponse } from 'next/server';
import { createAdminClient } from '@/lib/supabase';
import { requireAdmin } from '@/lib/auth';

export async function GET(request: NextRequest) {
  try {
    await requireAdmin(); // 管理者権限チェック
    
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('pageSize') || '20');
    const includeHidden = searchParams.get('includeHidden') === 'true';

    const supabase = createAdminClient();

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
      .order('createdAt', { ascending: false })
      .range((page - 1) * pageSize, page * pageSize - 1);

    if (!includeHidden) {
      query = query.eq('isHidden', false);
    }

    const { data: predictions, error: predictionsError } = await query;

    if (predictionsError) {
      throw predictionsError;
    }

    // 総数を取得
    let countQuery = supabase
      .from('predictions')
      .select('*', { count: 'exact', head: true });

    if (!includeHidden) {
      countQuery = countQuery.eq('isHidden', false);
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
    console.error('Error fetching admin predictions:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    if (error instanceof Error && error.message === 'Admin access required') {
      return NextResponse.json({ message: 'Admin access required' }, { status: 403 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}