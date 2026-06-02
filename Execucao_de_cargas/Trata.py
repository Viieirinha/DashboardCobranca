import pandas as pd

# Leitura do arquivo (usando low_memory=False para evitar avisos de Dtype)
file_path = r'C:\Users\matheus.fagundes\Documents\Dash_Cobranca\Bases\Faixa.csv'
df = pd.read_csv(file_path, sep=";", low_memory=False, on_bad_lines="skip")

# Conversão de colunas de data (errors='coerce' transforma erros/vazios em NaT, evitando travamentos)
df['DATA_EMISSAO'] = pd.to_datetime(df['DATA_EMISSAO'], errors='coerce')
df['VCTO'] = pd.to_datetime(df['VCTO'], errors='coerce')

# Mesclagem do DataFrame
merged_df = pd.merge(df, df[['title', 'VCTO']], how='left', left_on='titulo_vinculado', right_on='title', suffixes=('', '_vinculado'))

# Cálculo da diferença de datas
merged_df['date_difference'] = (merged_df['VCTO_vinculado'] - merged_df['DATA_EMISSAO']).dt.days.abs()

# Função para categorizar a diferença de datas
def categorize_date_difference(diff):
    if pd.isna(diff):
        return 'SEM DATA' # Evita erro caso diff seja nulo
    elif 10 <= diff <= 29:
        return '10 A 29 DIAS'
    elif 30 <= diff <= 45:
        return '30 A 45 DIAS'
    elif 46 <= diff <= 60:
        return '46 A 60 DIAS'
    elif 61 <= diff <= 75:
        return '61 A 75 DIAS'
    elif 76 <= diff <= 90:
        return '76 A 90 DIAS'
    elif 91 <= diff <= 180:
        return '91 A 180 DIAS'
    elif 181 <= diff <= 360:
        return '181 A 360 DIAS'
    elif diff > 360:
        return '361 DIAS OU MAIS'
    else:
        return 'ABAIXO DE 11 DIAS'

# Aplicação da função de categorização
merged_df['category'] = merged_df['date_difference'].apply(categorize_date_difference)

# Listas de operadores e natureza financeira selecionados (Removida a duplicidade da Mavis)
selected_operators = [
    'ERICK MEDRADO DOS SANTOS BELEM','MAVIS ERMIRCIA DIAS DOS SANTOS','GEISIANE ALVES RIBEIRO','KEMILLY THAUANNY LIMA',
    'CLAUDIA SANDRA DA SILVA','ELIZABETE MEYRE DA SILVA','VANESSA REIS LIMA','JOAO BOSCO OLIVEIRA LEITAO',
    'ELLEN CHRISTINA MENDONCA DA SILVA','GRACE KELLY PEREIRA LEISTER','JAIR TEIXEIRA CHAVES PONTE','CAIO COSTA DE OLIVEIRA',
    'ALLANN BRENDOW ALVES BARBOSA PAVESE','Luciana Rodrigues da Silva','SAMALA STEFANE CONCEICAO DA SILVA', 
    'Geovana Monteiro Lima Sousa','JOAO VITOR GAMA SOUZA','Sara Rayssa Pereira','Alline Morais de Almeida',
    'Rosangela Braz de Carvalho e Sousa', 'TATIANY CORREIA VIANA MENDES', 'RENATA PIMENTA ALVES','Jabez da Silva Sousa', 
    'Simone Rodrigues da Costa', 'Guilherme Oliveira Caixeta dos Santos', 'Ellen Nara Lima Santana', 
    'Andreia Cristina Batista de Oliveira', 'Maiky Santos Silva', 'Catia da Silva Rodrigues Ribeiro', 
    'Daniel Rodrigues do Nascimento', 'Breno Gabriel Amorim Xavier', 'Eduardo Vicente Pereira Junior', 
    'João Pedro Cabral Cordeiro', 'Tiago Francisco Rodrigues Alcantara', 'Marcos Vinicius Moreira Ribeiro', 
    'Flavia Santos Silva', 'Izabella Vitoria Reis Evangelista', 'RADIR FELIPE RODRIGUES NUNES',
    'Josiquele Pereira de Oliveira', 'Barbara Kathleen Ferreira de Queiroz', 'Patricia Xavier Ramos', 
    'Ildson Gomes de Abreu', 'Ludmyla Luana dos Santos Goncalves', 'Agata Isabela Silva dos Santos', 
    'Carlos Alberto da Silva Freitas', 'Levy Augusto Santana Rodrigues', 'Eliene de Fátima correia', 
    'Geovanna Gomes da Silva', 'Giovanna Tatyelle da Marcena Dantas','Elison Diogo Costa da Silva', 
    'Steffany Araujo França', 'Markhel Oliveira Sousa'
]
selected_natureza_finance = ['OR - Receitas Renegociação', 'RS - Receita Serviço SCM', 'O - Baixa de Títulos']

# Filtragem do DataFrame
filtered_df = merged_df[(merged_df['OPERADOR'].isin(selected_operators)) & (merged_df['NATUREZA FINANCE'].isin(selected_natureza_finance))]

# Limpeza de Duplicadas
filtered_df = filtered_df.drop_duplicates()
filtered_df = filtered_df.sort_values(by='title_vinculado', na_position='last')
filtered_df = filtered_df.drop_duplicates(subset=['title'], keep='first')

# Salvamento do DataFrame SEM A COLUNA DE ÍNDICE (Isso evita erros no app.py)
output_path = r'C:\\Users\\matheus.fagundes\\Documents\\Dash_Cobranca\\Bases\\FaixaDeAtraso.csv'
filtered_df.to_csv(output_path, index=False)
print(f"Base de faixa de atraso tratada e salva com sucesso em: {output_path}")