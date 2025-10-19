import "@typespec/http";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("""
宝くじの種類

対応している宝くじの種類を定義する列挙型。
各種類によって数字の形式やルールが異なります。
""")
enum LotteryType {
  @doc("ナンバーズ3: 3桁の数字を予測")
  NUMBERS3,
  @doc("ナンバーズ4: 4桁の数字を予測")
  NUMBERS4,
  @doc("ロト6: 1〜43から6個選択")
  LOTO6,
  @doc("ビンゴ5: 5×5ビンゴカード形式")
  BINGO5,
  @doc("ロト7: 1〜37から7個選択")
  LOTO7,
  @doc("ミニロト: 1〜31から5個選択")
  MINILOTO,
}

@doc("""
ページネーションレスポンス

一覧取得APIの標準的なページネーション形式
""")
model PaginationResponse<T> {
  @doc("ページ内のアイテム配列")
  items: T[];
  
  @doc("総件数（フィルタ後）")
  total: int32;
  
  @doc("現在のページ番号（1始まり）")
  page: int32;
  
  @doc("1ページあたりの最大件数")
  limit: int32;
}

@doc("成功レスポンス")
model SuccessResponse {
  @doc("成功フラグ")
  success: boolean;
}
