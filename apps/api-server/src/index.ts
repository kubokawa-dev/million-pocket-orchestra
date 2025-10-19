import dotenv from 'dotenv';
import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';
import { logger } from 'hono/logger';

// ルーターのインポート (後で作成)
import { auth } from './routes/auth';
import { draws } from './routes/draws';
import { predictions } from './routes/predictions';
import { users } from './routes/users';

dotenv.config({ path: `.env.${process.env.NODE_ENV || 'development'}` });

const app = new Hono();

// --- ミドルウェア ---
app.use('*', cors()); // CORSを許可
app.use('*', logger()); // リクエストロガー

// --- ルーティング ---
app.get('/', (c) => c.text('Million Pocket API'));

// 各機能のルーターを適用
app.route('/auth', auth);
app.route('/draws', draws);
app.route('/predictions', predictions);
app.route('/users', users);

// --- サーバー起動 ---
const port = Number(process.env.PORT) || 8787;
console.log(`Server is running on port ${port}`);

serve({
  fetch: app.fetch,
  port,
});

export default app;

