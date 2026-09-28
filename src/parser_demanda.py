from pathlib import Path
import pandas as pd


def parsear_demanda(filepath: str | Path) -> pd.DataFrame:
    path = Path(filepath)
    if not path.is_file():
        raise FileNotFoundError(f"No se encontro el archivo: {filepath}")

    registros = []
    with open(path, "r", encoding="utf-8") as f:
        _ = f.readline()
        for linea in f:
            limpia = linea.strip().rstrip(";")
            if not limpia:
                continue
            partes = limpia.split(";")
            if len(partes) >= 2:
                registros.append((partes[0], partes[1]))

    df = pd.DataFrame(registros, columns=["local_datetime", "demanda_kwh"])
    df["demanda_kwh"] = (
        df["demanda_kwh"]
        .str.replace(".", "", regex=False)
        .str.replace(",", ".", regex=False)
        .astype(float)
    )
    df["demanda_mwh"] = df["demanda_kwh"] / 1000.0

    df["timestamp_utc"] = (
        pd.to_datetime(df["local_datetime"])
        .dt.tz_localize("Europe/Madrid", nonexistent="shift_forward", ambiguous="infer")
        .dt.tz_convert("UTC")
    )

    df = df[["timestamp_utc", "demanda_mwh"]].sort_values("timestamp_utc").drop_duplicates(subset=["timestamp_utc"])

    # Rejilla temporal completa de 5 minutos en UTC
    rejilla_completa = pd.date_range(
        start=df["timestamp_utc"].min(),
        end=df["timestamp_utc"].max(),
        freq="5min",
        name="timestamp_utc"
    )

    df = df.set_index("timestamp_utc").reindex(rejilla_completa)
    
    # Tratamiento de la laguna: interpolacion lineal para los intervalos faltantes
    df["demanda_mwh"] = df["demanda_mwh"].interpolate(method="time")
    
    return df.reset_index()


if __name__ == "__main__":
    resultado = parsear_demanda("data/demanda_semanal_espana_peninsular.csv")
    print(f"Filas procesadas y regularizadas: {len(resultado)}")
    print(resultado.head())