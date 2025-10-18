import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@million-pocket/database';
import { requireAuth } from '@/lib/auth';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const searchParams = request.nextUrl.searchParams;
    const page = parseInt(searchParams.get('page') || '1');
    const pageSize = parseInt(searchParams.get('pageSize') || '20');

    const skip = (page - 1) * pageSize;

    const [comments, total] = await Promise.all([
      prisma.comment.findMany({
        where: {
          predictionId: id,
          isHidden: false,
        },
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
        },
      }),
      prisma.comment.count({
        where: {
          predictionId: id,
          isHidden: false,
        },
      }),
    ]);

    return NextResponse.json({
      comments,
      total,
    });
  } catch (error) {
    console.error('Error fetching comments:', error);
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const user = await requireAuth();
    const body = await request.json();

    const comment = await prisma.comment.create({
      data: {
        userId: user.id,
        predictionId: id,
        content: body.content,
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

    return NextResponse.json(comment, { status: 201 });
  } catch (error) {
    console.error('Error creating comment:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
