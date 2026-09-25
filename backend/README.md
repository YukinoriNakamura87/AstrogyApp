# バックエンド DB マイグレーション

## DDD構成

バックエンドは、業務ルールをFastAPIやSQLAlchemyから独立させる軽量なDDD構成です。

```text
app/
├── domain/          # Client・NatalChartなどの業務概念とRepository契約
├── application/     # 登録・一覧・チャート取得などのユースケース
├── infrastructure/  # PostgreSQL/SQLAlchemyとKerykeionの実装
├── presentation/    # HTTPリクエスト・レスポンスの型
└── main.py          # FastAPIルートと各層を組み合わせる場所
```

依存方向は外側から内側へ向けます。`domain` はFastAPI、SQLAlchemy、Kerykeionを
知りません。たとえばチャート計算ライブラリを将来変更しても、業務概念とユースケースを
保ったまま `infrastructure` の実装を差し替えられます。

現段階では一人用ツールの規模に合わせ、集約や値オブジェクトを過剰に細分化していません。
セッションと解釈辞書は、それぞれの機能を実装するときに独立した業務概念として追加します。

開発コンテナ起動後、リポジトリのルートから実行します。

```bash
docker compose exec backend alembic upgrade head
docker compose exec backend alembic current
docker compose exec backend alembic check
```

`upgrade head` は既に適用済みのマイグレーションを再実行しません。スキーマ変更時は
`backend/migrations/versions/` に新しいリビジョンを追加してから適用します。
`check` は ORM と適用済みスキーマに未反映の差分がないか確認します。

初期スキーマには `clients`、`charts`、`chart_interpretation_memos` のみ含めます。
セッション記録と解釈辞書はそれぞれの機能実装時に追加します。

## 現在の API

- `GET /dashboard`：登録数、チャート数、最近登録したクライアントを返します。
- `GET /locations/search?q=Moriyama%2C%20Shiga`：Open-Meteoで出生地候補・座標・タイムゾーンを検索します。現在はローマ字入力を前提とします。
- `GET /clients`：クライアント一覧を返します。`search` と `sign` で絞り込めます。
- `GET /clients/{id}`：基本情報と保存済みネイタルチャートを返します。
- `POST /clients`：氏名、出生年月日・時刻、出生地、緯度・経度、IANA タイムゾーンを登録します。
- `GET /clients/{id}/chart`：初回のみ Kerykeion でネイタルチャートを計算し、以後は DB に保存した結果を返します。
- `GET /clients/{id}/chart/memos`：天体ごとの保存済みチャート解釈メモを返します。
- `PUT /clients/{id}/chart/memos`：指定した天体の解釈メモを上書きします。空文字を指定するとその天体のメモを削除します。
- `GET /clients/{id}/chart/lilly-score`：保存済みチャートを独立ライブラリへ渡し、リリー式採点結果を返します。
- `GET /clients/{id}/chart/summary`：保存済みチャートをMarkdown形式で返します。

チャート計算には出生時刻が必要です。時刻不明のクライアントは登録できますが、チャート取得時に 422 を返します。
計算は登録済み座標とタイムゾーンを使い、外部の地名検索 API には接続しません。

新規チャートではKerykeion 5.12が対応する23恒星に加え、Vertex、主要アラビック・パーツ、
四大小惑星、真リリス、平均ノードを補足情報として保存します。これらは通常チャートの
`active_points` には含めないため、既存のアスペクトや元素・三区分の集計には影響しません。
