import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("ユーザー情報")
model User {
  @doc("ユーザーID（Supabase auth.users.idと一致）")
  id: string;
  
  @doc("メールアドレス")
  email: string;
  
  @doc("ユーザー名")
  username?: string;
  
  @doc("表示名")
  displayName?: string;
  
  @doc("アバター画像URL")
  avatarUrl?: string;
  
  @doc("自己紹介")
  bio?: string;
  
  @doc("作成日時")
  createdAt?: utcDateTime;
  
  @doc("更新日時")
  updatedAt?: utcDateTime;
}

@doc("ユーザーの予測成績分析")
model UserAnalysis {
  @doc("ユーザーID")
  userId: string;
  
  @doc("ユーザー名")
  username: string;
  
  @doc("宝くじ種類別の分析結果")
  analysis: {
    loto6?: LotteryAnalysis;
    numbers4?: LotteryAnalysis;
    numbers3?: LotteryAnalysis;
  };
}

@doc("宝くじ種類別の成績分析")
model LotteryAnalysis {
  @doc("総予測数")
  totalPredictions: int32;
  
  @doc("当選数")
  totalWins: int32;
  
  @doc("的中率")
  winRate: float32;
  
  @doc("詳細内訳")
  breakdown: {};
}
