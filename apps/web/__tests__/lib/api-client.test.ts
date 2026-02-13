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

describe("api.health", () => {
	it("returns health data on success", async () => {
		mockFetch.mockReturnValueOnce(jsonResponse({ status: "healthy", service: "credit-risk-api" }));

		const result = await api.health();
		expect(result).toEqual({ status: "healthy", service: "credit-risk-api" });
		expect(mockFetch).toHaveBeenCalledWith(
			expect.stringContaining("/health"),
			expect.objectContaining({
				headers: expect.objectContaining({ "Content-Type": "application/json" }),
			}),
		);
	});
});

describe("api.train", () => {
	it("sends POST with config and training timeout", async () => {
		const mockResult = {
			model_id: "abc123",
			model_type: "logistic_regression",
			metrics: { accuracy: 0.85 },
		};
		mockFetch.mockReturnValueOnce(jsonResponse(mockResult));

		const config = {
			model_type: "logistic_regression" as const,
			test_size: 0.2,
			random_state: 42,
			undersample: false,
			cv_folds: 5,
		};

		const result = await api.train(config);
		expect(result.model_id).toBe("abc123");

		const [url, options] = mockFetch.mock.calls[0];
		expect(url).toContain("/train/");
		expect(options.method).toBe("POST");
		expect(JSON.parse(options.body)).toEqual(config);
	});
});

describe("api.predict", () => {
	it("sends POST with prediction request", async () => {
		const mockResponse = {
			model_id: "abc123",
			predictions: [{ predicted_default: false, default_probability: 0.15 }],
		};
		mockFetch.mockReturnValueOnce(jsonResponse(mockResponse));

		const request = {
			model_id: "abc123",
			applications: [
				{
					person_age: 30,
					person_income: 50000,
					person_emp_length: 5,
					loan_amnt: 10000,
					loan_int_rate: 10.5,
					loan_percent_income: 0.2,
					cb_person_cred_hist_length: 5,
					person_home_ownership: "RENT" as const,
					loan_intent: "PERSONAL" as const,
					loan_grade: "B" as const,
					cb_person_default_on_file: "N" as const,
				},
			],
			threshold: null,
			include_probabilities: true,
		};

		const result = await api.predict(request);
		expect(result.predictions).toHaveLength(1);
		expect(result.predictions[0].predicted_default).toBe(false);
	});
});

describe("api.listModels", () => {
	it("returns model list", async () => {
		const mockModels = [
			{
				model_id: "abc123",
				model_type: "logistic_regression",
				threshold: 0.5,
				roc_auc: 0.85,
				accuracy: 0.82,
				created_at: "2025-01-01T00:00:00Z",
			},
		];
		mockFetch.mockReturnValueOnce(jsonResponse(mockModels));

		const result = await api.listModels();
		expect(result).toHaveLength(1);
		expect(result[0].model_type).toBe("logistic_regression");
	});
});

describe("error handling", () => {
	it("throws ApiClientError on non-ok response with status", async () => {
		mockFetch.mockReturnValueOnce(jsonResponse({ detail: "Model not found" }, 404));

		try {
			await api.getModel("nonexistent");
			expect.unreachable("Should have thrown");
		} catch (err) {
			expect(err).toBeInstanceOf(ApiClientError);
			expect((err as ApiClientError).status).toBe(404);
			expect((err as ApiClientError).message).toBe("Model not found");
		}
	});

	it("throws ApiClientError on network error", async () => {
		mockFetch.mockRejectedValueOnce(new TypeError("Failed to fetch"));

		await expect(api.health()).rejects.toThrow(ApiClientError);
	});

	it("throws ApiClientError on timeout", async () => {
		mockFetch.mockImplementationOnce(
			() =>
				new Promise((_, reject) => {
					setTimeout(() => reject(new DOMException("Aborted", "AbortError")), 10);
				}),
		);

		await expect(api.health()).rejects.toThrow("Request timed out");
	});
});
