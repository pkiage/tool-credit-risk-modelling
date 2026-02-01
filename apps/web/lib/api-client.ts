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

async function request<T>(
	path: string,
	options?: RequestInit & { timeout?: number },
): Promise<T> {
	const { timeout = DEFAULT_TIMEOUT, ...fetchOptions } = options ?? {};
	const controller = new AbortController();
	const timeoutId = setTimeout(() => controller.abort(), timeout);

	try {
		const response = await fetch(`${API_BASE_URL}${path}`, {
			...fetchOptions,
			signal: controller.signal,
			headers: {
				"Content-Type": "application/json",
				...fetchOptions?.headers,
			},
		});

		if (!response.ok) {
			const error = await response.json().catch(() => ({ detail: response.statusText }));
			throw new ApiClientError(error.detail || `Request failed: ${response.statusText}`, response.status);
		}

		return (await response.json()) as T;
	} catch (error) {
		if (error instanceof ApiClientError) throw error;
		if (error instanceof DOMException && error.name === "AbortError") {
			throw new ApiClientError("Request timed out", 408);
		}
		throw new ApiClientError(
			error instanceof Error ? error.message : "Network error",
			0,
		);
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

	persistModel: async (modelId: string): Promise<PersistResponse> => {
		return request<PersistResponse>(`/models/${modelId}/persist`, {
			method: "POST",
		});
	},
};

export { ApiClientError };
