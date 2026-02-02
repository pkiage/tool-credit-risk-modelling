import type {
	HealthResponse,
	ModelMetadata,
	PersistResponse,
	PredictionRequest,
	PredictionResponse,
	TrainingConfig,
	TrainingResult,
} from "./types";

const API_BASE_URL = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
const DEFAULT_TIMEOUT = 30_000;
const TRAINING_TIMEOUT = 120_000;

class ApiClientError extends Error {
	constructor(
		message: string,
		public status: number,
	) {
		super(message);
		this.name = "ApiClientError";
	}
}

function getApiKey(): string | null {
	if (typeof document === "undefined") return null;
	const match = document.cookie.match(/api_key=([^;]+)/);
	return match ? match[1] : null;
}

async function request<T>(path: string, options?: RequestInit & { timeout?: number }): Promise<T> {
	const { timeout = DEFAULT_TIMEOUT, ...fetchOptions } = options ?? {};
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), timeout);

	const apiKey = getApiKey();

	try {
		const response = await fetch(`${API_BASE_URL}${path}`, {
			...fetchOptions,
			signal: controller.signal,
			headers: {
				"Content-Type": "application/json",
				...(apiKey ? { Authorization: `Bearer ${apiKey}` } : {}),
				...fetchOptions?.headers,
			},
		});

		if (response.status === 401) {
			if (typeof window !== "undefined") {
				window.location.href = "/login";
			}
			throw new ApiClientError("Unauthorized", 401);
		}

		if (!response.ok) {
			const error = await response.json().catch(() => ({ detail: response.statusText }));
			throw new ApiClientError(
				error.detail || `Request failed: ${response.statusText}`,
				response.status,
			);
		}

		return (await response.json()) as T;
	} catch (error) {
		if (error instanceof ApiClientError) throw error;
		if (error instanceof DOMException && error.name === "AbortError") {
			throw new ApiClientError("Request timed out", 408);
		}
		throw new ApiClientError(error instanceof Error ? error.message : "Network error", 0);
	} finally {
		clearTimeout(timeoutId);
	}
}

export const api = {
	health: async (): Promise<HealthResponse> => {
		return request<HealthResponse>("/health");
	},

	train: async (config: TrainingConfig): Promise<TrainingResult> => {
		return request<TrainingResult>("/train", {
			method: "POST",
			body: JSON.stringify(config),
			timeout: TRAINING_TIMEOUT,
		});
	},

	predict: async (requestBody: PredictionRequest): Promise<PredictionResponse> => {
		return request<PredictionResponse>("/predict", {
			method: "POST",
			body: JSON.stringify(requestBody),
		});
	},

	listModels: async (): Promise<ModelMetadata[]> => {
		return request<ModelMetadata[]>("/models");
	},

	getModel: async (modelId: string): Promise<ModelMetadata> => {
		return request<ModelMetadata>(`/models/${modelId}`);
	},

	getModelResults: async (modelId: string): Promise<TrainingResult> => {
		return request<TrainingResult>(`/models/${modelId}/results`);
	},

	persistModel: async (modelId: string): Promise<PersistResponse> => {
		return request<PersistResponse>(`/models/${modelId}/persist`, {
			method: "POST",
		});
	},
};

export { ApiClientError };
