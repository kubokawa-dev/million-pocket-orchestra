import { Hono } from 'hono';
import * as predictionService from '../services/predictionService';

export const predictions = new Hono();

// 予測投稿の一覧を取得
predictions.get('/', async (c) => {
  const params = c.req.query();
  const result = await predictionService.getPredictionPosts(params);
  return c.json(result);
});

// 新しい予測を投稿
predictions.post('/', async (c) => {
  const body = await c.req.json();
  // TODO: AuthGuard実装後は、認証情報からuserIdを取得する
  if (!body.userId || !body.drawId || !Array.isArray(body.predictions)) {
    return c.json({ error: 'Invalid request body' }, 400);
  }
  try {
    const newPost = await predictionService.createPredictionPost(body);
    return c.json(newPost, 201);
  } catch (error: any) {
    return c.json({ error: error.message }, 400);
  }
});

// 特定の予測投稿を取得
predictions.get('/:postId', async (c) => {
  const { postId } = c.req.param();
  const post = await predictionService.getPredictionPostById(postId);
  if (!post) {
    return c.json({ error: 'Post not found' }, 404);
  }
  return c.json(post);
});

// --- Social Features ---

// 投稿に「いいね」する
predictions.post('/:postId/likes', async (c) => {
  const { postId } = c.req.param();
  const { userId } = await c.req.json(); // TODO: Get userId from auth
  if (!userId) return c.json({ error: 'userId is required' }, 400);

  try {
    const result = await predictionService.likePredictionPost(postId, userId);
    return c.json(result, 201);
  } catch (error: any) {
    return c.json({ error: error.message }, 400);
  }
});

// 投稿の「いいね」を取り消す
predictions.delete('/:postId/likes', async (c) => {
  const { postId } = c.req.param();
  const { userId } = await c.req.json(); // TODO: Get userId from auth
  if (!userId) return c.json({ error: 'userId is required' }, 400);

  await predictionService.unlikePredictionPost(postId, userId);
  return c.json({ success: true }, 200);
});

// コメントを投稿する
predictions.post('/:postId/comments', async (c) => {
  const { postId } = c.req.param();
  const { userId, content } = await c.req.json(); // TODO: Get userId from auth
  if (!userId || !content) return c.json({ error: 'userId and content are required' }, 400);

  const newComment = await predictionService.createComment(postId, userId, content);
  return c.json(newComment, 201);
});
