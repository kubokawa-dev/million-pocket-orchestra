import { supabase } from '../lib/supabase';

/**
 * 新規ユーザーを登録する
 */
export const signUp = async (email: string, password: string, username: string) => {
  // 1. Supabase Authにユーザーを作成
  const { data: authData, error: authError } = await supabase.auth.signUp({
    email,
    password,
  });

  if (authError) {
    throw new Error(authError.message);
  }
  if (!authData.user) {
    throw new Error('Failed to create user in Supabase.');
  }

  // 2. ローカルのUserテーブルにユーザー情報を同期
  const { data: newUser, error: dbError } = await supabase
    .from('users')
    .insert({
      id: authData.user.id, // SupabaseのIDを主キーとして使用
      email,
      username,
    })
    .select()
    .single();

  if (dbError) {
    console.error('Failed to sync user to local DB:', dbError);
    // Cleanup: delete the created Supabase auth user
    // const { error: deleteError } = await supabase.auth.admin.deleteUser(authData.user.id);
    // if (deleteError) console.error('Failed to clean up Supabase user:', deleteError);
    throw new Error('Failed to save user data.');
  }

  return {
    session: authData.session,
    user: newUser,
  };
}

/**
 * ログイン処理
 */
export const login = async (email: string, password: string) => {
  const { data, error } = await supabase.auth.signInWithPassword({
    email,
    password,
  });

  if (error) {
    throw new Error(error.message);
  }
  if (!data.session) {
    throw new Error('Login failed, no session returned.');
  }

  // ローカルDBのユーザー情報を取得して返すことも可能
  const { data: user } = await supabase
    .from('users')
    .select('*')
    .eq('id', data.user.id)
    .single();

  return {
    session: data.session,
    user,
  };
};
