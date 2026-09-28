import numpy as np
import pandas as pd
import pytest

from src.calculo import cruzar_y_calcular_balance, generar_granularidades


def test_balance_energia_adicional():
    timestamps = pd.date_range("2026-03-23 00:00:00+00:00", periods=3, freq="5min")
    df_demanda = pd.DataFrame({
        "timestamp_utc": timestamps,
        "demanda_mwh": [100.0, 50.0, 200.0]
    })
    df_eolica = pd.DataFrame({
        "timestamp_utc": timestamps,
        "potencia_mw": [600.0, 1200.0, 1200.0],
        "eolica_mwh": [50.0, 100.0, 100.0]
    })

    balance = cruzar_y_calcular_balance(df_demanda, df_eolica)

    assert balance["energia_adicional_mwh"].iloc[0] == 50.0
    assert balance["energia_adicional_mwh"].iloc[1] == 0.0
    assert balance["energia_adicional_mwh"].iloc[2] == 100.0


def test_conservacion_energia_en_granularidades():
    timestamps = pd.date_range("2026-03-23 00:00:00+00:00", periods=12, freq="5min")
    df_balance = pd.DataFrame({
        "timestamp_utc": timestamps,
        "demanda_mwh": [100.0] * 12,
        "eolica_mwh": [20.0] * 12,
        "energia_adicional_mwh": [80.0] * 12
    })

    gran = generar_granularidades(df_balance)

    total_base = df_balance["energia_adicional_mwh"].sum()
    total_minutal = gran["minutal"]["energia_adicional_mwh"].sum()
    total_horaria = gran["horaria"]["energia_adicional_mwh"].sum()
    total_diaria = gran["diaria"]["energia_adicional_mwh"].sum()

    assert pytest.approx(total_base, 0.001) == total_minutal
    assert pytest.approx(total_base, 0.001) == total_horaria
    assert pytest.approx(total_base, 0.001) == total_diaria