import "@typespec/http";
import "@typespec/rest";
import "../common/types.tsp";
import "../common/errors.tsp";
import "../models/user.tsp";
import "../models/prediction.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace MillionPocketAPI;

@tag("users")
@route("/users")
namespace Users {
  @doc("ユーザープロフィール取得")
  @get
  @route("/{userId}")
  op getProfile(@path userId: string): User | NotFoundError;
  
  @doc("ユーザーの予測投稿一覧取得")
  @get
  @route("/{userId}/predictions")
  op getPredictions(
    @path userId: string,
    @query @doc("ページ番号") page?: int32,
    @query @doc("1ページあたりの件数") limit?: int32,
  ): PaginationResponse<PredictionPost>;
  
  @doc("ユーザーの予測成績分析取得")
  @get
  @route("/{userId}/analysis")
  op getAnalysis(@path userId: string): UserAnalysis | NotFoundError;
}
