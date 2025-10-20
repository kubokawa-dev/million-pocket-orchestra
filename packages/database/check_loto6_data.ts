import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function checkLoto6Data() {
  const draws = await prisma.loto6Draw.findMany({
    take: 5,
    orderBy: { draw_number: 'asc' }
  })

  console.log('Loto6 Draws (最初の5件):')
  draws.forEach(draw => {
    console.log(`  Draw ${draw.draw_number}: ${draw.numbers} (bonus: ${draw.bonus_number})`)
  })

  const count = await prisma.loto6Draw.count()
  console.log(`\n合計: ${count}件`)

  await prisma.$disconnect()
}

checkLoto6Data()
