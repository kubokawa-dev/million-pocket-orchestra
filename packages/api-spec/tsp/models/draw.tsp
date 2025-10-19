import "@typespec/http";
import "../common/types.tsp";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("抽選情報")
model Draw {
  @doc("抽選ID")
  id: string;
  
  @doc("宝くじの種類")
  lotteryType: LotteryType;
  
  @doc("回号")
  drawNumber: int32;
  
  @doc("抽選日時")
  drawDate: utcDateTime;
  
  @doc("当選番号（結果発表後に設定）")
  winningNumbers?: string;
  
  @doc("作成日時")
  createdAt?: utcDateTime;
  
  @doc("更新日時")
  updatedAt?: utcDateTime;
}
