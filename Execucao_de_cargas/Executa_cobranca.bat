cd C:\Users\matheus.fagundes\Documents\Dash_Cobranca\Execucao_de_cargas
set PGUSER=cliente_matheus_fagundes
set PGPASSWORD=YzkwMTE5YzYxY2Q5
set PGHOST=144.22.173.101
set PGPORT=5432
set PGDATABASE=dbemp00489

set QUERY_FILE=C:\Users\matheus.fagundes\Documents\Dash_Cobranca\Execucao_de_cargas\cobranca.sql
set OUTPUT_FILE=C:\Users\matheus.fagundes\Documents\Dash_Cobranca\Bases\Fat_gerado_por.csv

set PGCLIENTENCODING=UTF-8
psql -U %PGUSER% -d %PGDATABASE% -h %PGHOST% -p %PGPORT% -A -F ";" -f "%QUERY_FILE%" -o "%OUTPUT_FILE%"

pause