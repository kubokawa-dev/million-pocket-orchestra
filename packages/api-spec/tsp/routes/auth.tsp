import "@typespec/http";
import "@typespec/rest";
import "../common/errors.tsp";
import "../models/user.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace MillionPocketAPI;

@doc("認証レスポンス")
model AuthResponse {
  @doc("Supabaseセッション情報")
  session?: {
    access_token: string;
    refresh_token: string;
    expires_in: int32;
    token_type: string;
  };
  
  @doc("ユーザー情報")
  user?: User;
}

@doc("サインアップリクエスト")
model SignupRequest {
  @doc("メールアドレス")
  email: string;
  
  @doc("パスワード（6文字以上）")
  @minLength(6)
  password: string;
  
  @doc("ユーザー名")
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
  @doc("新規ユーザー登録")
  @post
  @route("/signup")
  op signup(@body request: SignupRequest): {
    @statusCode _: 201;
    @body body: AuthResponse;
  } | BadRequestError;
  
  @doc("ログイン")
  @post
  @route("/login")
  op login(@body request: LoginRequest): AuthResponse | UnauthorizedError;
}
