import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@million-pocket/database';
import { requireAuth } from '@/lib/auth';

export async function GET(request: NextRequest) {
  try {
    await requireAuth();
    // TODO: Add admin role check

    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('pageSize') || '20');
    const includeHidden = searchParams.get('includeHidden') === 'true';

    const skip = (page - 1) * pageSize;

    const where: any = includeHidden ? {} : { isHidden: false };

    const [predictions, total] = await Promise.all([
      prisma.prediction.findMany({
        where,
        skip,
        take: pageSize,
        orderBy: { createdAt: 'desc' },
        include: {
          user: {
            select: {
              id: true,
              username: true,
              displayName: true,
              avatarUrl: true,
            },
          },
          _count: {
            select: {
              likes: true,
              comments: true,
            },
          },
        },
      }),
      prisma.prediction.count({ where }),
    ]);

    return NextResponse.json({
      predictions: predictions.map((p) => ({
        ...p,
        likeCount: p._count.likes,
        commentCount: p._count.comments,
      })),
      total,
      page,
      pageSize,
    });
  } catch (error) {
    console.error('Error fetching predictions:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
