import "@typespec/http";
import "@typespec/rest";
import "../common/types.tsp";
import "../common/errors.tsp";
import "../models/prediction.tsp";
import "../models/social.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace MillionPocketAPI;

@tag("predictions")
@route("/predictions")
namespace Predictions {
  @doc("予測投稿一覧取得")
  @get
  op list(
    @query @doc("ページ番号") page?: int32,
    @query @doc("1ページあたりの件数") limit?: int32,
    @query @doc("ユーザーIDでフィルタ") userId?: string,
    @query @doc("抽選IDでフィルタ") drawId?: string,
    @query @doc("宝くじの種類でフィルタ") lotteryType?: LotteryType,
  ): PaginationResponse<PredictionPost>;
  
  @doc("新しい予測を投稿")
  @post
  op create(@body request: CreatePredictionPostRequest): {
    @statusCode _: 201;
    @body body: PredictionPost;
  } | BadRequestError;
  
  @doc("特定の予測投稿取得")
  @get
  @route("/{postId}")
  op get(@path postId: string): PredictionPost | NotFoundError;
  
  @doc("投稿に「いいね」する")
  @post
  @route("/{postId}/likes")
  op like(
    @path postId: string,
    @body request: LikeRequest,
  ): {
    @statusCode _: 201;
    @body body: Like;
  } | BadRequestError;
  
  @doc("「いいね」を取り消す")
  @delete
  @route("/{postId}/likes")
  op unlike(
    @path postId: string,
    @body request: LikeRequest,
  ): SuccessResponse;
  
  @doc("コメントを投稿する")
  @post
  @route("/{postId}/comments")
  op createComment(
    @path postId: string,
    @body request: CreateCommentRequest,
  ): {
    @statusCode _: 201;
    @body body: Comment;
  } | BadRequestError;
}
