import { Hono } from 'hono';
import * as drawService from '../services/drawService';

export const draws = new Hono();

// 抽選情報の一覧を取得
draws.get('/', async (c) => {
  const { lotteryType, page, limit } = c.req.query();
  const drawsData = await drawService.getDraws(lotteryType, page, limit);
  return c.json(drawsData);
});

// 開催予定の抽選情報を取得
draws.get('/upcoming', async (c) => {
  const upcomingDraws = await drawService.getUpcomingDraws();
  return c.json(upcomingDraws);
});

// 特定の抽選情報を取得
draws.get('/:drawId', async (c) => {
  const { drawId } = c.req.param();
  const draw = await drawService.getDrawById(drawId);
  if (!draw) {
    return c.json({ error: 'Draw not found' }, 404);
  }
  return c.json(draw);
});
