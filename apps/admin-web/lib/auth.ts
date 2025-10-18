import { createClient } from './supabase';
import { NextRequest } from 'next/server';

export interface AuthUser {
  id: string;
  email: string;
  role?: 'admin' | 'user';
}

// 認証が必要なAPI用のミドルウェア
export async function requireAuth(): Promise<AuthUser> {
  const supabase = await createClient();
  
  const { data: { user }, error } = await supabase.auth.getUser();
  
  if (error || !user) {
    throw new Error('Unauthorized');
  }
  
  return {
    id: user.id,
    email: user.email || '',
    role: 'user' // デフォルトは一般ユーザー
  };
}

// 管理者権限が必要なAPI用のミドルウェア
export async function requireAdmin(): Promise<AuthUser> {
  const user = await requireAuth();
  
  // 管理者権限のチェック（実際の実装では、ユーザーのメタデータや別テーブルで管理）
  // ここでは簡単にemailで判定（実際の運用では適切な権限管理を実装）
  const adminEmails = process.env.ADMIN_EMAILS?.split(',') || [];
  
  if (!adminEmails.includes(user.email)) {
    throw new Error('Admin access required');
  }
  
  return {
    ...user,
    role: 'admin'
  };
}

// リクエストから認証情報を取得
export async function getAuthFromRequest(request: NextRequest): Promise<AuthUser | null> {
  try {
    const supabase = await createClient();
    const { data: { user } } = await supabase.auth.getUser();
    
    if (!user) return null;
    
    return {
      id: user.id,
      email: user.email || '',
      role: 'user'
    };
  } catch {
    return null;
  }
}