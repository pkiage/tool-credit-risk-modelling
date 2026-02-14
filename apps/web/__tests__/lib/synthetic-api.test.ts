import { afterEach, beforeEach, describe, expect, it, vi } from "vitest";
import { ApiClientError, api } from "@/lib/api-client";

const mockFetch = vi.fn();

beforeEach(() => {
	mockFetch.mockReset();
	vi.stubGlobal("fetch", mockFetch);
});

afterEach(() => {
	vi.restoreAllMocks();
});

function jsonResponse(data: unknown, status = 200) {
	return Promise.resolve({
		ok: status >= 200 && status < 300,
		status,
		statusText: status === 200 ? "OK" : "Error",
		json: () => Promise.resolve(data),
	});
}

describe("api.generateSynthetic", () => {
	it("sends POST with config to /synthetic/generate/", async () => {
		const mockResponse = {
			dataset_id: "syn-abc123",
			metadata: {
				n_samples: 5000,
				n_features: 26,
				default_rate_actual: 0.218,
				feature_names: ["person_age", "person_income"],
				summary_stats: {
					person_age: { mean: 27.5, std: 6.1, min: 20, max: 84 },
				},
			},
		};
		mockFetch.mockReturnValueOnce(jsonResponse(mockResponse));

		const config = {
			n_samples: 5000,
			default_rate: 0.22,
			distributions: [],
			random_seed: 42,
		};

		const result = await api.generateSynthetic(config);
		expect(result.dataset_id).toBe("syn-abc123");
		expect(result.metadata.n_samples).toBe(5000);
		expect(result.metadata.n_features).toBe(26);
		expect(result.metadata.default_rate_actual).toBe(0.218);

		const [url, options] = mockFetch.mock.calls[0];
		expect(url).toContain("/synthetic/generate/");
		expect(options.method).toBe("POST");
		expect(JSON.parse(options.body)).toEqual(config);
	});

	it("returns typed SyntheticGenerateResponse", async () => {
		const mockResponse = {
			dataset_id: "syn-def456",
			metadata: {
				n_samples: 10000,
				n_features: 26,
				default_rate_actual: 0.5,
				feature_names: ["person_age"],
				summary_stats: {},
			},
		};
		mockFetch.mockReturnValueOnce(jsonResponse(mockResponse));

		const result = await api.generateSynthetic({
			n_samples: 10000,
			default_rate: 0.5,
			distributions: [],
			random_seed: null,
		});

		expect(result).toHaveProperty("dataset_id");
		expect(result).toHaveProperty("metadata");
		expect(result.metadata).toHaveProperty("n_samples");
		expect(result.metadata).toHaveProperty("n_features");
		expect(result.metadata).toHaveProperty("default_rate_actual");
		expect(result.metadata).toHaveProperty("feature_names");
		expect(result.metadata).toHaveProperty("summary_stats");
	});

	it("throws ApiClientError on 400 response", async () => {
		mockFetch.mockReturnValueOnce(jsonResponse({ detail: "n_samples must be positive" }, 400));

		try {
			await api.generateSynthetic({
				n_samples: -1,
				default_rate: 0.22,
				distributions: [],
				random_seed: 42,
			});
			expect.unreachable("Should have thrown");
		} catch (err) {
			expect(err).toBeInstanceOf(ApiClientError);
			expect((err as ApiClientError).status).toBe(400);
			expect((err as ApiClientError).message).toBe("n_samples must be positive");
		}
	});

	it("throws ApiClientError on 500 response", async () => {
		mockFetch.mockReturnValueOnce(jsonResponse({ detail: "Internal server error" }, 500));

		await expect(
			api.generateSynthetic({
				n_samples: 5000,
				default_rate: 0.22,
				distributions: [],
				random_seed: 42,
			}),
		).rejects.toThrow(ApiClientError);
	});
});
