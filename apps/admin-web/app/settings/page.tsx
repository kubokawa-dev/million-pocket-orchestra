import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function SettingsPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">設定</h1>
        <p className="text-muted-foreground">
          システムの設定を管理します
        </p>
      </div>

      <div className="grid gap-6">
        <Card>
          <CardHeader>
            <CardTitle>データベース設定</CardTitle>
            <CardDescription>
              データベース接続の設定
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>接続状態</span>
                <span className="text-green-600 font-medium">接続中</span>
              </div>
              <div className="flex justify-between items-center">
                <span>データベース</span>
                <span className="text-muted-foreground">PostgreSQL</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>API設定</CardTitle>
            <CardDescription>
              APIエンドポイントの設定
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>API URL</span>
                <span className="text-muted-foreground">http://localhost:3001/api</span>
              </div>
              <div className="flex justify-between items-center">
                <span>認証</span>
                <span className="text-muted-foreground">Supabase Auth</span>
              </div>
            </div>
          </CardContent>
        </Card>

        <Card>
          <CardHeader>
            <CardTitle>システム情報</CardTitle>
            <CardDescription>
              システムのバージョン情報
            </CardDescription>
          </CardHeader>
          <CardContent>
            <div className="space-y-4">
              <div className="flex justify-between items-center">
                <span>アプリバージョン</span>
                <span className="text-muted-foreground">1.0.0</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Next.js</span>
                <span className="text-muted-foreground">15.1.4</span>
              </div>
              <div className="flex justify-between items-center">
                <span>Prisma</span>
                <span className="text-muted-foreground">6.17.1</span>
              </div>
            </div>
          </CardContent>
        </Card>
      </div>
    </div>
  );
}
