import Link from "next/link";

const recentImports = [
  { id: "UC-001", name: "週末VLOGチャンネル", status: "完了", fetchedAt: "11/12 18:32" },
  { id: "UC-002", name: "ライブ配信まとめ", status: "進行中", fetchedAt: "11/13 09:10" },
  { id: "UC-003", name: "ハウツー解説", status: "エラー", fetchedAt: "11/13 21:47" },
];

export default function ChannelImportPage() {
  return (
    <div className="space-y-8">
      <header className="space-y-3">
        <p className="text-sm uppercase tracking-wide text-gray-500">channels / import</p>
        <h1 className="text-2xl font-semibold text-gray-900">チャンネルを取り込む</h1>
        <p className="text-sm text-gray-500">
          バックエンドで用意された API を利用してチャンネル情報を取り込みます。URL または ID を入力し、取り込みボタンを押すだけで
          即座に分析ビューへ反映されます。
        </p>
      </header>

      <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="space-y-2">
          <label htmlFor="channelInput" className="text-sm font-semibold text-gray-800">
            チャンネル URL / ID
          </label>
          <input
            id="channelInput"
            type="text"
            placeholder="https://www.youtube.com/@example または UCxxxx"
            className="w-full rounded-xl border border-gray-200 px-4 py-3 text-sm text-gray-800 placeholder:text-gray-400 focus:border-youtube-red focus:outline-none focus:ring-2 focus:ring-youtube-red/20"
            disabled
          />
        </div>
        <p className="mt-3 text-xs text-gray-500">
          ※ このフォームは UI のみを先行実装しています。バックエンド接続時に `lib/api.ts` の `importChannel` を呼び出す予定です。
        </p>
        <div className="mt-6 flex flex-wrap gap-3">
          <button
            type="button"
            disabled
            className="inline-flex items-center justify-center rounded-full bg-youtube-red px-5 py-2 text-sm font-semibold text-white opacity-60"
          >
            取り込み（近日対応）
          </button>
          <Link
            href="/channels"
            className="inline-flex items-center justify-center rounded-full border border-gray-200 px-5 py-2 text-sm font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red"
          >
            チャンネル一覧を見る
          </Link>
        </div>
      </section>

      <section className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h2 className="text-lg font-semibold text-gray-900">最近の取り込み状況</h2>
            <p className="text-sm text-gray-500">バックエンドのレスポンスと結合予定のダミーデータです。</p>
          </div>
          <Link
            href="/channels"
            className="text-sm font-semibold text-youtube-red transition hover:text-red-600"
          >
            すべて表示
          </Link>
        </div>
        <div className="mt-6 overflow-hidden rounded-xl border border-gray-100">
          <table className="min-w-full divide-y divide-gray-100 text-sm">
            <thead className="bg-gray-50 text-left text-xs font-semibold uppercase tracking-wide text-gray-500">
              <tr>
                <th className="px-4 py-3">チャンネル</th>
                <th className="px-4 py-3">ステータス</th>
                <th className="px-4 py-3">最終更新</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-gray-100 bg-white text-gray-700">
              {recentImports.map((item) => (
                <tr key={item.id}>
                  <td className="px-4 py-3">
                    <p className="font-semibold text-gray-900">{item.name}</p>
                    <p className="text-xs text-gray-500">{item.id}</p>
                  </td>
                  <td className="px-4 py-3">
                    <span
                      className={`inline-flex rounded-full px-3 py-1 text-xs font-semibold ${
                        item.status === "完了"
                          ? "bg-emerald-50 text-emerald-600"
                          : item.status === "エラー"
                          ? "bg-red-50 text-red-600"
                          : "bg-amber-50 text-amber-600"
                      }`}
                    >
                      {item.status}
                    </span>
                  </td>
                  <td className="px-4 py-3 text-sm text-gray-500">{item.fetchedAt}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </section>
    </div>
  );
}
