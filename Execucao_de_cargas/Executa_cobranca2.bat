@echo off
cd C:\Users\savio.menezes\Documents\Dash_Cobranca\Execucao_de_cargas

set PGUSER=cliente_rpa
set PGPASSWORD=ZDdiNjZjYjNhMDk1
set PGHOST=144.22.173.101
set PGPORT=5432
set PGDATABASE=dbemp00489

set QUERY_FILE=C:\Users\savio.menezes\Documents\Dash_Cobranca\Execucao_de_cargas\cobranca.sql
set OUTPUT_FILE=C:\Users\savio.menezes\Documents\Dash_Cobranca\Bases\Fat_gerado_por.csv

set PGCLIENTENCODING=UTF-8

echo Executando query...

"C:\Program Files\PostgreSQL\16\bin\psql.exe" ^
  -U %PGUSER% ^
  -d %PGDATABASE% ^
  -h %PGHOST% ^
  -p %PGPORT% ^
  -A -F ";" ^
  -f "%QUERY_FILE%" ^
  -o "%OUTPUT_FILE%"

if %errorlevel% equ 0 (
    echo Query executada com sucesso!
) else (
    echo Erro na execucao da query. Codigo: %errorlevel%
)

pause
