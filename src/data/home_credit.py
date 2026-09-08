"""Memory-conscious feature aggregation for Home Credit Default Risk."""
from __future__ import annotations

from collections.abc import Callable
from pathlib import Path

import numpy as np
import pandas as pd

CHUNK_SIZE = 250_000


def _flat_aggregate(
    source: Path,
    usecols: list[str],
    transform: Callable[[pd.DataFrame], pd.DataFrame],
    aggregations: dict[str, str],
    prefix: str,
) -> pd.DataFrame:
    """Aggregate a large CSV per applicant without holding it all in memory."""
    partials: list[pd.DataFrame] = []
    for chunk in pd.read_csv(source, usecols=usecols, chunksize=CHUNK_SIZE):
        transformed = transform(chunk)
        partials.append(transformed.groupby("SK_ID_CURR", sort=False).agg(aggregations))
    if not partials:
        return pd.DataFrame(index=pd.Index([], name="SK_ID_CURR"))
    partial = pd.concat(partials)
    reducers = {column: ("max" if operation == "max" else "min" if operation == "min" else "sum") for column, operation in aggregations.items()}
    output = partial.groupby(level=0, sort=False).agg(reducers)
    return output.rename(columns=lambda column: f"{prefix}_{column}")


def _application_features(data_dir: Path) -> tuple[pd.DataFrame, pd.Series]:
    columns = [
        "SK_ID_CURR", "TARGET", "AMT_INCOME_TOTAL", "AMT_CREDIT", "AMT_ANNUITY",
        "AMT_GOODS_PRICE", "DAYS_BIRTH", "DAYS_EMPLOYED", "DAYS_REGISTRATION",
        "DAYS_ID_PUBLISH", "CNT_FAM_MEMBERS", "EXT_SOURCE_1", "EXT_SOURCE_2", "EXT_SOURCE_3",
        "REGION_RATING_CLIENT", "REGION_RATING_CLIENT_W_CITY", "HOUR_APPR_PROCESS_START",
        "DAYS_LAST_PHONE_CHANGE", "FLAG_OWN_CAR", "FLAG_OWN_REALTY",
    ]
    frame = pd.read_csv(data_dir / "application_train.csv", usecols=columns)
    target = frame.pop("TARGET").astype(int)
    frame["DAYS_EMPLOYED"] = frame["DAYS_EMPLOYED"].replace(365243, np.nan)
    frame["FLAG_OWN_CAR"] = (frame["FLAG_OWN_CAR"] == "Y").astype(int)
    frame["FLAG_OWN_REALTY"] = (frame["FLAG_OWN_REALTY"] == "Y").astype(int)
    frame["app_credit_to_income"] = frame["AMT_CREDIT"] / frame["AMT_INCOME_TOTAL"].replace(0, np.nan)
    frame["app_annuity_to_income"] = frame["AMT_ANNUITY"] / frame["AMT_INCOME_TOTAL"].replace(0, np.nan)
    return frame.set_index("SK_ID_CURR"), target.set_axis(frame["SK_ID_CURR"])


def _bureau_features(data_dir: Path) -> pd.DataFrame:
    bureau_columns = ["SK_ID_CURR", "SK_ID_BUREAU", "DAYS_CREDIT", "AMT_CREDIT_SUM", "AMT_CREDIT_SUM_DEBT", "CREDIT_DAY_OVERDUE", "CNT_CREDIT_PROLONG"]
    bureau = pd.read_csv(data_dir / "bureau.csv", usecols=bureau_columns)
    bureau_map = bureau[["SK_ID_BUREAU", "SK_ID_CURR"]]
    bureau["record_count"] = 1
    bureau["debt_ratio_component"] = bureau["AMT_CREDIT_SUM_DEBT"] / bureau["AMT_CREDIT_SUM"].replace(0, np.nan)
    base = bureau.groupby("SK_ID_CURR", sort=False).agg({
        "record_count": "sum", "DAYS_CREDIT": "min", "AMT_CREDIT_SUM": "sum",
        "AMT_CREDIT_SUM_DEBT": "sum", "CREDIT_DAY_OVERDUE": "sum",
        "CNT_CREDIT_PROLONG": "sum", "debt_ratio_component": "mean",
    }).rename(columns=lambda column: f"bureau_{column}")

    status_parts: list[pd.DataFrame] = []
    for chunk in pd.read_csv(data_dir / "bureau_balance.csv", usecols=["SK_ID_BUREAU", "STATUS"], chunksize=CHUNK_SIZE):
        chunk = chunk.merge(bureau_map, on="SK_ID_BUREAU", how="inner")
        chunk["status_count"] = 1
        chunk["late_status_count"] = chunk["STATUS"].isin(["1", "2", "3", "4", "5"]).astype(int)
        chunk["default_status_count"] = (chunk["STATUS"] == "5").astype(int)
        status_parts.append(chunk.groupby("SK_ID_CURR", sort=False)[["status_count", "late_status_count", "default_status_count"]].sum())
    if status_parts:
        statuses = pd.concat(status_parts).groupby(level=0, sort=False).sum()
        statuses["bureau_balance_late_ratio"] = statuses["late_status_count"] / statuses["status_count"].replace(0, np.nan)
        base = base.join(statuses.rename(columns=lambda column: f"bureau_balance_{column}"), how="left")
    return base


def _previous_features(data_dir: Path) -> pd.DataFrame:
    def transform(chunk: pd.DataFrame) -> pd.DataFrame:
        chunk["record_count"] = 1
        chunk["refused_count"] = (chunk["NAME_CONTRACT_STATUS"] == "Refused").astype(int)
        chunk["cancelled_count"] = (chunk["NAME_CONTRACT_STATUS"] == "Canceled").astype(int)
        chunk["application_credit_gap"] = chunk["AMT_APPLICATION"] - chunk["AMT_CREDIT"]
        return chunk

    return _flat_aggregate(
        data_dir / "previous_application.csv",
        ["SK_ID_CURR", "AMT_APPLICATION", "AMT_CREDIT", "AMT_ANNUITY", "DAYS_DECISION", "NAME_CONTRACT_STATUS"],
        transform,
        {"record_count": "sum", "refused_count": "sum", "cancelled_count": "sum", "AMT_APPLICATION": "sum", "AMT_CREDIT": "sum", "AMT_ANNUITY": "sum", "DAYS_DECISION": "min", "application_credit_gap": "sum"},
        "previous",
    )


def _pos_features(data_dir: Path) -> pd.DataFrame:
    def transform(chunk: pd.DataFrame) -> pd.DataFrame:
        chunk["record_count"] = 1
        chunk["late_count"] = (chunk["SK_DPD"] > 0).astype(int)
        chunk["default_late_count"] = (chunk["SK_DPD_DEF"] > 0).astype(int)
        return chunk

    return _flat_aggregate(
        data_dir / "POS_CASH_balance.csv",
        ["SK_ID_CURR", "MONTHS_BALANCE", "CNT_INSTALMENT_FUTURE", "SK_DPD", "SK_DPD_DEF"],
        transform,
        {"record_count": "sum", "MONTHS_BALANCE": "min", "CNT_INSTALMENT_FUTURE": "sum", "SK_DPD": "max", "SK_DPD_DEF": "max", "late_count": "sum", "default_late_count": "sum"},
        "pos",
    )


def _credit_card_features(data_dir: Path) -> pd.DataFrame:
    def transform(chunk: pd.DataFrame) -> pd.DataFrame:
        chunk["record_count"] = 1
        chunk["late_count"] = (chunk["SK_DPD"] > 0).astype(int)
        chunk["utilisation"] = chunk["AMT_BALANCE"] / chunk["AMT_CREDIT_LIMIT_ACTUAL"].replace(0, np.nan)
        return chunk

    return _flat_aggregate(
        data_dir / "credit_card_balance.csv",
        ["SK_ID_CURR", "MONTHS_BALANCE", "AMT_BALANCE", "AMT_CREDIT_LIMIT_ACTUAL", "AMT_PAYMENT_CURRENT", "SK_DPD", "SK_DPD_DEF"],
        transform,
        {"record_count": "sum", "MONTHS_BALANCE": "min", "AMT_BALANCE": "sum", "AMT_CREDIT_LIMIT_ACTUAL": "sum", "AMT_PAYMENT_CURRENT": "sum", "SK_DPD": "max", "SK_DPD_DEF": "max", "late_count": "sum", "utilisation": "sum"},
        "card",
    )


def _installment_features(data_dir: Path) -> pd.DataFrame:
    def transform(chunk: pd.DataFrame) -> pd.DataFrame:
        chunk["record_count"] = 1
        chunk["payment_gap"] = chunk["AMT_PAYMENT"] - chunk["AMT_INSTALMENT"]
        chunk["days_late"] = (chunk["DAYS_ENTRY_PAYMENT"] - chunk["DAYS_INSTALMENT"]).clip(lower=0)
        chunk["late_count"] = (chunk["days_late"] > 0).astype(int)
        return chunk

    return _flat_aggregate(
        data_dir / "installments_payments.csv",
        ["SK_ID_CURR", "AMT_INSTALMENT", "AMT_PAYMENT", "DAYS_ENTRY_PAYMENT", "DAYS_INSTALMENT"],
        transform,
        {"record_count": "sum", "AMT_INSTALMENT": "sum", "AMT_PAYMENT": "sum", "payment_gap": "sum", "days_late": "sum", "late_count": "sum"},
        "installment",
    )


def build_home_credit_features(data_dir: str | Path) -> tuple[pd.DataFrame, pd.Series]:
    """Build one feature row per applicant and return matching default labels."""
    source = Path(data_dir)
    application, target = _application_features(source)
    aggregates = [
        _bureau_features(source), _previous_features(source), _pos_features(source),
        _credit_card_features(source), _installment_features(source),
    ]
    features = application
    for aggregate in aggregates:
        features = features.join(aggregate, how="left")
    return features.replace([np.inf, -np.inf], np.nan), target.reindex(features.index)

