import "@typespec/http";
import "../common/types.tsp";

using TypeSpec.Http;

namespace MillionPocketAPI;

@doc("""
抽選情報

宝くじの抽選回に関する情報を表します。
抽選日時、当選番号などを管理し、予測投稿の対象となります。
""")
model Draw {
  @doc("""
  抽選ID
  
  抽選回を一意に識別するID。
  データベースの主キーとして使用されます。
  """)
  id: string;
  
  @doc("""
  宝くじの種類
  
  この抽選がどの宝くじ種類に属するかを示します。
  LOTO6、NUMBERS3、NUMBERS4、MINILOTO、BINGO5、LOTO7のいずれか。
  """)
  lotteryType: LotteryType;
  
  @doc("""
  回号
  
  抽選の回数を示す通し番号。
  例: LOTO6の第1850回の場合、1850が格納されます。
  """)
  drawNumber: int32;
  
  @doc("""
  抽選日時
  
  抽選が実施される（された）日時（UTC）。
  未来の日時の場合は開催予定、過去の場合は実施済みを表します。
  """)
  drawDate: utcDateTime;
  
  @doc("""
  当選番号
  
  抽選結果の当選番号。結果発表後に設定されます。
  形式: カンマ区切りの数字文字列（例: "1,10,22,33,40,41"）
  未発表の場合はnull。
  """)
  winningNumbers?: string;
  
  @doc("""
  作成日時
  
  この抽選情報がシステムに登録された日時（UTC）。
  """)
  createdAt?: utcDateTime;
  
  @doc("""
  更新日時
  
  この抽選情報が最後に更新された日時（UTC）。
  主に当選番号の設定時に更新されます。
  """)
  updatedAt?: utcDateTime;
}
