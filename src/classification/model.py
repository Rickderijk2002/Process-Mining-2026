"""Classification tree linking deviation counts to throughput class."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import numpy as np
import pandas as pd
from sklearn.metrics import f1_score, make_scorer, precision_score, recall_score
from sklearn.model_selection import GridSearchCV, train_test_split
from sklearn.tree import DecisionTreeClassifier

GOOD = "good"
BAD = "bad"
CASE_ID_COL = "case_id"
THROUGHPUT_COL = "throughput_time"
POSITIVE_CLASS = BAD

DEFAULT_PARAM_GRID = {
    "max_depth": [2, 3, 4, 5],
    "min_samples_leaf": [5, 10, 20],
    "ccp_alpha": [0.0, 0.001, 0.01, 0.1],
}

F1_SCORER = make_scorer(f1_score, pos_label=POSITIVE_CLASS)


def label_throughput(
    throughput: pd.Series,
    cutoff: float,
) -> pd.Series:
    if cutoff < 0:
        raise ValueError(f"cutoff must be non-negative, got {cutoff}")
    return pd.Series(
        np.where(throughput <= cutoff, GOOD, BAD),
        index=throughput.index,
        name="label",
    )


def move_feature_columns(frame: pd.DataFrame) -> list[str]:
    return [
        column
        for column in frame.columns
        if column.startswith(("model_move_", "log_move_"))
    ]


def case_set_scores(
    predicted: set[str],
    expected: set[str],
) -> dict[str, float]:
    if not expected and not predicted:
        return {"precision": 1.0, "recall": 1.0}
    if not predicted:
        return {"precision": 0.0, "recall": 0.0}
    if not expected:
        return {"precision": 0.0, "recall": 0.0}

    true_positive = len(predicted & expected)
    precision = true_positive / len(predicted)
    recall = true_positive / len(expected)
    return {"precision": precision, "recall": recall}


@dataclass
class LeafRule:
    rule_id: int
    predicted_class: str
    conditions: list[str]
    case_ids: list[str]
    n_good: int
    n_bad: int

    @property
    def n_cases(self) -> int:
        return self.n_good + self.n_bad

    @property
    def share_bad(self) -> float:
        if self.n_cases == 0:
            return 0.0
        return self.n_bad / self.n_cases

    def as_row(self) -> dict[str, Any]:
        return {
            "rule_id": self.rule_id,
            "predicted_class": self.predicted_class,
            "conditions": " AND ".join(self.conditions) if self.conditions else "TRUE",
            "n_cases": self.n_cases,
            "n_good": self.n_good,
            "n_bad": self.n_bad,
            "share_bad": round(self.share_bad, 4),
        }


@dataclass
class FitResult:
    estimator: DecisionTreeClassifier
    best_params: dict[str, Any]
    rules: list[LeafRule]
    held_out_precision: float | None
    held_out_recall: float | None


class DeviationTree:
    """Fit a classification tree on move counts against a throughput cutoff."""

    def __init__(
        self,
        *,
        random_state: int = 0,
        test_size: float = 0.25,
        param_grid: dict[str, list[Any]] | None = None,
        cv: int = 5,
    ) -> None:
        self.random_state = random_state
        self.test_size = test_size
        self.param_grid = param_grid if param_grid is not None else DEFAULT_PARAM_GRID
        self.cv = cv

    def fit(
        self,
        frame: pd.DataFrame,
        cutoff: float,
        *,
        holdout: bool = True,
        search: bool = True,
        max_depth: int | None = None,
    ) -> FitResult:
        _require_columns(frame, [CASE_ID_COL, THROUGHPUT_COL])
        features = move_feature_columns(frame)
        if not features:
            raise ValueError("encoding table has no model_move_ or log_move_ columns")

        labels = label_throughput(frame[THROUGHPUT_COL], cutoff)
        feature_frame = frame[features]
        case_ids = frame[CASE_ID_COL].astype(str)

        if holdout:
            x_fit, x_test, y_fit, y_test = train_test_split(
                feature_frame,
                labels,
                test_size=self.test_size,
                random_state=self.random_state,
                stratify=labels,
            )
        else:
            x_fit, y_fit = feature_frame, labels
            x_test = y_test = None

        if search:
            grid = GridSearchCV(
                DecisionTreeClassifier(random_state=self.random_state),
                param_grid=self.param_grid,
                scoring=F1_SCORER,
                refit=True,
                cv=self.cv,
                n_jobs=1,
            )
            grid.fit(x_fit, y_fit)
            estimator = grid.best_estimator_
            best_params = dict(grid.best_params_)
        else:
            depth = 1 if max_depth is None else max_depth
            estimator = DecisionTreeClassifier(
                max_depth=depth,
                random_state=self.random_state,
            )
            estimator.fit(x_fit, y_fit)
            best_params = {"max_depth": depth, "ccp_alpha": 0.0}

        held_out_precision: float | None = None
        held_out_recall: float | None = None
        if holdout and x_test is not None and y_test is not None:
            y_pred = estimator.predict(x_test)
            held_out_precision = float(
                precision_score(
                    y_test,
                    y_pred,
                    pos_label=POSITIVE_CLASS,
                    zero_division=0,
                )
            )
            held_out_recall = float(
                recall_score(
                    y_test,
                    y_pred,
                    pos_label=POSITIVE_CLASS,
                    zero_division=0,
                )
            )

        rules = extract_leaf_rules(
            estimator,
            feature_frame,
            case_ids,
            labels,
            feature_names=features,
        )

        return FitResult(
            estimator=estimator,
            best_params=best_params,
            rules=rules,
            held_out_precision=held_out_precision,
            held_out_recall=held_out_recall,
        )


def extract_leaf_rules(
    estimator: DecisionTreeClassifier,
    features: pd.DataFrame,
    case_ids: pd.Series,
    labels: pd.Series,
    *,
    feature_names: list[str],
) -> list[LeafRule]:
    tree = estimator.tree_
    children_left = tree.children_left
    children_right = tree.children_right
    feature_index = tree.feature
    threshold = tree.threshold

    paths: dict[int, list[str]] = {}
    stack: list[tuple[int, list[str]]] = [(0, [])]
    while stack:
        node_id, conditions = stack.pop()
        left = children_left[node_id]
        right = children_right[node_id]
        if left == right:
            paths[node_id] = conditions
            continue
        name = feature_names[feature_index[node_id]]
        cut = threshold[node_id]
        stack.append((left, [*conditions, f"{name} <= {cut:g}"]))
        stack.append((right, [*conditions, f"{name} > {cut:g}"]))

    leaf_ids = estimator.apply(features)
    predicted = estimator.predict(features)

    rules: list[LeafRule] = []
    for rule_id, leaf_id in enumerate(sorted(paths)):
        mask = leaf_ids == leaf_id
        leaf_case_ids = case_ids.loc[mask].astype(str).tolist()
        if len(leaf_case_ids) == 0:
            continue
        leaf_labels = labels.loc[mask]
        leaf_predictions = predicted[mask]
        predicted_class = str(pd.Series(leaf_predictions).mode().iloc[0])
        rules.append(
            LeafRule(
                rule_id=rule_id,
                predicted_class=predicted_class,
                conditions=paths[leaf_id],
                case_ids=leaf_case_ids,
                n_good=int((leaf_labels == GOOD).sum()),
                n_bad=int((leaf_labels == BAD).sum()),
            )
        )
    return rules


def rules_to_frame(rules: list[LeafRule]) -> pd.DataFrame:
    return pd.DataFrame([rule.as_row() for rule in rules])


def rules_to_case_frame(rules: list[LeafRule]) -> pd.DataFrame:
    rows = [
        {"rule_id": rule.rule_id, "case_id": case_id}
        for rule in rules
        for case_id in rule.case_ids
    ]
    return pd.DataFrame(rows, columns=["rule_id", "case_id"])


def bad_case_ids(rules: list[LeafRule]) -> set[str]:
    cases: set[str] = set()
    for rule in rules:
        if rule.predicted_class == BAD:
            cases.update(rule.case_ids)
    return cases


def _require_columns(frame: pd.DataFrame, columns: list[str]) -> None:
    missing = [column for column in columns if column not in frame.columns]
    if missing:
        raise ValueError(f"encoding table missing columns: {missing}")
