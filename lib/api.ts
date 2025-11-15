import type { Channel, ChannelImportResponse } from "@/types/channel";
import type { VideoListResponse } from "@/types/video";
import type { ApiErrorResponse } from "@/types/api";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_BASE_URL || "";

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
  return response.json();
}

export async function importChannel(
  channelUrlOrId: string
): Promise<ChannelImportResponse> {
  const response = await fetch(`${API_BASE_URL}/channels/import`, {
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
}): Promise<{ items: Channel[]; totalCount: number }> {
  const queryParams = new URLSearchParams();
  if (params?.q) queryParams.set("q", params.q);
  if (params?.limit) queryParams.set("limit", params.limit.toString());
  if (params?.offset) queryParams.set("offset", params.offset.toString());

  const response = await fetch(
    `${API_BASE_URL}/channels?${queryParams.toString()}`
  );

  return handleResponse<{ items: Channel[]; totalCount: number }>(response);
}

export async function getChannel(
  channelId: number
): Promise<ChannelImportResponse> {
  const response = await fetch(`${API_BASE_URL}/channels/${channelId}`);

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
  const queryParams = new URLSearchParams();
  if (params?.sort) queryParams.set("sort", params.sort);
  if (params?.limit) queryParams.set("limit", params.limit.toString());
  if (params?.offset) queryParams.set("offset", params.offset.toString());
  if (params?.from) queryParams.set("from", params.from);
  if (params?.to) queryParams.set("to", params.to);
  if (params?.minViews)
    queryParams.set("minViews", params.minViews.toString());

  const response = await fetch(
    `${API_BASE_URL}/channels/${channelId}/videos?${queryParams.toString()}`
  );

  return handleResponse<VideoListResponse>(response);
}

