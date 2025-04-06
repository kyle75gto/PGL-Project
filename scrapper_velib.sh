TIMESTAMP=$(date +"%Y-%m-%d_%H-%M")

# Fichiers avec timestamp
HTML_FILE="velib_page_$TIMESTAMP.html"
CSV_FILE="identifiants_velib_$TIMESTAMP.csv"

echo " Lancement de la recup du HTML avec Playwright..."

python velib_playwright.py "$HTML_FILE"

# Supprimer la ligne problématique qui n' a pas le même format
sed -i '/13118_relais/d' "$HTML_FILE"

# Extraire les données depuis le HTML
grep -oP '<span title="\K\d{4,5}(?=" dir="auto")' "$HTML_FILE" > ids.txt
grep -oP '<span title="\K\d+(?=" dir="auto">)' "$HTML_FILE" | sed -n '2~6p' > bornettes.txt
grep -oP '<span title="\K\d+(?=" dir="auto">)' "$HTML_FILE" | sed -n '3~6p' > total_velos.txt
grep -oP '<span title="\K\d+(?=" dir="auto">)' "$HTML_FILE" | sed -n '4~6p' > velos_mecaniques.txt
grep -oP '<span title="\K\d+(?=" dir="auto">)' "$HTML_FILE" | sed -n '5~6p' > velos_electriques.txt

# Créer le fichier CSV final
echo "Identifiant_Station,Bornettes_Libres,Total_Velos_Dispo,Velos_Mecaniques,Velos_Electriques" > "$CSV_FILE"
paste -d ',' ids.txt bornettes.txt total_velos.txt velos_mecaniques.txt velos_electriques.txt >> "$CSV_FILE"

# Nettoyage
rm ids.txt bornettes.txt total_velos.txt velos_mecaniques.txt velos_electriques.txt
rm "$HTML_FILE"

# Conversion CSV → XLSX avec Python
python csv_to_xlsx.py "$CSV_FILE"
XLSX_FILE="${CSV_FILE%.csv}.xlsx"

# Supprimer le CSV si conversion réussie
if [ -f "$XLSX_FILE" ]; then
  rm "$CSV_FILE"
  echo "   - XLSX : $XLSX_FILE"
  # Déplacer le fichier XLSX dans le dossier
  mv "$XLSX_FILE" "Datasets/$XLSX_FILE"
  echo "   - Fichier déplacé dans Datasets/"
else
  echo "    Conversion echouee. CSV conserve : $CSV_FILE"
fi
