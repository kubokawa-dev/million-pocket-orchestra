import { Card, CardContent, CardDescription, CardHeader, CardTitle } from '@/components/ui/card';

export default function UsersPage() {
  return (
    <div className="space-y-8">
      <div>
        <h1 className="text-3xl font-bold tracking-tight">ユーザー管理</h1>
        <p className="text-muted-foreground">
          ユーザーアカウントの管理を行います
        </p>
      </div>

      <Card>
        <CardHeader>
          <CardTitle>ユーザー一覧</CardTitle>
          <CardDescription>
            登録されているユーザーを表示します
          </CardDescription>
        </CardHeader>
        <CardContent>
          <div className="text-center py-8 text-muted-foreground">
            <p>ユーザーデータを読み込み中...</p>
            <p className="text-sm mt-2">
              Supabase認証が設定されると、ユーザー情報が表示されます
            </p>
          </div>
        </CardContent>
      </Card>
    </div>
  );
}
