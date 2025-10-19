import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("エラーレスポンス")
@error
model ErrorResponse {
  @doc("エラーメッセージ")
  error: string;
}

@doc("Not Found (404)")
@error
model NotFoundError is ErrorResponse {
  @statusCode _: 404;
}

@doc("Bad Request (400)")
@error
model BadRequestError is ErrorResponse {
  @statusCode _: 400;
}

@doc("Unauthorized (401)")
@error
model UnauthorizedError is ErrorResponse {
  @statusCode _: 401;
}
