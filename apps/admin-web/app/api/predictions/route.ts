import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@million-pocket/database';
import { requireAuth } from '@/lib/auth';

export async function GET(request: NextRequest) {
  try {
    const searchParams = request.nextUrl.searchParams;
    const lotteryType = searchParams.get('lotteryType');
    const userId = searchParams.get('userId');
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('pageSize') || '20');

    const skip = (page - 1) * pageSize;

    const where: any = {
      isPublic: true,
      isHidden: false,
    };

    if (lotteryType) {
      where.lotteryType = lotteryType;
    }

    if (userId) {
      where.userId = userId;
    }

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
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(request: NextRequest) {
  try {
    const user = await requireAuth();
    const body = await request.json();

    const prediction = await prisma.prediction.create({
      data: {
        userId: user.id,
        lotteryType: body.lotteryType,
        numbers: body.numbers,
        bonusNumber: body.bonusNumber,
        confidence: body.confidence,
        reasoning: body.reasoning,
        targetDrawNumber: body.targetDrawNumber,
        targetDrawDate: body.targetDrawDate ? new Date(body.targetDrawDate) : null,
        isPublic: body.isPublic ?? true,
      },
      include: {
        user: {
          select: {
            id: true,
            username: true,
            displayName: true,
            avatarUrl: true,
          },
        },
      },
    });

    return NextResponse.json(prediction, { status: 201 });
  } catch (error) {
    console.error('Error creating prediction:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
