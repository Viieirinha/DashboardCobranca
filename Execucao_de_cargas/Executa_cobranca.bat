@echo off
echo Iniciando a carga de dados...

cd C:\Users\matheus.fagundes\Documents\Dash_Cobranca\Execucao_de_cargas

for /F "usebackq tokens=1,* delims==" %%A in ("C:\Users\matheus.fagundes\Documents\Dash_Cobranca\.env") do (
    set %%A=%%B
)

set PGPASSWORD=%DB_PASSWORD%

set QUERY_FILE=C:\Users\matheus.fagundes\Documents\Dash_Cobranca\Execucao_de_cargas\cobranca.sql
set OUTPUT_FILE=C:\Users\matheus.fagundes\Documents\Dash_Cobranca\Bases\Fat_gerado_por.csv
set PGCLIENTENCODING=UTF-8

psql -U %DB_USER% -d %DB_NAME% -h %DB_HOST% -p %DB_PORT% -A -F ";" -f "%QUERY_FILE%" -o "%OUTPUT_FILE%"

echo Extracao finalizada com sucesso!
pause