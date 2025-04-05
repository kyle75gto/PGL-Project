HTML_FILE="velib_page.html"
CSV_FILE="identifiants_velib.csv"

echo " Lancement de la récupération dynamique du HTML Velib"

python velib_playwright.py

#supprime ligne problématique qui a un ID douteux

sed -i '/13118_relais/d' "$HTML_FILE"

# Extraire les identifiants (5 chiffres uniquement)

grep -oP '<span title="\K\d{4,5}(?=" dir="auto")' "$HTML_FILE" > ids.txt

grep -oP '<span title="\K\d+(?=" dir="auto">)' velib_page.html | sed -n '2~6p' > bornettes.txt

grep -oP '<span title="\K\d+(?=" dir="auto">)' velib_page.html | sed -n '3~6p' > total_velos.txt

grep -oP '<span title="\K\d+(?=" dir="auto">)' velib_page.html | sed -n '4~6p' > velos_mecaniques.txt

grep -oP '<span title="\K\d+(?=" dir="auto">)' velib_page.html | sed -n '5~6p' > velos_electriques.txt

# Créer le fichier CSV

echo "Identifiant_Station,Bornettes_Libres,Total_Velos_Dispo,Velos_Mecaniques,Velos_Electriques" > "$CSV_FILE"
paste -d ',' ids.txt bornettes.txt total_velos.txt velos_mecaniques.txt velos_electriques.txt >> "$CSV_FILE"

rm ids.txt bornettes.txt total_velos.txt velos_mecaniques.txt velos_electriques.txt

echo " Fichiers générés :"
echo "   - HTML : $HTML_FILE"
echo "   - CSV  : $CSV_FILE"
