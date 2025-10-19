import { Hono } from 'hono';
import * as authService from '../services/authService';

export const auth = new Hono();

// 新規ユーザー登録
auth.post('/signup', async (c) => {
  const { email, password, username } = await c.req.json();
  if (!email || !password || !username) {
    return c.json({ error: 'Email, password, and username are required' }, 400);
  }

  try {
    const result = await authService.signUp(email, password, username);
    return c.json(result, 201);
  } catch (error: any) {
    return c.json({ error: error.message }, 400);
  }
});

// ログイン
auth.post('/login', async (c) => {
  const { email, password } = await c.req.json();
  if (!email || !password) {
    return c.json({ error: 'Email and password are required' }, 400);
  }

  try {
    const result = await authService.login(email, password);
    return c.json(result);
  } catch (error: any) {
    return c.json({ error: error.message }, 401);
  }
});
