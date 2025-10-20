import { PrismaClient } from '@prisma/client'

const prisma = new PrismaClient()

async function seedMLData() {
  console.log('MLデータのシード開始...')

  try {
    // Numbers4 ML Data
    console.log('\nNumbers4 MLデータを挿入中...')
    
    // Model Events
    await prisma.numbers4ModelEvent.upsert({
      where: { id: 1 },
      update: {},
      create: {
        id: 1,
        event_ts: '2025-10-17T14:53:41.292259+00:00',
        actual_number: '0000',
        predictions: '[]',
        hit_exact: 0,
        top_match: null,
        max_position_hits: 0,
        notes: 'Model state restored from numbers4/model_state.json'
      }
    })

    // Numbers3 ML Data
    console.log('Numbers3 MLデータを挿入中...')
    
    await prisma.numbers3ModelEvent.upsert({
      where: { id: 1 },
      update: {},
      create: {
        id: 1,
        event_ts: '2025-10-18T05:44:49.062417+00:00',
        actual_number: '123',
        predictions: '["123", "456", "789", "012", "345"]',
        hit_exact: 1,
        top_match: '123',
        max_position_hits: 3,
        notes: 'テスト用の学習イベント'
      }
    })

    // Loto6 ML Data
    console.log('Loto6 MLデータを挿入中...')
    
    await prisma.loto6ModelEvent.upsert({
      where: { id: 1 },
      update: {},
      create: {
        id: 1,
        event_ts: '2025-10-18T06:00:34.138906+00:00',
        actual_number: '123456',
        predictions: '["123456", "234567", "345678", "456789", "567890"]',
        hit_exact: 1,
        top_match: '123456',
        max_position_hits: 6,
        notes: 'テスト用の学習イベント'
      }
    })

    await prisma.loto6ModelEvent.upsert({
      where: { id: 2 },
      update: {},
      create: {
        id: 2,
        event_ts: '2025-10-18T06:02:07.055331+00:00',
        actual_number: '123456',
        predictions: '["123456", "234567", "345678", "456789", "567890"]',
        hit_exact: 1,
        top_match: '123456',
        max_position_hits: 6,
        notes: 'テスト用の学習イベント'
      }
    })

    // データ数を確認
    const numbers4Events = await prisma.numbers4ModelEvent.count()
    const numbers3Events = await prisma.numbers3ModelEvent.count()
    const loto6Events = await prisma.loto6ModelEvent.count()

    console.log('\n✅ MLデータのシード完了!')
    console.log(`Numbers4 Model Events: ${numbers4Events} 件`)
    console.log(`Numbers3 Model Events: ${numbers3Events} 件`)
    console.log(`Loto6 Model Events: ${loto6Events} 件`)

  } catch (error) {
    console.error('❌ MLデータシードエラー:', error)
    throw error
  } finally {
    await prisma.$disconnect()
  }
}

seedMLData()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
