import pandas as pd
import sys

def main():
    file_path = 'INVENTARIO.xlsx'
    print(f"Leyendo '{file_path}'...")
    try:
        # Load excel file to inspect sheets
        xl = pd.ExcelFile(file_path)
        print(f"\nHojas encontradas en el archivo: {xl.sheet_names}")
        
        # Load the first sheet (or default one) with header=1 to inspect structure
        print("\nLeyendo las primeras 10 filas de la primera hoja...")
        df = pd.read_excel(xl, sheet_name=xl.sheet_names[0], header=1, nrows=10)
        print("\nLectura exitosa!")
        print("\nNombres de las columnas detectadas (usando fila 1 como cabecera):")
        for idx, col in enumerate(df.columns):
            print(f"{idx + 1}. {repr(col)}")
        
        print("\nVista previa de las primeras 5 filas:")
        print(df.head(5).to_string())
    except Exception as e:
        print(f"Error al leer el archivo Excel: {e}", file=sys.stderr)

if __name__ == '__main__':
    main()
