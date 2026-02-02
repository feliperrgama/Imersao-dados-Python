# Importação das Bibliotecas:
import pandas as pd
import plotly.express as px
import streamlit as st

# ---- Configuração da página do site ----
# Definindo o título da página, o icone e o layout:
st.set_page_config(
    page_title='Dashboard de Salários na Área de Dados',
    page_icon='📊',
    layout='wide' # Deixa a página larga e não compacta
)

# ---- Carregamento dos dados ----
data_frame = pd.read_csv("https://raw.githubusercontent.com/vqrca/dashboard_salarios_dados/refs/heads/main/dados-imersao-final.csv")


# ---- Barra lateral (Filtros) ----
st.sidebar.header("🔍 Filtros")


# Filtro por ano
anos_disponiveis = sorted(data_frame['ano'].unique())
anos_selecionados = st.sidebar.multiselect("Ano", anos_disponiveis, max_selections=len(data_frame['ano'].unique()), placeholder="Escolha as opções que deseja")

# Filtro por experiência
experiencias_disponiveis = sorted(data_frame['senioridade'].unique())
experiencias_selecionadas = st.sidebar.multiselect("Experiência", experiencias_disponiveis, max_selections=len(data_frame['senioridade'].unique()), placeholder="Escolha as opções que deseja")

# Filtro para tipo de contrato
contratos_disponiveis = sorted(data_frame['contrato'].unique())
contratos_selecionadas = st.sidebar.multiselect("Tipo de Contrato", contratos_disponiveis, max_selections=len(data_frame['contrato'].unique()), placeholder="Escolha as opções que deseja")

# Filtro por tamanho da empresa:
tamanhos_disponiveis = sorted(data_frame['tamanho_empresa'].unique())
tamanhos_selecionados = st.sidebar.multiselect("Tamanho da Empresa", tamanhos_disponiveis, max_selections=len(data_frame['tamanho_empresa'].unique()), placeholder="Escolha as opções que deseja")


# ---- Filtragem do DataFrame ----
# O dataframe tem de ser filtrado com base nas seleções do usuário na barra lateral, na qual estão os filtros. Este é o componente visual dos filtros. Aqui ocorre a aplicação dos filtros:
data_frame_filtrado = data_frame[
    (data_frame['ano'].isin(anos_selecionados)) &
    (data_frame['senioridade'].isin(experiencias_selecionadas)) &
    (data_frame['contrato'].isin(contratos_selecionadas)) &
    (data_frame['tamanho_empresa'].isin(tamanhos_selecionados))
]


# ---- Contepudo Principal do Site ----
st.title('Dashboard de Análise de Salários na Área de Dados')
st.markdown('Explore os dados salariais na área de dados dos últimos anos. Utilize os filtros à esquerda para refinar sua análise') # Subtítulo

# ---- Métricas Principais (KPIs)
st.subheader('Métricas gerais (Salário anual em USD)')

if not data_frame_filtrado.empty:
    salario_medio = data_frame_filtrado['usd'].mean().round(2)
    salario_maximo = data_frame_filtrado['usd'].max()
    total_registos = data_frame_filtrado['usd'].shape[0]
    cargo_mais_frequente = data_frame_filtrado['cargo'].mode()[0]
else:
    salario_medio, salario_maximo, total_registos, cargo_mais_frequente = 0, 0, 0, " "

col1, col2, col3, col4 = st.columns(4)
col1.metric("Salário Média", f'{salario_medio:,.2f}')
col2.metric("Salário Máximo", f'{salario_maximo:,.2f}')
col3.metric('Total de Registros', f'{total_registos:,}')
col4.metric('Cargo mais Frequente', cargo_mais_frequente)

st.markdown('===')

# ---- Análises Visuaus com Plotly ----
st.subheader("Gráficos")

col_graf1, col_graf2 = st.columns(2)

with col_graf1:
    if not data_frame_filtrado.empty:
        top_cargos = data_frame_filtrado.groupby('cargo')['usd'].mean().round(2).nlargest(10).sort_values(ascending=True).reset_index()

        grafico_10_cargos = px.bar(
            top_cargos,
            x='usd',
            y='cargo',
            orientation='h',
            title='Top 10 cargos por salário médio',
            labels={'usd': 'Média salarial anual (usd)', 'cargo': ''}
        )

        grafico_10_cargos.update_layout(title_x=0.1, yaxis={'categoryorder': 'total ascending'})
        st.plotly_chart(grafico_10_cargos, True)
    else:
        st.warning("Nenhum dado para exibir no gráfico de cargos")

with col_graf2:
    if not data_frame_filtrado.empty:
        grafico_hist = px.histogram(
            data_frame_filtrado,
            x='usd',
            nbins=30,
            title="Distribuição de salários anuais",
            labels={'usd': 'Faixa salarial (USD)', 'count': ''}
        )
        grafico_hist.update_layout(title_x=0.1)
        st.plotly_chart(grafico_hist, True)
    else:
        st.warning('Nenhum dado para exibir no gráfico de distribuição')

col_graf3, col_graf4 = st.columns(2)

with col_graf3:
    if not data_frame_filtrado.empty:
        remoto_contagem = data_frame_filtrado['remoto'].value_counts().reset_index()
        remoto_contagem.columns = ['tipo_trabalho', 'quantidade']
        grafico_remoto = px.pie(
            remoto_contagem,
            names='tipo_trabalho',
            values='quantidade',
            title='Proporção dos tipos de trabalho'
        )
        grafico_remoto.update_traces(textinfo='percent+label')
        grafico_remoto.update_layout(title_x=0.1)
        st.plotly_chart(grafico_remoto, True)
    else:
        st.warning('Nenhum dado para exibir no gráfico dos tipos de trabalho')

with col_graf4:
    if not data_frame_filtrado.empty:
        df_ds = data_frame_filtrado[data_frame_filtrado['cargo'] == 'Data Scientist']
        media_ds_pais = data_frame_filtrado.groupby('residencia_iso3')['usd'].mean().round(2).reset_index()

        grafico_paises = px.choropleth(
            media_ds_pais,
            locations='residencia_iso3',
            color='usd',
            color_continuous_scale='rdylgn',
            title='Salário Médio de Cientista de Dados por país',
            labels={'usd': 'Salário Médio (USD)', 'residencia_iso3': 'País'}
        )
        grafico_paises.update_layout(title_x=0.1)
        st.plotly_chart(grafico_paises, True)
    else:
        st.warning("Nenhum dado para exibir o gráfico dos países!")


# ---- Data Frame Original para Análise ----
st.subheader('Dados Detalhados')
st.dataframe(data_frame_filtrado)
