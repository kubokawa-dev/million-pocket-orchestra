import "@typespec/http";
import "../common/types.tsp";
import "./user.tsp";
import "./draw.tsp";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("予測数字（宝くじ種類により形式が異なる）")
model PredictionNumbers {
  @doc("予測数字（LOTO6: 数値配列、NUMBERS3/4: 文字列）")
  numbers: int32[] | string;
}

@doc("個別の予測")
model Prediction {
  @doc("予測ID")
  id: string;
  
  @doc("予測投稿ID")
  predictionPostId: string;
  
  @doc("予測数字")
  numbers: PredictionNumbers;
}

@doc("予測投稿")
model PredictionPost {
  @doc("予測投稿ID")
  id: string;
  
  @doc("投稿したユーザーID")
  userId: string;
  
  @doc("対象の抽選ID")
  drawId: string;
  
  @doc("投稿日時")
  createdAt: utcDateTime;
  
  @doc("投稿したユーザー情報")
  user?: User;
  
  @doc("対象の抽選情報")
  draw?: Draw;
  
  @doc("この投稿に含まれる予測（最大5つ）")
  predictions?: Prediction[];
  
  @doc("いいね数")
  likesCount?: int32;
  
  @doc("コメント数")
  commentsCount?: int32;
}

@doc("予測投稿作成リクエスト")
model CreatePredictionPostRequest {
  @doc("ユーザーID（将来は認証トークンから取得）")
  userId: string;
  
  @doc("対象の抽選ID")
  drawId: string;
  
  @doc("予測数字のリスト（1〜5個）")
  @minItems(1)
  @maxItems(5)
  predictions: PredictionNumbers[];
}
