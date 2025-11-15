import type { Channel, ChannelImportResponse, ChannelListResponse } from "@/types/channel";
import type { VideoListResponse } from "@/types/video";
import type { ApiErrorResponse } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";

function checkApiBaseUrl() {
  if (!API_BASE_URL) {
    const errorMessage = [
      "APIエンドポイントが設定されていません。",
      "",
      "以下の手順を確認してください:",
      "1. プロジェクトルートに .env.local ファイルを作成",
      "2. NEXT_PUBLIC_API_BASE_URL=https://your-api-url を記述",
      "3. 開発サーバーを再起動（環境変数の変更は再起動が必要）",
      "",
      "現在の値: " + (process.env.NEXT_PUBLIC_API_BASE_URL || "(未設定)"),
    ].join("\n");
    throw new Error(errorMessage);
  }
}

async function handleResponse<T>(response: Response): Promise<T> {
  if (!response.ok) {
    const error: ApiErrorResponse = await response.json().catch(() => ({
      error: {
        code: response.status,
        message: "リクエストに失敗しました",
        details: null,
      },
    }));
    throw new Error(error.error?.message || "リクエストに失敗しました");
  }
  
  const text = await response.text();
  if (!text) {
    throw new Error("レスポンスが空です");
  }
  
  try {
    return JSON.parse(text) as T;
  } catch (parseError) {
    console.error("JSONパースエラー:", parseError);
    console.error("レスポンステキスト:", text);
    throw new Error(`レスポンスのパースに失敗しました: ${text.substring(0, 100)}`);
  }
}

async function fetchWithErrorHandling(
  url: string,
  options?: RequestInit
): Promise<Response> {
  try {
    const response = await fetch(url, options);
    return response;
  } catch (error) {
    if (error instanceof TypeError && error.message === "Failed to fetch") {
      const errorDetails = [
        "APIサーバーに接続できません。",
        "",
        "考えられる原因:",
        "1. CORSエラー: API GatewayのCORS設定を確認してください",
        "2. ネットワークエラー: インターネット接続を確認してください",
        "3. API Gatewayがデプロイされていない可能性があります",
        "",
        `リクエストURL: ${url}`,
        `API Base URL: ${API_BASE_URL}`,
      ].join("\n");
      throw new Error(errorDetails);
    }
    throw error;
  }
}

export async function importChannel(
  channelUrlOrId: string
): Promise<ChannelImportResponse> {
  checkApiBaseUrl();
  const response = await fetchWithErrorHandling(`${API_BASE_URL}/channels/import`, {
    method: "POST",
    headers: {
      "Content-Type": "application/json",
    },
    body: JSON.stringify({ channelUrlOrId }),
  });

  return handleResponse<ChannelImportResponse>(response);
}

export async function getChannels(params?: {
  q?: string;
  limit?: number;
  offset?: number;
}): Promise<ChannelListResponse> {
  checkApiBaseUrl();
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.set("q", params.q);
  if (params?.limit) queryParams.set("limit", params.limit.toString());
  if (params?.offset) queryParams.set("offset", params.offset.toString());

  const url = `${API_BASE_URL}/channels${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;
  const response = await fetchWithErrorHandling(url);

  return handleResponse<ChannelListResponse>(response);
}

export async function getChannel(
  channelId: number
): Promise<ChannelImportResponse> {
  checkApiBaseUrl();
  const response = await fetchWithErrorHandling(`${API_BASE_URL}/channels/${channelId}`);

  return handleResponse<ChannelImportResponse>(response);
}

export async function getChannelVideos(
  channelId: number,
  params?: {
    sort?: string;
    limit?: number;
    offset?: number;
    from?: string;
    to?: string;
    minViews?: number;
  }
): Promise<VideoListResponse> {
  checkApiBaseUrl();
  const queryParams = new URLSearchParams();
  if (params?.sort) queryParams.set("sort", params.sort);
  if (params?.limit) queryParams.set("limit", params.limit.toString());
  if (params?.offset) queryParams.set("offset", params.offset.toString());
  if (params?.from) queryParams.set("from", params.from);
  if (params?.to) queryParams.set("to", params.to);
  if (params?.minViews)
    queryParams.set("minViews", params.minViews.toString());

  const url = `${API_BASE_URL}/channels/${channelId}/videos${queryParams.toString() ? `?${queryParams.toString()}` : ""}`;
  const response = await fetchWithErrorHandling(url);

  return handleResponse<VideoListResponse>(response);
}

