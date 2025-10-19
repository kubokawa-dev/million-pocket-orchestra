import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("""
ユーザー情報モデル

ユーザーの基本情報を表します。Supabase認証と連携し、
プロフィール情報を管理します。
""")
model User {
  @doc("""
  ユーザーID
  
  Supabase auth.users.idと一致するUUID形式の一意な識別子です。
  すべてのユーザー関連データの外部キーとして使用されます。
  """)
  id: string;
  
  @doc("""
  メールアドレス
  
  ユーザーの登録メールアドレス。ログイン時の識別子として使用されます。
  Supabase認証により管理され、一意性が保証されます。
  """)
  email: string;
  
  @doc("""
  ユーザー名
  
  ユーザーが設定する一意の識別子。他のユーザーから見える公開情報です。
  省略可能で、未設定の場合はメールアドレスの一部が使用される場合があります。
  """)
  username?: string;
  
  @doc("""
  表示名
  
  ユーザーのプロフィールに表示される名前。
  ユーザー名とは異なり、一意性は要求されません。
  """)
  displayName?: string;
  
  @doc("""
  アバター画像URL
  
  ユーザーのプロフィール画像のURL。
  Supabase StorageまたはGravatarなどの外部サービスのURLを格納します。
  """)
  avatarUrl?: string;
  
  @doc("""
  自己紹介
  
  ユーザーのプロフィール説明文。500文字以内の自由記述形式です。
  """)
  bio?: string;
  
  @doc("""
  作成日時
  
  ユーザーアカウントが作成された日時（UTC）。
  """)
  createdAt?: utcDateTime;
  
  @doc("""
  更新日時
  
  ユーザー情報が最後に更新された日時（UTC）。
  """)
  updatedAt?: utcDateTime;
}

@doc("""
ユーザーの予測成績分析

特定ユーザーの全宝くじ種類における予測成績を集計・分析した結果です。
的中率や傾向分析により、ユーザーの予測精度を評価します。
""")
model UserAnalysis {
  @doc("""
  ユーザーID
  
  分析対象のユーザーを識別するID。
  """)
  userId: string;
  
  @doc("""
  ユーザー名
  
  表示用のユーザー名。
  """)
  username: string;
  
  @doc("""
  宝くじ種類別の分析結果
  
  各宝くじ種類（LOTO6、NUMBERS3、NUMBERS4など）ごとの
  予測成績を格納します。データがない種類はundefinedとなります。
  """)
  analysis: {
    @doc("LOTO6の予測成績")
    loto6?: LotteryAnalysis;
    
    @doc("NUMBERS4の予測成績")
    numbers4?: LotteryAnalysis;
    
    @doc("NUMBERS3の予測成績")
    numbers3?: LotteryAnalysis;
  };
}

@doc("""
宝くじ種類別の成績分析

特定の宝くじ種類における予測成績の詳細データです。
総予測数、当選数、的中率などの統計情報を提供します。
""")
model LotteryAnalysis {
  @doc("""
  総予測数
  
  このユーザーが行った予測の総数（結果が確定したもののみ）。
  """)
  totalPredictions: int32;
  
  @doc("""
  当選数
  
  予測が的中した回数。部分的中も含む場合があります。
  """)
  totalWins: int32;
  
  @doc("""
  的中率
  
  当選数 ÷ 総予測数で算出される成功率（0.0〜1.0）。
  例: 0.15 = 15%の的中率
  """)
  winRate: float32;
  
  @doc("""
  詳細内訳
  
  将来的な拡張用フィールド。
  等級別当選数、よく選ぶ数字の分析などを格納予定。
  """)
  breakdown: {};
}
