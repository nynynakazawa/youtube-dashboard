type Metric = {
  label: string;
  value: string;
  trend: string;
  positive?: boolean;
};

const metrics: Metric[] = [
  { label: "\u7dcf\u518d\u751f\u56de\u6570", value: "12,430,981", trend: "\u524d\u6708\u6bd4 +8.2%", positive: true },
  { label: "\u767b\u9332\u8005\u6570", value: "254,103", trend: "\u76f4\u8fd130\u65e5 +3,421", positive: true },
  { label: "\u516c\u958b\u52d5\u753b\u6570", value: "486 \u672c", trend: "\u4eca\u6708 +12 \u672c" },
  { label: "\u5e73\u5747\u8996\u8074\u7dad\u6301\u7387", value: "58%", trend: "\u524d\u6708\u6bd4 -1.4%", positive: false },
];

const copy = {
  pageTitle: "YouTube \u30c1\u30e3\u30f3\u30cd\u30eb\u89e3\u6790\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9",
  pageLead: "\u30c1\u30e3\u30f3\u30cd\u30eb\u306e\u6210\u9577\u3084\u52d5\u753b\u306e\u30d1\u30d5\u30a9\u30fc\u30de\u30f3\u30b9\u3092\u53ef\u8996\u5316\u3059\u308b\u305f\u3081\u306e\u30c0\u30c3\u30b7\u30e5\u30dc\u30fc\u30c9\u3067\u3059\u3002",
  summaryTitle: "\u8996\u8074\u52d5\u5411\u306e\u30b5\u30de\u30ea\u30fc",
  summaryLead: "\u76f4\u8fd1 30 \u65e5\u9593\u306e\u4e3b\u8981\u6307\u6a19\u30b5\u30de\u30ea",
  summaryButton: "\u30ec\u30dd\u30fc\u30c8\u3092\u8868\u793a",
  topicsTitle: "\u4eba\u6c17\u30c8\u30d4\u30c3\u30af",
  topicShorts: "\u30b7\u30e7\u30fc\u30c8\u52d5\u753b\u5236\u4f5c",
  topicLive: "\u30e9\u30a4\u30d6\u914d\u4fe1",
  topicCollab: "\u30b3\u30e9\u30dc\u4f01\u753b",
  scheduleTitle: "\u52d5\u753b\u516c\u958b\u30b9\u30b1\u30b8\u30e5\u30fc\u30eb",
  scheduleLive: "\u9031\u672b\u30e9\u30a4\u30d6\u914d\u4fe1\u307e\u3068\u3081",
  scheduleReview: "\u65b0\u88fd\u54c1\u30ec\u30d3\u30e5\u30fc vol.12",
  activityTitle: "\u6700\u65b0\u30a2\u30af\u30c6\u30a3\u30d3\u30c6\u30a3",
  activityComments: "\u65b0\u3057\u3044\u30b3\u30e1\u30f3\u30c8 128 \u4ef6",
  activityCommentsDesc: "\u300c\u30b7\u30e7\u30fc\u30c8\u52d5\u753b\u64ae\u5f71\u8853\u300d\u3078\u306e\u53cd\u5fdc\u304c\u6025\u5897\u4e2d",
  activityCollab: "\u30b3\u30e9\u30dc\u4f9d\u983c\u304c 4 \u4ef6\u5c4a\u3044\u3066\u3044\u307e\u3059",
  activityCollabDesc: "\u672a\u5bfe\u5fdc\u306e\u30ea\u30af\u30a8\u30b9\u30c8\u3092\u78ba\u8a8d\u3057\u3066\u304f\u3060\u3055\u3044",
  activityReport: "\u30a2\u30ca\u30ea\u30c6\u30a3\u30af\u30b9\u30ec\u30dd\u30fc\u30c8\u3092\u66f4\u65b0",
  activityReportDesc: "\u8a73\u7d30\u306f\u300c\u30a2\u30ca\u30ea\u30c6\u30a3\u30af\u30b9\u300d\u30bf\u30d6\u3078",
  notificationsButton: "\u901a\u77e5\u30bb\u30f3\u30bf\u30fc\u3092\u958b\u304f",
};

export default function Home() {
  return (
    <div className="space-y-8">
      <section>
        <h1 className="text-2xl font-semibold text-gray-900">{copy.pageTitle}</h1>
        <p className="mt-2 text-sm text-gray-500">{copy.pageLead}</p>

        <div className="mt-8 grid gap-4 sm:grid-cols-2 xl:grid-cols-4">
          {metrics.map((metric) => (
            <article
              key={metric.label}
              className="rounded-2xl border border-gray-100 bg-white p-5 shadow-sm transition hover:-translate-y-0.5 hover:shadow-md"
            >
              <p className="text-xs font-medium uppercase tracking-wide text-gray-500">
                {metric.label}
              </p>
              <p className="mt-3 text-2xl font-semibold text-gray-900">{metric.value}</p>
              <p
                className={`mt-1 text-xs font-semibold ${
                  metric.positive === false
                    ? "text-red-500"
                    : metric.positive
                    ? "text-emerald-500"
                    : "text-gray-500"
                }`}
              >
                {metric.trend}
              </p>
            </article>
          ))}
        </div>
      </section>

      <section className="grid gap-6 lg:grid-cols-3">
        <article className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm lg:col-span-2">
          <div className="flex items-center justify-between">
            <div>
              <h2 className="text-lg font-semibold text-gray-900">{copy.summaryTitle}</h2>
              <p className="text-sm text-gray-500">{copy.summaryLead}</p>
            </div>
            <button className="rounded-full border border-gray-200 px-4 py-2 text-xs font-semibold text-gray-700 transition hover:border-youtube-red hover:text-youtube-red">
              {copy.summaryButton}
            </button>
          </div>
          <div className="mt-6 grid gap-4 sm:grid-cols-2">
            <div className="rounded-xl border border-gray-100 p-4">
              <p className="text-sm font-semibold text-gray-700">{copy.topicsTitle}</p>
              <ul className="mt-3 space-y-2 text-sm text-gray-600">
                <li className="flex items-center justify-between">
                  <span>{copy.topicShorts}</span>
                  <span className="text-gray-400">34%</span>
                </li>
                <li className="flex items-center justify-between">
                  <span>{copy.topicLive}</span>
                  <span className="text-gray-400">26%</span>
                </li>
                <li className="flex items-center justify-between">
                  <span>{copy.topicCollab}</span>
                  <span className="text-gray-400">19%</span>
                </li>
              </ul>
            </div>
            <div className="rounded-xl border border-gray-100 p-4">
              <p className="text-sm font-semibold text-gray-700">{copy.scheduleTitle}</p>
              <ul className="mt-3 space-y-3 text-sm text-gray-600">
                <li>
                  <p className="font-semibold text-gray-800">11 \u6708 15 \u65e5</p>
                  <p className="text-gray-500">{copy.scheduleLive}</p>
                </li>
                <li>
                  <p className="font-semibold text-gray-800">11 \u6708 18 \u65e5</p>
                  <p className="text-gray-500">{copy.scheduleReview}</p>
                </li>
              </ul>
            </div>
          </div>
        </article>

        <article className="rounded-2xl border border-gray-100 bg-white p-6 shadow-sm">
          <h2 className="text-lg font-semibold text-gray-900">{copy.activityTitle}</h2>
          <ul className="mt-4 space-y-4 text-sm text-gray-600">
            <li>
              <p className="font-semibold text-gray-800">{copy.activityComments}</p>
              <p className="text-gray-500">{copy.activityCommentsDesc}</p>
            </li>
            <li>
              <p className="font-semibold text-gray-800">{copy.activityCollab}</p>
              <p className="text-gray-500">{copy.activityCollabDesc}</p>
            </li>
            <li>
              <p className="font-semibold text-gray-800">{copy.activityReport}</p>
              <p className="text-gray-500">{copy.activityReportDesc}</p>
            </li>
          </ul>
          <button className="mt-6 w-full rounded-xl bg-youtube-red px-4 py-2 text-sm font-semibold text-white transition hover:bg-red-600">
            {copy.notificationsButton}
          </button>
        </article>
      </section>
    </div>
  );
}
