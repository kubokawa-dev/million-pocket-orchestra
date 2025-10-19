import "@typespec/http";
import "@typespec/rest";
import "../common/errors.tsp";
import "../models/user.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace MillionPocketAPI;

@doc("""
認証レスポンス

サインアップまたはログイン時に返される認証情報。
Supabaseのセッショントークンとユーザー情報を含みます。
""")
model AuthResponse {
  @doc("""
  Supabaseセッション情報
  
  JWTアクセストークンとリフレッシュトークンを含むセッションデータ。
  access_tokenをAuthorizationヘッダーに設定してAPIリクエストを行います。
  """)
  session?: {
    @doc("アクセストークン（JWT）")
    access_token: string;
    
    @doc("リフレッシュトークン")
    refresh_token: string;
    
    @doc("有効期限（秒）")
    expires_in: int32;
    
    @doc("トークンタイプ（'Bearer'）")
    token_type: string;
  };
  
  @doc("""
  ユーザー情報
  
  認証成功時に返されるユーザーの詳細情報。
  """)
  user?: User;
}

@doc("""
サインアップリクエスト

新規ユーザー登録時のリクエストボディ。
""")
model SignupRequest {
  @doc("""
  メールアドレス
  
  ログインIDとして使用されます。
  有効なメール形式である必要があります。
  """)
  email: string;
  
  @doc("""
  パスワード
  
  6文字以上のパスワード。
  Supabaseのパスワードポリシーに準拠します。
  """)
  @minLength(6)
  password: string;
  
  @doc("""
  ユーザー名
  
  プロフィール表示に使用される一意の識別子。
  """)
  username: string;
}

@doc("ログインリクエスト")
model LoginRequest {
  @doc("メールアドレス")
  email: string;
  
  @doc("パスワード")
  password: string;
}

@tag("auth")
@route("/auth")
namespace Auth {
  @doc("""
  新規ユーザー登録
  
  メールアドレスとパスワードで新規アカウントを作成します。
  Supabase Authにより認証され、セッショントークンが発行されます。
  
  レスポンス:
  - 201: 登録成功、セッション情報を返却
  - 400: メール重複、パスワードポリシー違反など
  """)
  @post
  @route("/signup")
  op signup(
    @doc("""
    サインアップリクエスト
    
    メール、パスワード、ユーザー名を含む。
    """)
    @body request: SignupRequest
  ): {
    @statusCode _: 201;
    @body body: AuthResponse;
  } | BadRequestError;
  
  @doc("""
  ログイン
  
  メールアドレスとパスワードで認証し、セッショントークンを取得します。
  
  レスポンス:
  - 200: ログイン成功、セッション情報を返却
  - 401: メールまたはパスワードが不正
  """)
  @post
  @route("/login")
  op login(
    @doc("""
    ログインリクエスト
    
    メールとパスワードを含む。
    """)
    @body request: LoginRequest
  ): AuthResponse | UnauthorizedError;
}
