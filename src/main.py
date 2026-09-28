import argparse
from pathlib import Path
import sys

from parser_demanda import parsear_demanda
from cliente_esios import descargar_generacion_eolica
from calculo import cruzar_y_calcular_balance, generar_granularidades


def main() -> None:
    parser = argparse.ArgumentParser(
        description="Calculo de energia adicional requerida en Espana peninsular (23-29 marzo 2026)."
    )
    parser.add_argument(
        "--demanda",
        type=str,
        default="data/demanda_semanal_espana_peninsular.csv",
        help="Ruta al archivo CSV con los datos de demanda peninsular.",
    )
    parser.add_argument(
        "--granularidad",
        type=str,
        choices=["minutal", "cincominutal", "horaria", "diaria", "todas"],
        default="todas",
        help="Granularidad temporal de salida (por defecto: todas).",
    )
    parser.add_argument(
        "--output-dir",
        type=str,
        default="output",
        help="Directorio donde se guardaran los archivos CSV resultantes.",
    )

    args = parser.parse_args()

    ruta_demanda = Path(args.demanda)
    if not ruta_demanda.is_file():
        print(f"Error: No se encuentra el archivo de demanda en '{args.demanda}'", file=sys.stderr)
        sys.exit(1)

    print("[1/4] Procesando y regularizando serie de demanda...")
    df_demanda = parsear_demanda(ruta_demanda)

    print("[2/4] Obteniendo datos de generacion eolica (indicador 551)...")
    df_eolica = descargar_generacion_eolica()

    print("[3/4] Calculando balance de energia adicional...")
    df_balance = cruzar_y_calcular_balance(df_demanda, df_eolica)

    print("[4/4] Agregando resoluciones temporales...")
    dict_granularidades = generar_granularidades(df_balance)

    out_dir = Path(args.output_dir)
    out_dir.mkdir(parents=True, exist_ok=True)

    seleccion = (
        dict_granularidades.keys()
        if args.granularidad == "todas"
        else [args.granularidad]
    )

    print("\nResultados generados exitosamente:")
    for key in seleccion:
        df_res = dict_granularidades[key]
        archivo_salida = out_dir / f"energia_adicional_{key}.csv"
        df_res.to_csv(archivo_salida, index=False)
        total_mwh = df_res["energia_adicional_mwh"].sum()
        print(
            f" - {key.capitalize()}: {len(df_res)} filas guardadas en '{archivo_salida}' | Total: {total_mwh:,.2f} MWh"
        )


if __name__ == "__main__":
    main()