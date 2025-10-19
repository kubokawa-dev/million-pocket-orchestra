import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("いいね")
model Like {
  @doc("いいねID")
  id: string;
  
  @doc("いいねしたユーザーID")
  userId: string;
  
  @doc("いいね対象の投稿ID")
  predictionPostId: string;
  
  @doc("いいね日時")
  createdAt: utcDateTime;
}

@doc("コメント")
model Comment {
  @doc("コメントID")
  id: string;
  
  @doc("コメントしたユーザーID")
  userId: string;
  
  @doc("コメント対象の投稿ID")
  predictionPostId: string;
  
  @doc("コメント内容")
  content: string;
  
  @doc("非表示フラグ")
  isHidden: boolean;
  
  @doc("コメント日時")
  createdAt: utcDateTime;
  
  @doc("更新日時")
  updatedAt: utcDateTime;
}

@doc("いいねリクエスト")
model LikeRequest {
  @doc("ユーザーID（将来は認証トークンから取得）")
  userId: string;
}

@doc("コメント作成リクエスト")
model CreateCommentRequest {
  @doc("ユーザーID（将来は認証トークンから取得）")
  userId: string;
  
  @doc("コメント内容")
  @minLength(1)
  @maxLength(500)
  content: string;
}
