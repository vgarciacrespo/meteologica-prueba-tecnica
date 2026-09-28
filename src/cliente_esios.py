from pathlib import Path
import pandas as pd
import requests

URL_ESIOS_INDICADOR = "https://api.esios.ree.es/indicators/551"


def descargar_generacion_eolica(
    fecha_inicio: str = "2026-03-23T00:00:00+01:00",
    fecha_fin: str = "2026-03-29T23:55:00+02:00",
    cache_path: str | Path | None = "data/eolica_551.json",
) -> pd.DataFrame:
    path_cache = Path(cache_path) if cache_path else None

    if path_cache and path_cache.is_file():
        df = pd.read_json(path_cache)
        df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
        return df

    params = {
        "start_date": fecha_inicio,
        "end_date": fecha_fin,
        "geo_ids": "",
        "geo_agg": "sum",
        "locale": "es",
    }

    headers = {
        "accept": "application/json; application/vnd.esios-api-v1+json",
        "content-type": "application/json",
        "origin": "https://www.esios.ree.es",
        "referer": "https://www.esios.ree.es/",
        "user-agent": "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        "x-api-key": "request_your_personal_token_sending_email_to_consultasios@ree.es",
    }

    try:
        response = requests.get(
            URL_ESIOS_INDICADOR, params=params, headers=headers, timeout=30
        )
        response.raise_for_status()
        data = response.json()
    except requests.exceptions.RequestException as e:
        raise RuntimeError(f"Error al descargar datos eolicos de ESIOS: {e}")

    valores = data.get("indicator", {}).get("values", [])
    if not valores:
        raise ValueError("ESIOS no devolvio registros para el periodo indicado.")

    registros = []
    for item in valores:
        val = item.get("value")
        if val is not None:
            registros.append(
                {
                    "timestamp_utc": item.get("datetime_utc"),
                    "potencia_mw": float(val),
                }
            )

    df = pd.DataFrame(registros)
    df["timestamp_utc"] = pd.to_datetime(df["timestamp_utc"], utc=True)
    df = (
        df.sort_values("timestamp_utc")
        .drop_duplicates(subset=["timestamp_utc"])
        .reset_index(drop=True)
    )

    df["eolica_mwh"] = df["potencia_mw"] * (5.0 / 60.0)

    if path_cache:
        path_cache.parent.mkdir(parents=True, exist_ok=True)
        df.to_json(path_cache, date_format="iso")

    return df


if __name__ == "__main__":
    df_eolica = descargar_generacion_eolica()
    print(f"Registros eolicos descargados/cargados: {len(df_eolica)}")
    print(df_eolica.head())