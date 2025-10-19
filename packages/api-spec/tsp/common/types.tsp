import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("宝くじの種類")
enum LotteryType {
  @doc("ナンバーズ3") NUMBERS3,
  @doc("ナンバーズ4") NUMBERS4,
  @doc("ロト6") LOTO6,
  @doc("ビンゴ5") BINGO5,
  @doc("ロト7") LOTO7,
  @doc("ミニロト") MINILOTO,
}

@doc("ページネーションレスポンス")
model PaginationResponse<T> {
  @doc("ページ内のアイテム")
  items: T[];
  
  @doc("総件数")
  total: int32;
  
  @doc("現在のページ番号")
  page: int32;
  
  @doc("1ページあたりの件数")
  limit: int32;
}

@doc("成功レスポンス")
model SuccessResponse {
  @doc("成功フラグ")
  success: boolean;
}
