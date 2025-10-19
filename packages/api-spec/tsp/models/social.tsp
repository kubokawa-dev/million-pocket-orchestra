import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("""
いいね

予測投稿に対するユーザーの「いいね」を表します。
1ユーザーは1つの投稿に対して1回のみいいねできます。
""")
model Like {
  @doc("""
  いいねID
  
  いいねを一意に識別するID。
  """)
  id: string;
  
  @doc("""
  いいねしたユーザーID
  
  いいねを行ったユーザーのID。
  """)
  userId: string;
  
  @doc("""
  いいね対象の投稿ID
  
  いいねされた予測投稿のID。
  """)
  predictionPostId: string;
  
  @doc("""
  いいね日時
  
  いいねが行われた日時（UTC）。
  """)
  createdAt: utcDateTime;
}

@doc("""
コメント

予測投稿に対するユーザーのコメントを表します。
他のユーザーとの交流やフィードバックを目的とします。
""")
model Comment {
  @doc("""
  コメントID
  
  コメントを一意に識別するID。
  """)
  id: string;
  
  @doc("""
  コメントしたユーザーID
  
  コメントを投稿したユーザーのID。
  """)
  userId: string;
  
  @doc("""
  コメント対象の投稿ID
  
  コメントされた予測投稿のID。
  """)
  predictionPostId: string;
  
  @doc("""
  コメント内容
  
  実際のコメントテキスト。
  1〜500文字の範囲で入力可能です。
  """)
  content: string;
  
  @doc("""
  非表示フラグ
  
  管理者によって非表示にされたコメントの場合true。
  不適切なコメントのモデレーションに使用されます。
  """)
  isHidden: boolean;
  
  @doc("""
  コメント日時
  
  コメントが投稿された日時（UTC）。
  """)
  createdAt: utcDateTime;
  
  @doc("""
  更新日時
  
  コメントが最後に編集された日時（UTC）。
  現在は編集機能未実装のため、createdAtと同じ値。
  """)
  updatedAt: utcDateTime;
}

@doc("""
いいねリクエスト

予測投稿にいいねを追加・削除する際のリクエストボディ。
""")
model LikeRequest {
  @doc("""
  ユーザーID
  
  いいねを行うユーザーのID。
  将来的には認証トークンから自動取得予定。
  """)
  userId: string;
}

@doc("""
コメント作成リクエスト

予測投稿にコメントを追加する際のリクエストボディ。
""")
model CreateCommentRequest {
  @doc("""
  ユーザーID
  
  コメントを投稿するユーザーのID。
  将来的には認証トークンから自動取得予定。
  """)
  userId: string;
  
  @doc("""
  コメント内容
  
  投稿するコメントのテキスト。
  1文字以上500文字以内である必要があります。
  """)
  @minLength(1)
  @maxLength(500)
  content: string;
}
