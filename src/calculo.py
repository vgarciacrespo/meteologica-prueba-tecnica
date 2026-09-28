import numpy as np
import pandas as pd


def cruzar_y_calcular_balance(
    df_demanda: pd.DataFrame, df_eolica: pd.DataFrame
) -> pd.DataFrame:
    df = pd.merge(df_demanda, df_eolica, on="timestamp_utc", how="inner")

    df["energia_adicional_mwh"] = np.maximum(
        0.0, df["demanda_mwh"] - df["eolica_mwh"]
    )

    return df[["timestamp_utc", "demanda_mwh", "eolica_mwh", "energia_adicional_mwh"]]


def generar_granularidades(df_5min: pd.DataFrame) -> dict[str, pd.DataFrame]:
    df_base = df_5min.copy().set_index("timestamp_utc")

    df_cincominutal = df_base[["energia_adicional_mwh"]].reset_index()

    minutos_range = pd.date_range(
        start=df_base.index.min(),
        end=df_base.index.max() + pd.Timedelta(minutes=4),
        freq="1min",
        name="timestamp_utc",
    )
    df_minutal = (
        df_base[["energia_adicional_mwh"]]
        .reindex(minutos_range)
        .ffill()
    )
    df_minutal["energia_adicional_mwh"] = df_minutal["energia_adicional_mwh"] / 5.0
    df_minutal = df_minutal.reset_index()

    df_horaria = (
        df_base["energia_adicional_mwh"]
        .resample("1h")
        .sum()
        .reset_index()
    )

    df_diaria = (
        df_base["energia_adicional_mwh"]
        .resample("1D")
        .sum()
        .reset_index()
    )

    return {
        "cincominutal": df_cincominutal,
        "minutal": df_minutal,
        "horaria": df_horaria,
        "diaria": df_diaria,
    }


if __name__ == "__main__":
    from parser_demanda import parsear_demanda
    from cliente_esios import descargar_generacion_eolica

    demanda = parsear_demanda("data/demanda_semanal_espana_peninsular.csv")
    eolica = descargar_generacion_eolica()
    balance = cruzar_y_calcular_balance(demanda, eolica)
    granularidades = generar_granularidades(balance)

    print("--- Resumen de granularidades generadas ---")
    for nombre, df in granularidades.items():
        print(
            f"{nombre.capitalize()}: {len(df)} registros | Total energia adicional: {df['energia_adicional_mwh'].sum():.2f} MWh"
        )