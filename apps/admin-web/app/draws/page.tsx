import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function DrawsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">抽選結果管理</h1>
        <p className="text-muted-foreground">
          抽選結果の登録と管理を行います
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>ナンバーズ3</CardTitle>
            <CardDescription>
              ナンバーズ3の抽選結果を登録
            </CardDescription>
          </CardHeader>
          <CardContent>
            <button className="w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              抽選結果を登録
            </button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ナンバーズ4</CardTitle>
            <CardDescription>
              ナンバーズ4の抽選結果を登録
            </CardDescription>
          </CardHeader>
          <CardContent>
            <button className="w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              抽選結果を登録
            </button>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ロト6</CardTitle>
            <CardDescription>
              ロト6の抽選結果を登録
            </CardDescription>
          </CardHeader>
          <CardContent>
            <button className="w-full inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90">
              抽選結果を登録
            </button>
          </CardContent>
        </Card>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>最近の抽選結果</CardTitle>
          <CardDescription>
            最新の抽選結果を表示します
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <p>抽選結果データを読み込み中...</p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
