/**
 * TypeScript interfaces synced with shared/schemas/ Pydantic models.
 * CRITICAL: These must exactly match the Pydantic schema field names and types.
 */

// === Enums as literal unions ===

export type HomeOwnership = "RENT" | "OWN" | "MORTGAGE" | "OTHER";

export type LoanIntent =
	| "EDUCATION"
	| "MEDICAL"
	| "VENTURE"
	| "PERSONAL"
	| "DEBTCONSOLIDATION"
	| "HOMEIMPROVEMENT";

export type LoanGrade = "A" | "B" | "C" | "D" | "E" | "F" | "G";

export type DefaultOnFile = "Y" | "N";

export type ModelType = "logistic_regression" | "xgboost" | "random_forest";

// === Core schemas ===

export interface LoanApplication {
	person_age: number;
	person_income: number;
	person_emp_length: number;
	loan_amnt: number;
	loan_int_rate: number;
	loan_percent_income: number;
	cb_person_cred_hist_length: number;
	person_home_ownership: HomeOwnership;
	loan_intent: LoanIntent;
	loan_grade: LoanGrade;
	cb_person_default_on_file: DefaultOnFile;
}

export interface TrainingConfig {
	model_type: ModelType;
	test_size: number;
	random_state: number;
	undersample: boolean;
	cv_folds: number;
}

export interface ThresholdResult {
	threshold: number;
	sensitivity: number;
	specificity: number;
	youden_j: number;
	precision: number;
	f1_score: number;
}

export interface ROCCurveData {
	fpr: number[];
	tpr: number[];
	thresholds: number[];
}

export interface ConfusionMatrix {
	matrix: number[][];
	true_negatives: number;
	false_positives: number;
	false_negatives: number;
	true_positives: number;
}

export interface CalibrationCurve {
	prob_true: number[];
	prob_pred: number[];
	n_bins: number;
}

export interface ModelMetrics {
	accuracy: number;
	precision: number;
	recall: number;
	f1_score: number;
	roc_auc: number;
	threshold_analysis: ThresholdResult;
	roc_curve: ROCCurveData;
	confusion_matrix: ConfusionMatrix;
	calibration_curve: CalibrationCurve | null;
}

export interface TrainingResult {
	model_id: string;
	model_type: string;
	metrics: ModelMetrics;
	optimal_threshold: number;
	feature_importance: Record<string, number> | null;
	training_config: TrainingConfig;
	training_time_seconds: number;
}

export interface PredictionRequest {
	model_id: string;
	applications: LoanApplication[];
	threshold: number | null;
	include_probabilities: boolean;
}

export interface PredictionResult {
	application: LoanApplication;
	predicted_default: boolean;
	default_probability: number;
	confidence: number;
}

export interface PredictionResponse {
	model_id: string;
	model_type: string;
	threshold: number;
	predictions: PredictionResult[];
	timestamp: string;
	total_applications: number;
	predicted_defaults: number;
	predicted_approvals: number;
}

export interface ModelMetadata {
	model_id: string;
	model_type: string;
	threshold: number;
	roc_auc: number;
	accuracy: number;
	created_at: string;
}

// === API response types ===

export interface HealthResponse {
	status: string;
	service: string;
}

export interface PersistResponse {
	model_id: string;
	path: string;
	instructions: string;
}

export interface ApiError {
	detail: string;
}
