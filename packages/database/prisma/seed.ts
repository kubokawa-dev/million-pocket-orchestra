import { PrismaClient } from '@prisma/client'
import * as fs from 'fs'
import * as path from 'path'

const prisma = new PrismaClient()

interface DrawData {
  draw_number: number
  draw_date: string
  numbers: string
}

interface Loto6DrawData {
  draw_number: number
  draw_date: string
  numbers: string
  bonus_number: number
}

function extractDrawNumber(roundText: string): number | null {
  const match = roundText.match(/第(\d+)回/)
  return match ? parseInt(match[1]) : null
}

function parseNumbers3CSV(filePath: string): DrawData[] {
  const data: DrawData[] = []
  
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    const lines = content.split('\n')
    
    // ヘッダー行をスキップ
    for (let i = 1; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue
      
      const columns = line.split(',')
      
      if (columns.length >= 2) {
        const month = path.basename(filePath).replace('.csv', '').replace('2025', '')
        
        // 形式1: 回号,抽せん日,当せん番号 (202508以降)
        if (columns.length >= 3 && columns[0].includes('第') && columns[0].includes('回')) {
          const roundText = columns[0]
          const drawDate = columns[1]
          const numbers = columns[2]
          
          const drawNumber = extractDrawNumber(roundText)
          
          if (drawNumber && drawDate && numbers) {
            data.push({
              draw_number: drawNumber,
              draw_date: drawDate,
              numbers: numbers
            })
          }
        }
        // 形式2: 抽選日,当選番号 (202501-202507)
        else if (columns.length >= 2 && columns[0].includes('/')) {
          const drawDate = columns[0]
          const numbers = columns[1]
          
          // 月と行番号から抽選回数を推定
          const monthNum = parseInt(month)
          const drawNumber = (monthNum - 1) * 25 + i
          
          if (drawDate && numbers) {
            data.push({
              draw_number: drawNumber,
              draw_date: drawDate,
              numbers: numbers
            })
          }
        }
      }
    }
    
    console.log(`ファイル ${filePath} から ${data.length} 件のデータを読み込みました`)
    return data
    
  } catch (error) {
    console.error(`ファイル ${filePath} の読み込みエラー:`, error)
    return []
  }
}

function parseNumbers4CSV(filePath: string): DrawData[] {
  const data: DrawData[] = []
  
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    const lines = content.split('\n')
    
    for (const line of lines) {
      const trimmedLine = line.trim()
      if (!trimmedLine) continue
      
      const columns = trimmedLine.split(',')
      
      if (columns.length >= 3) {
        // 回号,抽せん日,当せん番号,その他のデータ...
        const roundText = columns[0]
        const drawDate = columns[1]
        const numbers = columns[2]
        
        const drawNumber = extractDrawNumber(roundText)
        
        if (drawNumber && drawDate && numbers) {
          data.push({
            draw_number: drawNumber,
            draw_date: drawDate,
            numbers: numbers
          })
        }
      }
    }
    
    console.log(`ファイル ${filePath} から ${data.length} 件のデータを読み込みました`)
    return data
    
  } catch (error) {
    console.error(`ファイル ${filePath} の読み込みエラー:`, error)
    return []
  }
}

async function seedNumbers3() {
  console.log('ナンバーズ3のデータをシード中...')
  
  const numbers3Dir = path.join(process.cwd(), '..', '..', 'numbers3')
  const csvFiles = fs.readdirSync(numbers3Dir)
    .filter(file => file.endsWith('.csv'))
    .sort()
    .map(file => path.join(numbers3Dir, file))
  
  let allData: DrawData[] = []
  
  for (const csvFile of csvFiles) {
    const data = parseNumbers3CSV(csvFile)
    allData = allData.concat(data)
  }
  
  console.log(`ナンバーズ3: 合計 ${allData.length} 件のデータを取得しました`)
  
  if (allData.length > 0) {
    // 既存データを削除
    await prisma.numbers3Draw.deleteMany()
    
    // データを挿入
    for (const item of allData) {
      await prisma.numbers3Draw.upsert({
        where: { draw_number: item.draw_number },
        update: {
          draw_date: item.draw_date,
          numbers: item.numbers
        },
        create: {
          draw_number: item.draw_number,
          draw_date: item.draw_date,
          numbers: item.numbers
        }
      })
    }
    
    console.log(`ナンバーズ3: ${allData.length} 件のデータを挿入しました`)
  }
}

async function seedNumbers4() {
  console.log('ナンバーズ4のデータをシード中...')
  
  const numbers4Dir = path.join(process.cwd(), '..', '..', 'numbers4')
  const csvFiles = fs.readdirSync(numbers4Dir)
    .filter(file => file.endsWith('.csv'))
    .sort()
    .map(file => path.join(numbers4Dir, file))
  
  let allData: DrawData[] = []
  
  for (const csvFile of csvFiles) {
    const data = parseNumbers4CSV(csvFile)
    allData = allData.concat(data)
  }
  
  console.log(`ナンバーズ4: 合計 ${allData.length} 件のデータを取得しました`)
  
  if (allData.length > 0) {
    // 既存データを削除
    await prisma.numbers4Draw.deleteMany()
    
    // データを挿入
    for (const item of allData) {
      await prisma.numbers4Draw.upsert({
        where: { draw_number: item.draw_number },
        update: {
          draw_date: item.draw_date,
          numbers: item.numbers
        },
        create: {
          draw_number: item.draw_number,
          draw_date: item.draw_date,
          numbers: item.numbers
        }
      })
    }
    
    console.log(`ナンバーズ4: ${allData.length} 件のデータを挿入しました`)
  }
}

function extractBonusNumber(bonusText: string): number | null {
  const match = bonusText.match(/\((\d+)\)/)
  return match ? parseInt(match[1]) : null
}

function parseLoto6CSV(filePath: string): Loto6DrawData[] {
  const data: Loto6DrawData[] = []
  
  try {
    const content = fs.readFileSync(filePath, 'utf-8')
    const lines = content.split('\n')
    
    for (let i = 0; i < lines.length; i++) {
      const line = lines[i].trim()
      if (!line) continue
      
      const columns = line.split(',')
      
      if (columns.length >= 9) {
        try {
          // 回号から抽選番号を抽出
          const drawNumber = extractDrawNumber(columns[0])
          if (!drawNumber) continue
          
          // 抽せん日
          const drawDate = columns[1]
          
          // 本数字（6個）
          const mainNumbers = []
          for (let j = 2; j < 8; j++) {
            if (j < columns.length && columns[j].match(/^\d+$/)) {
              mainNumbers.push(columns[j])
            }
          }
          
          if (mainNumbers.length !== 6) continue
          
          // ボーナス数字
          const bonusNumber = extractBonusNumber(columns[8])
          if (bonusNumber === null) continue
          
          // 本数字を文字列として結合
          const numbersStr = mainNumbers.join(',')
          
          data.push({
            draw_number: drawNumber,
            draw_date: drawDate,
            numbers: numbersStr,
            bonus_number: bonusNumber
          })
          
        } catch (error) {
          console.log(`行の解析エラー: ${line}, エラー: ${error}`)
          continue
        }
      }
    }
  } catch (error) {
    console.error(`ファイル読み込みエラー (${filePath}):`, error)
  }
  
  return data
}

async function seedLoto6() {
  console.log('ロト6のデータをシード中...')
  
  const loto6Dir = path.join(process.cwd(), '..', '..', 'loto6')
  
  if (!fs.existsSync(loto6Dir)) {
    console.log('loto6ディレクトリが見つかりません')
    return
  }
  
  const csvFiles = fs.readdirSync(loto6Dir)
    .filter(file => file.endsWith('.csv'))
    .sort()
  
  let allData: Loto6DrawData[] = []
  
  for (const file of csvFiles) {
    const filePath = path.join(loto6Dir, file)
    console.log(`ファイル ${file} から ${parseLoto6CSV(filePath).length} 件のデータを読み込みました`)
    const data = parseLoto6CSV(filePath)
    allData = allData.concat(data)
  }
  
  console.log(`ロト6: 合計 ${allData.length} 件のデータを取得しました`)
  
  if (allData.length > 0) {
    // データをupsertで挿入
    for (const item of allData) {
      await prisma.loto6Draw.upsert({
        where: { draw_number: item.draw_number },
        update: {
          draw_date: item.draw_date,
          numbers: item.numbers,
          bonus_number: item.bonus_number
        },
        create: {
          draw_number: item.draw_number,
          draw_date: item.draw_date,
          numbers: item.numbers,
          bonus_number: item.bonus_number
        }
      })
    }
    
    console.log(`ロト6: ${allData.length} 件のデータを挿入しました`)
  }
}

async function main() {
  console.log('データベースシード開始...')
  
  try {
    await seedNumbers3()
    await seedNumbers4()
    await seedLoto6()
    
    // 最終的なデータ数を確認
    const numbers3Count = await prisma.numbers3Draw.count()
    const numbers4Count = await prisma.numbers4Draw.count()
    const loto6Count = await prisma.loto6Draw.count()
    
    console.log('シード完了!')
    console.log(`ナンバーズ3: ${numbers3Count} 件`)
    console.log(`ナンバーズ4: ${numbers4Count} 件`)
    console.log(`ロト6: ${loto6Count} 件`)
    console.log(`合計: ${numbers3Count + numbers4Count + loto6Count} 件`)
    
  } catch (error) {
    console.error('シードエラー:', error)
    throw error
  } finally {
    await prisma.$disconnect()
  }
}

main()
  .catch((e) => {
    console.error(e)
    process.exit(1)
  })
