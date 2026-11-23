"""Fit-on-train preprocessing pipeline (imputation, scaling, encoding) for IoT-23."""
import csv
import math
from pathlib import Path
from typing import Dict, List, Set, Any, Optional, Tuple, Union

from iot23.schema import ZEEK_UNSET_FIELD
from iot23.features import FEATURE_COLUMNS, TARGET_COLUMNS, METADATA_COLUMNS

NUMERICAL_FEATURES: List[str] = [
    "id.orig_p",
    "id.resp_p",
    "duration",
    "orig_bytes",
    "resp_bytes",
    "missed_bytes",
    "orig_pkts",
    "orig_ip_bytes",
    "resp_pkts",
    "resp_ip_bytes",
]

CATEGORICAL_FEATURES: List[str] = [
    "proto",
    "service",
    "conn_state",
    "history",
]

UNKNOWN_TOKEN = "<UNK>"
UNKNOWN_INDEX = 0

class FitOnTrainPreprocessor:
    """
    Leakage-safe preprocessor enforcing Invariant 5:
    All imputation values, scalers, and encoding dictionaries are learned
    exclusively on the training partition.
    """

    def __init__(self):
        self.is_fitted = False
        self.numerical_medians: Dict[str, float] = {}
        self.numerical_means: Dict[str, float] = {}
        self.numerical_stds: Dict[str, float] = {}
        self.categorical_vocabs: Dict[str, Dict[str, int]] = {}
        self.learned_parameters: List[Dict[str, Any]] = []

    def fit(self, train_records: List[Dict[str, Any]], partition_name: str = "train") -> "FitOnTrainPreprocessor":
        """
        Fit preprocessing parameters on the training partition only.
        
        Raises ValueError if partition_name is not 'train' (Invariant 5 enforcement).
        """
        if partition_name != "train":
            raise ValueError(
                f"Invariant 5 Violation: Preprocessing parameters must be fitted "
                f"exclusively on 'train', but received '{partition_name}'."
            )

        self.learned_parameters = []

        # 1. Fit Numerical Imputers (Median) and Scalers (Mean, Std)
        for col in NUMERICAL_FEATURES:
            vals: List[float] = []
            for r in train_records:
                v = r.get(col)
                if v is not None and str(v).strip() != ZEEK_UNSET_FIELD and str(v).strip() != "":
                    try:
                        vals.append(float(v))
                    except (ValueError, TypeError):
                        pass

            if vals:
                sorted_vals = sorted(vals)
                n = len(sorted_vals)
                if n % 2 == 1:
                    median_val = sorted_vals[n // 2]
                else:
                    median_val = (sorted_vals[(n // 2) - 1] + sorted_vals[n // 2]) / 2.0
                mean_val = sum(vals) / float(n)
                variance = sum((x - mean_val) ** 2 for x in vals) / float(n)
                std_val = math.sqrt(variance) if variance > 0 else 1.0
            else:
                median_val = 0.0
                mean_val = 0.0
                std_val = 1.0

            if std_val == 0.0:
                std_val = 1.0

            self.numerical_medians[col] = median_val
            self.numerical_means[col] = mean_val
            self.numerical_stds[col] = std_val

            self.learned_parameters.append({
                "parameter_name": f"{col}_impute_median",
                "column": col,
                "fit_source": "train",
                "partition_learned": "train",
                "value": str(round(median_val, 6)),
            })
            self.learned_parameters.append({
                "parameter_name": f"{col}_scale_mean",
                "column": col,
                "fit_source": "train",
                "partition_learned": "train",
                "value": str(round(mean_val, 6)),
            })
            self.learned_parameters.append({
                "parameter_name": f"{col}_scale_std",
                "column": col,
                "fit_source": "train",
                "partition_learned": "train",
                "value": str(round(std_val, 6)),
            })

        # 2. Fit Categorical Vocabularies
        for col in CATEGORICAL_FEATURES:
            # Index 0 is reserved for UNKNOWN_TOKEN
            vocab: Dict[str, int] = {UNKNOWN_TOKEN: UNKNOWN_INDEX}
            current_idx = 1
            for r in train_records:
                val = str(r.get(col, ZEEK_UNSET_FIELD)).strip()
                if val and val not in vocab:
                    vocab[val] = current_idx
                    current_idx += 1

            self.categorical_vocabs[col] = vocab

            self.learned_parameters.append({
                "parameter_name": f"{col}_vocab_size",
                "column": col,
                "fit_source": "train",
                "partition_learned": "train",
                "value": str(len(vocab)),
            })

        self.is_fitted = True
        return self

    def transform(self, records: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Transform a batch of records using parameters fitted on train.
        Unseen categories are safely mapped to index 0 (<UNK>).
        """
        if not self.is_fitted:
            raise RuntimeError("Preprocessor must be fitted on training data before transform.")

        transformed_records = []
        for r in records:
            out_rec: Dict[str, Any] = {}

            # Process numerical features: impute unset with median, then standardize
            for col in NUMERICAL_FEATURES:
                raw_val = r.get(col)
                if raw_val is None or str(raw_val).strip() == ZEEK_UNSET_FIELD or str(raw_val).strip() == "":
                    val = self.numerical_medians[col]
                else:
                    try:
                        val = float(raw_val)
                    except (ValueError, TypeError):
                        val = self.numerical_medians[col]

                # Standard scaling: (x - mean) / std
                scaled = (val - self.numerical_means[col]) / self.numerical_stds[col]
                out_rec[f"{col}_scaled"] = round(scaled, 6)

            # Process categorical features: encode via train vocab, unseen -> 0 (<UNK>)
            for col in CATEGORICAL_FEATURES:
                raw_cat = str(r.get(col, ZEEK_UNSET_FIELD)).strip()
                vocab = self.categorical_vocabs[col]
                encoded_idx = vocab.get(raw_cat, UNKNOWN_INDEX)
                out_rec[f"{col}_encoded"] = encoded_idx

            # Preserve targets and metadata without scaling
            for t_col in TARGET_COLUMNS:
                if t_col in r:
                    out_rec[t_col] = r[t_col]

            for m_col in METADATA_COLUMNS:
                if m_col in r:
                    out_rec[m_col] = r[m_col]

            transformed_records.append(out_rec)

        return transformed_records

    def export_parameters_csv(self, output_path: Path) -> None:
        """Write the parameter catalog CSV file."""
        output_path.parent.mkdir(parents=True, exist_ok=True)
        fieldnames = ["parameter_name", "column", "fit_source", "partition_learned", "value"]
        with open(output_path, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(self.learned_parameters)
