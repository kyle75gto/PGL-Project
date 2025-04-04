CHROME_PATH="C:\Program Files\Google\Chrome\Application\chrome.exe"
URL="https://opendata.paris.fr/explore/embed/dataset/velib-disponibilite-en-temps-reel/table/?disjunctive.is_renting&disjunctive.is_installed&disjunctive.is_returning&disjunctive.name&disjunctive.nom_arrondissement_communes"
HTML_FILE="velib_page.html"
CSV_FILE="identifiants_velib.csv"

# Utiliser Chrome Headless pour capturer le vrai HTML avec JavaScript exécuté
"$CHROME_PATH" --headless --disable-gpu --virtual-time-budget=5000 --dump-dom "$URL" > "$HTML_FILE"

# Vérifier si le HTML a été récupéré
if [ ! -s "$HTML_FILE" ]; then
  echo " ERREUR : HTML vide. Chrome n'a pas récupéré les données."
  exit 1
fi

# Extraire les identifiants (5 chiffres uniquement)
grep -oP '<span title="\K\d{4,5}(?=" dir="auto")' "$HTML_FILE" > temp_ids.txt

# Créer le fichier CSV
echo "Identifiant_Station" > "$CSV_FILE"
cat temp_ids.txt >> "$CSV_FILE"

rm temp_ids.txt

echo " Fichiers générés :"
echo "   - HTML : $HTML_FILE"
echo "   - CSV  : $CSV_FILE"