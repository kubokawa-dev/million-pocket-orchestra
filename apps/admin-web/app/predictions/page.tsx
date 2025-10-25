import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function PredictionsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">予測一覧</h1>
        <p className="text-muted-foreground">
          ユーザーの予測投稿を管理します
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>予測投稿</CardTitle>
          <CardDescription>
            すべての予測投稿を表示します
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="space-y-4">
            <div className="text-center py-8 text-muted-foreground">
              <p>予測データを読み込み中...</p>
              <p className="text-sm mt-2">
                APIエンドポイントが正常に動作するまで、データは表示されません
              </p>
            </div>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
