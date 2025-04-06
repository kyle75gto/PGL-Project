import sys
import pandas as pd

if len(sys.argv) < 2:
    print("Usage : python csv_to_xlsx.py <fichier.csv>")
    sys.exit(1)

csv_file = sys.argv[1]
xlsx_file = csv_file.replace(".csv", ".xlsx")

try:
    df = pd.read_csv(csv_file)
    df.to_excel(xlsx_file, index=False)
    print(f" Conversion terminee : {xlsx_file}")
except Exception as e:
    print(f" Erreur : {e}")
