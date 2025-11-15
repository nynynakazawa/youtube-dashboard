export interface ApiError {
  code: number;
  message: string;
  details: unknown | null;
}

export interface ApiErrorResponse {
  error: ApiError;
}

