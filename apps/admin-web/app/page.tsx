import Link from 'next/link';
import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function Dashboard() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">ダッシュボード</h1>
        <p className="text-muted-foreground">
          Million Pocket管理画面へようこそ
        </p>
      </div>

      <div className="grid gap-6 md:grid-cols-2 lg:grid-cols-3">
        <Card>
          <CardHeader>
            <CardTitle>予測管理</CardTitle>
            <CardDescription>
              ユーザーの予測投稿を管理します
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link
              href="/predictions"
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              予測一覧を見る
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>抽選結果</CardTitle>
            <CardDescription>
              抽選結果の登録と管理を行います
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link
              href="/draws"
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              抽選結果を管理
            </Link>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>ユーザー管理</CardTitle>
            <CardDescription>
              ユーザーアカウントの管理を行います
            </CardDescription>
          </CardHeader>
          <CardContent>
            <Link
              href="/users"
              className="inline-flex items-center justify-center rounded-md bg-primary px-4 py-2 text-sm font-medium text-primary-foreground hover:bg-primary/90"
            >
              ユーザー一覧を見る
            </Link>
          </CardContent>
        </Card>
      </div>

      <div className="grid gap-6 md:grid-cols-2">
        <Card>
          <CardHeader>
            <CardTitle>統計情報</CardTitle>
            <CardDescription>
              システムの利用状況を確認できます
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between">
                <span>総予測数</span>
                <span className="font-medium">-</span>
              </div>
              <div className="flex justify-between">
                <span>アクティブユーザー</span>
                <span className="font-medium">-</span>
              </div>
              <div className="flex justify-between">
                <span>今月の投稿数</span>
                <span className="font-medium">-</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>最近の活動</CardTitle>
            <CardDescription>
              最新のシステム活動を表示します
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-2 text-sm text-muted-foreground">
              <p>データを読み込み中...</p>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
