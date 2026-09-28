# Prueba Técnica: Cálculo de Energía Adicional Requerida (Meteologica)

Herramienta de línea de comandos (CLI) desarrollada en Python para calcular la **energía adicional requerida** en España peninsular durante la semana del **23 al 29 de marzo de 2026**, utilizando exclusivamente generación eólica.

El cálculo base responde a la formulación:

$$\text{Energía Adicional} = \max(0, \text{Demanda} - \text{Eólica})$$

---

## Estructura del Proyecto

```text
meteologica_prueba/
├── data/
│   ├── demanda_semanal_espana_peninsular.csv   # Dataset base de demanda
│   └── eolica_551.json                        # Caché local de generación eólica (ESIOS)
├── output/                                     # CSVs generados tras la ejecución
│   ├── energia_adicional_cincominutal.csv
│   ├── energia_adicional_minutal.csv
│   ├── energia_adicional_horaria.csv
│   └── energia_adicional_diaria.csv
├── src/
│   ├── __init__.py
│   ├── calculo.py                              # Balance energético y remuestreo temporal
│   ├── cliente_esios.py                        # Extracción automática del indicador 551
│   ├── main.py                                 # Punto de entrada y gestión del CLI
│   └── parser_demanda.py                       # Parseo, limpieza y regularización del CSV
├── tests/
│   └── test_calculo.py                         # Pruebas unitarias de consistencia y balance
├── requirements.txt                            # Dependencias fijadas del proyecto
├── .gitignore
├── memoria.md                                  # Memoria técnica justificativa
└── README.md                                  
```

---

## Requisitos Previos

- **Python:** 3.11 o superior (compatible con Python 3.13).
- **Sistema Operativo:** Compatible con entornos Linux y macOS.

---

## Instalación y Configuración

**1. Clonar el repositorio y acceder al directorio:**

```bash
git clone https://github.com/vgarciacrespo/meteologica-prueba-tecnica
cd meteologica_prueba
```

**2. Crear y activar el entorno virtual de Python:**

```bash
python3 -m venv .venv
source .venv/bin/activate
```

**3. Instalar las dependencias requeridas:**

```bash
pip install -r requirements.txt
```

---

## Ejecución del Programa

Para ejecutar el flujo completo (procesado de demanda, descarga de ESIOS, cálculo de balance y exportación a las cuatro granularidades):

```bash
python src/main.py
```

> Por defecto, los archivos resultantes se almacenan en el directorio `output/`.

---

## Opciones del CLI

El comando admite los siguientes parámetros opcionales:

| Parámetro | Descripción | Valor por defecto |
|---|---|---|
| `--granularidad` | Resolución temporal deseada: `minutal`, `cincominutal`, `horaria`, `diaria`, `todas` | `todas` |
| `--demanda` | Ruta alternativa al archivo CSV de demanda peninsular | `data/demanda_semanal_espana_peninsular.csv` |
| `--output-dir` | Ruta al directorio donde se guardarán los archivos CSV resultantes | `output` |

### Ejemplos de uso

Exportar únicamente la resolución horaria:

```bash
python src/main.py --granularidad horaria
```

Guardar los resultados en una carpeta personalizada:

```bash
python src/main.py --output-dir resultados_semanales
```

---

## Granularidades y Formato de Salida

Todos los archivos generados cumplen con las siguientes especificaciones:

- **Huso horario:** UTC (`timestamp_utc` formateado en ISO 8601).
- **Unidad de energía:** MWh (`energia_adicional_mwh`).

| Granularidad | Registros generados | Total Energía Adicional |
|---|---|---|
| Minutal (1 min) | 10.020 | 3.328.406,33 MWh |
| Cincominutal (5 min) | 2.004 | 3.328.406,33 MWh |
| Horaria (1 h) | 167 | 3.328.406,33 MWh |
| Diaria (1 d) | 8 | 3.328.406,33 MWh |

> **Nota:** La energía acumulada total se conserva a lo largo de las cuatro resoluciones temporales.

---

## Ejecución de Tests

Para verificar la lógica de cálculo y la conservación de energía entre resoluciones:

```bash
python -m pytest
```
