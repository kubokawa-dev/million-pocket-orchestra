import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@million-pocket/database';
import { requireAuth } from '@/lib/auth';

export async function GET(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const user = await requireAuth();

    const prediction = await prisma.prediction.findUnique({
      where: { id },
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
    });

    if (!prediction) {
      return NextResponse.json(
        { message: 'Prediction not found' },
        { status: 404 }
      );
    }

    // Check if current user has liked this prediction
    const isLiked = await prisma.like.findUnique({
      where: {
        userId_predictionId: {
          userId: user.id,
          predictionId: id,
        },
      },
    });

    return NextResponse.json({
      ...prediction,
      likeCount: prediction._count.likes,
      commentCount: prediction._count.comments,
      isLikedByCurrentUser: !!isLiked,
    });
  } catch (error) {
    console.error('Error fetching prediction:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const user = await requireAuth();
    const body = await request.json();

    // Check if user owns this prediction
    const existing = await prisma.prediction.findUnique({
      where: { id },
      select: { userId: true },
    });

    if (!existing) {
      return NextResponse.json(
        { message: 'Prediction not found' },
        { status: 404 }
      );
    }

    if (existing.userId !== user.id) {
      return NextResponse.json(
        { message: 'Forbidden' },
        { status: 403 }
      );
    }

    const prediction = await prisma.prediction.update({
      where: { id },
      data: {
        numbers: body.numbers,
        bonusNumber: body.bonusNumber,
        confidence: body.confidence,
        reasoning: body.reasoning,
        isPublic: body.isPublic,
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

    return NextResponse.json(prediction);
  } catch (error) {
    console.error('Error updating prediction:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}

export async function DELETE(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const user = await requireAuth();

    const existing = await prisma.prediction.findUnique({
      where: { id },
      select: { userId: true },
    });

    if (!existing) {
      return NextResponse.json(
        { message: 'Prediction not found' },
        { status: 404 }
      );
    }

    if (existing.userId !== user.id) {
      return NextResponse.json(
        { message: 'Forbidden' },
        { status: 403 }
      );
    }

    await prisma.prediction.delete({
      where: { id },
    });

    return NextResponse.json({ message: 'Prediction deleted' });
  } catch (error) {
    console.error('Error deleting prediction:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
