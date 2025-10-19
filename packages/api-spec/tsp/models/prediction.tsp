import "@typespec/http";
import "../common/types.tsp";
import "./user.tsp";
import "./draw.tsp";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("""
予測数字

宝くじの種類によって異なる形式の予測数字を表現します。
- LOTO6系: 数値の配列（例: [1, 10, 22, 33, 40, 41]）
- NUMBERS3/4系: 文字列（例: "1234"）
""")
model PredictionNumbers {
  @doc("""
  予測数字
  
  宝くじ種類による形式:
  - LOTO6, MINILOTO, LOTO7: 数値配列
    例: [1, 10, 22, 33, 40, 41]
  - NUMBERS3: 3桁の数字文字列
    例: "123"
  - NUMBERS4: 4桁の数字文字列
    例: "1234"
  """)
  numbers: int32[] | string;
}

@doc("""
個別の予測

1つの予測数字の組み合わせを表します。
1回の予測投稿には最大5つの予測を含めることができます。
""")
model Prediction {
  @doc("""
  予測ID
  
  個別の予測を一意に識別するID。
  """)
  id: string;
  
  @doc("""
  予測投稿ID
  
  この予測が属する予測投稿のID。
  """)
  predictionPostId: string;
  
  @doc("""
  予測数字
  
  実際に予測した数字の組み合わせ。
  宝くじ種類により形式が異なります。
  """)
  numbers: PredictionNumbers;
}

@doc("""
予測投稿

ユーザーが特定の抽選回に対して行った予測のまとまりです。
最大5つの予測数字を含むことができ、他のユーザーに公開されます。
いいねやコメントを受け付けることができます。
""")
model PredictionPost {
  @doc("""
  予測投稿ID
  
  投稿を一意に識別するID。
  """)
  id: string;
  
  @doc("""
  投稿したユーザーID
  
  この予測を投稿したユーザーのID。
  """)
  userId: string;
  
  @doc("""
  対象の抽選ID
  
  予測対象となる抽選回のID。
  """)
  drawId: string;
  
  @doc("""
  投稿日時
  
  予測が投稿された日時（UTC）。
  抽選日時より前である必要があります。
  """)
  createdAt: utcDateTime;
  
  @doc("""
  投稿したユーザー情報
  
  投稿者の詳細情報。一覧取得時などに自動で含まれます。
  """)
  user?: User;
  
  @doc("""
  対象の抽選情報
  
  予測対象の抽選の詳細情報。一覧取得時などに自動で含まれます。
  """)
  draw?: Draw;
  
  @doc("""
  この投稿に含まれる予測
  
  最大5つの予測数字の配列。
  詳細取得時に含まれます。
  """)
  predictions?: Prediction[];
  
  @doc("""
  いいね数
  
  この投稿が受けた「いいね」の総数。
  """)
  likesCount?: int32;
  
  @doc("""
  コメント数
  
  この投稿に付けられたコメントの総数。
  """)
  commentsCount?: int32;
}

@doc("""
予測投稿作成リクエスト

新しい予測を投稿する際のリクエストボディ。
""")
model CreatePredictionPostRequest {
  @doc("""
  ユーザーID
  
  投稿するユーザーのID。
  将来的には認証トークンから自動取得予定。
  """)
  userId: string;
  
  @doc("""
  対象の抽選ID
  
  予測対象となる抽選回のID。
  存在する抽選IDである必要があります。
  """)
  drawId: string;
  
  @doc("""
  予測数字のリスト
  
  1〜5個の予測数字を含む配列。
  各予測は宝くじ種類に応じた形式である必要があります。
  """)
  @minItems(1)
  @maxItems(5)
  predictions: PredictionNumbers[];
}
