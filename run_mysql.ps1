# Lanza la app Flask apuntando a MySQL de Clever Cloud.
# Ejecuta en PowerShell desde la carpeta del proyecto:
#   ./run_mysql.ps1

$env:MYSQL_HOST = "bfgmvgfdcayficn3c779-mysql.services.clever-cloud.com"
$env:MYSQL_PORT = "3306"
$env:MYSQL_DATABASE = "bfgmvgfdcayficn3c779"
$env:MYSQL_USER = "uea8z75dukaokmya"
$env:MYSQL_PASSWORD = "Pw0xdTXkH7loyjh4XklP"
$env:USE_MYSQL = "1"

python app.py
