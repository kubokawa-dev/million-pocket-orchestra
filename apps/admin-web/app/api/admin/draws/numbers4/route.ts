import { NextRequest, NextResponse } from 'next/server';
import { prisma } from '@million-pocket/database';
import { requireAuth } from '@/lib/auth';

export async function POST(request: NextRequest) {
  try {
    await requireAuth();
    // TODO: Add admin role check
    
    const body = await request.json();

    await prisma.numbers4Draw.create({
      data: {
        draw_number: body.draw_number,
        draw_date: body.draw_date,
        numbers: body.numbers,
      },
    });

    return NextResponse.json({ message: 'Numbers4 draw created successfully' });
  } catch (error: any) {
    console.error('Error creating Numbers4 draw:', error);
    if (error instanceof Error && error.message === 'Unauthorized') {
      return NextResponse.json({ message: 'Unauthorized' }, { status: 401 });
    }
    if (error.code === 'P2002') {
      return NextResponse.json(
        { message: 'Draw number already exists' },
        { status: 409 }
      );
    }
    return NextResponse.json(
      { message: 'Internal server error' },
      { status: 500 }
    );
  }
}
