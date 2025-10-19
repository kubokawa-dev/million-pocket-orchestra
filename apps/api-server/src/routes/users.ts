import { Hono } from 'hono';
import * as userService from '../services/userService';
import * as predictionService from '../services/predictionService';

export const users = new Hono();

// 特定のユーザーの公開プロフィールを取得
users.get('/:userId', async (c) => {
  const { userId } = c.req.param();
  const user = await userService.getUserProfile(userId);
  if (!user) {
    return c.json({ error: 'User not found' }, 404);
  }
  return c.json(user);
});

// 特定のユーザーの予測投稿履歴を取得
// predictionServiceのgetPredictionPostsを再利用する
users.get('/:userId/predictions', async (c) => {
  const { userId } = c.req.param();
  const params = { ...c.req.query(), userId };
  const result = await predictionService.getPredictionPosts(params);
  return c.json(result);
});

// 特定のユーザーの予測成績を分析
users.get('/:userId/analysis', async (c) => {
  const { userId } = c.req.param();
  try {
    const analysis = await userService.analyzeUserPredictions(userId);
    return c.json(analysis);
  } catch (error: any) {
    return c.json({ error: error.message }, 404);
  }
});
