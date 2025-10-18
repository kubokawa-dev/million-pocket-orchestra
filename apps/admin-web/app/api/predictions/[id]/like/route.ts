import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@million-pocket/database';
import { requireAuth } from '@/lib/auth';

export async function POST(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    const { id } = await params;
    const user = await requireAuth();

    await prisma.like.create({
      data: {
        userId: user.id,
        predictionId: id,
      },
    });

    return NextResponse.json({ message: 'Liked successfully' });
  } catch (error: any) {
    console.error('Error liking prediction:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    // Unique constraint violation
    if (error.code === 'P2002') {
      return NextResponse.json(
        { message: 'Already liked' },
        { status: 409 }
      );
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

    await prisma.like.delete({
      where: {
        userId_predictionId: {
          userId: user.id,
          predictionId: id,
        },
      },
    });

    return NextResponse.json({ message: 'Unliked successfully' });
  } catch (error) {
    console.error('Error unliking prediction:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
