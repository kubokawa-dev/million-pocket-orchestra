import "@typespec/http";
import "@typespec/rest";
import "../common/types.tsp";
import "../common/errors.tsp";
import "../models/draw.tsp";

using TypeSpec.Http;
using TypeSpec.Rest;

namespace MillionPocketAPI;

@tag("draws")
@route("/draws")
namespace Draws {
  @doc("抽選情報一覧取得")
  @get
  op list(
    @query @doc("宝くじの種類でフィルタ") lotteryType?: LotteryType,
    @query @doc("ページ番号") page?: int32,
    @query @doc("1ページあたりの件数") limit?: int32,
  ): PaginationResponse<Draw>;
  
  @doc("開催予定の抽選情報取得")
  @get
  @route("/upcoming")
  op upcoming(): Draw[];
  
  @doc("特定の抽選情報取得")
  @get
  @route("/{drawId}")
  op get(@path drawId: string): Draw | NotFoundError;
}
