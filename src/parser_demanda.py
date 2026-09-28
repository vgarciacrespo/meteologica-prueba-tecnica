from pathlib import Path
import pandas as pd


def parsear_demanda(filepath: str | Path) -> pd.DataFrame:
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontro el archivo: {filepath}")

    # 1. Parseo con manejo de decimales espanoles y lineas con separadores residuales
    df = pd.read_csv(
        path,
        sep=";",
        decimal=",",
        thousands=".",
        usecols=[0, 1],
        names=["local_datetime", "demanda_kwh"],
        header=0,
        engine="python",
    )

    # 2. Conversion a float y transformacion a MWh
    df["demanda_kwh"] = pd.to_numeric(df["demanda_kwh"], errors="coerce")
    df["demanda_mwh"] = df["demanda_kwh"] / 1000.0

    # 3. Normalizacion de zona horaria local peninsular a UTC
    df["timestamp_utc"] = (
        pd.to_datetime(df["local_datetime"])
        .dt.tz_localize("Europe/Madrid", nonexistent="shift_forward", ambiguous="infer")
        .dt.tz_convert("UTC")
    )

    # 4. Limpieza de duplicados y ordenacion
    df = (
        df[["timestamp_utc", "demanda_mwh"]]
        .dropna(subset=["timestamp_utc"])
        .sort_values("timestamp_utc")
        .drop_duplicates(subset=["timestamp_utc"])
    )

    # 5. Rejilla temporal completa de 5 minutos en UTC
    rejilla_completa = pd.date_range(
        start=df["timestamp_utc"].min(),
        end=df["timestamp_utc"].max(),
        freq="5min",
        name="timestamp_utc",
    )

    df = df.set_index("timestamp_utc").reindex(rejilla_completa)

    # 6. Interpolacion temporal para cubrir los intervalos faltantes
    df["demanda_mwh"] = df["demanda_mwh"].interpolate(method="time")

    return df.reset_index()


if __name__ == "__main__":
    resultado = parsear_demanda("data/demanda_semanal_espana_peninsular.csv")
    print(f"Filas procesadas y regularizadas: {len(resultado)}")
    print(resultado.head())