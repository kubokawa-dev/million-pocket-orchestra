import { createClient } from '@supabase/supabase-js';
import { Hono } from 'hono';

const supabaseUrl = process.env.SUPABASE_URL;
const supabaseKey = process.env.SUPABASE_ANON_KEY;

if (!supabaseUrl || !supabaseKey) {
  throw new Error('Supabase URL and Key must be defined in environment variables');
}

export const supabase = createClient(supabaseUrl, supabaseKey);

// Hono contextにSupabaseクライアントを注入するための型定義
type Variables = {
  supabase: typeof supabase;
};

export type SupabaseClient = typeof supabase;

export const appWithSupabase = new Hono<{ Variables: Variables }>();
