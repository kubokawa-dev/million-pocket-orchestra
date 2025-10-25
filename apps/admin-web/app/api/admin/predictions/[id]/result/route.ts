import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@million-pocket/database';
import { requireAuth } from '@/lib/auth';

export async function PATCH(
  request: NextRequest,
  { params }: { params: Promise<{ id: string }> }
) {
  try {
    await requireAuth();
    // TODO: Add admin role check
    const { id } = await params;
    const body = await request.json();

    const prediction = await prisma.prediction.update({
      where: { id },
      data: {
        actualDrawNumber: body.actualDrawNumber,
        actualNumbers: body.actualNumbers,
        actualBonusNumber: body.actualBonusNumber,
        hitStatus: body.hitStatus,
        hitCount: body.hitCount,
      },
    });

    return NextResponse.json(prediction);
  } catch (error) {
    console.error('Error updating prediction result:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
