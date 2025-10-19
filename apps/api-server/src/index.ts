import dotenv from 'dotenv';
import { serve } from '@hono/node-server';
import { Hono } from 'hono';
import { cors } from 'hono/cors';

dotenv.config({ path: '.env.development' });
import { createClient, SupabaseClient } from '@supabase/supabase-js';

// データベースの型。将来的には 'supabase gen types' で生成したものを使う
type Database = any;

// 環境変数の型定義
type Env = {
  Variables: {
    supabase: SupabaseClient<Database>;
  };
};

const app = new Hono<Env>();

// CORSミドルウェアを適用
app.use('*', cors());

// Supabaseクライアントを初期化するミドルウェア
app.use('*', async (c, next) => {
  if (c.var.supabase) {
    return await next();
  }
  const supabase = createClient<Database>(
    process.env.SUPABASE_URL!,
    process.env.SUPABASE_ANON_KEY!
  );
  c.set('supabase', supabase);
  await next();
});

// ルート
app.get('/', (c) => {
  return c.text('Hello Hono!');
});

// /sample エンドポイント
app.get('/sample', async (c) => {
  const supabase = c.get('supabase');

  // loto6_drawsテーブルから最新の1件を取得するサンプル
  const { data, error } = await supabase
    .from('loto6_draws')
    .select('*')
    .order('draw_number', { ascending: false })
    .limit(1);

  if (error) {
    console.error('Supabase Error:', error);
    return c.json({ error: 'Failed to fetch data from Supabase' }, 500);
  }

  return c.json(data);
});

const port = 8787;
console.log(`Server is running on port ${port}`);

serve({
  fetch: app.fetch,
  port,
});
