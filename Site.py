import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
import re

# Configuração da página
st.set_page_config(layout="wide", page_title="Análise de Experimentos")

# Dados hardcoded para o Experimento 1
dados_experimento_1 = {
    "GCC_1": {
        "Separado": {
            "Hit Rate": 52.3,
            "Miss Rate": 47.7,
        },
        "Unificado": {
            "Hit Rate": 91.14,
            "Miss Rate": 8.86,
        },
    },
    "VORTEX_2": {
        "Separado": {
            "Hit Rate": 90.1,
            "Miss Rate": 9.9,
        },
        "Unificado": {
            "Hit Rate": 94.7,
            "Miss Rate": 5.3,
        },
    }
}

# Função para carregar os dados de um experimento
def load_experiment_data(experiment_path):
    data = {}
    for root, _, files in os.walk(experiment_path):
        test_name = os.path.basename(root)
        test_data = []
        for file in files:
            if file.endswith(".csv"):  
                file_path = os.path.join(root, file)
                try:
                    df = pd.read_csv(file_path, delimiter=",", decimal='.', on_bad_lines="warn")
                    df["Source File"] = file 
                    test_data.append(df)
                except pd.errors.EmptyDataError:
                    st.warning(f"Arquivo vazio: {file_path}")
                except pd.errors.ParserError:
                    st.warning(f"Erro ao ler o arquivo: {file_path}. Verifique o formato do CSV.")
        if test_data:
            data[test_name] = pd.concat(test_data, ignore_index=True)
    return data

# Função para extrair a ordem numérica do nome do arquivo
def extract_test_order(file_name):
    match = re.search(r"(\d+\.\d+)", file_name)
    if match:
        return float(match.group(1))
    return 0

# Função para gerar gráfico de linha de tempo
def gerar_grafico_linha(dados, teste):
    # Cria um DataFrame para os dados
    dados_grafico = pd.DataFrame({
        "Tipo": ["Hit Rate", "Miss Rate", "Hit Rate", "Miss Rate"],
        "Cache": ["Separado", "Separado", "Unificado", "Unificado"],
        "Taxa (%)": [
            dados[teste]["Separado"]["Hit Rate"],
            dados[teste]["Separado"]["Miss Rate"],
            dados[teste]["Unificado"]["Hit Rate"],
            dados[teste]["Unificado"]["Miss Rate"],
        ]
    })

    # Gera o gráfico de linha
    plt.figure(figsize=(10, 6))
    sns.lineplot(data=dados_grafico, x="Cache", y="Taxa (%)", hue="Tipo", marker="o", markersize=10)
    plt.title(f"Comparação de Hit Rate e Miss Rate para {teste}")
    plt.xlabel("Tipo de Cache")
    plt.ylabel("Taxa (%)")
    plt.ylim(0, 100)  # Limita o eixo Y de 0% a 100%
    plt.grid(True)  # Adiciona uma grade ao gráfico
    st.pyplot(plt)

# Função para formatar valores grandes no eixo Y
def format_large_numbers(value, _):
    if value >= 1e9:  # Bilhões
        return f'{value / 1e9:.1f}B'
    elif value >= 1e6:  # Milhões
        return f'{value / 1e6:.1f}M'
    elif value >= 1e3:  # Milhares
        return f'{value / 1e3:.1f}K'
    else:
        return f'{value:.0f}'

# Interface do Streamlit
experiments_dir = "./" 
st.sidebar.title("Navegação")
selected_experiment = st.sidebar.selectbox("Selecione o Experimento", ["Experimento 1", "Experimento 2.1", "Experimento 2.2", "Experimento 3", "Experimento 4"])
experiment_path = os.path.join(experiments_dir, selected_experiment)

# Caso especial para o Experimento 1
if selected_experiment == "Experimento 1":
    st.title("Análise do Experimento 1")

    # Seleção do teste (GCC_1 ou VORTEX_2)
    teste_selecionado = st.sidebar.selectbox("Selecione o Teste", ["GCC_1", "VORTEX_2"])

    # Gera o gráfico de linha de tempo
    st.subheader(f"Gráfico de Comparação para {teste_selecionado}")
    gerar_grafico_linha(dados_experimento_1, teste_selecionado)

else:
    # Carregamento dos dados para outros experimentos
    experiment_data = load_experiment_data(experiment_path)
    if not experiment_data:
        st.warning(f"Nenhum dado encontrado para {selected_experiment}.")
    else:
        st.title(f"Análise do {selected_experiment}")
        available_tests = [test for test in ["GCC_1", "VORTEX_2"] if test in experiment_data]
        
        if available_tests:
            st.sidebar.subheader("Seleção do Teste") 
            selected_test = st.sidebar.selectbox("Selecione o Teste", available_tests, key="test_selector")
            
            if "Metric" in experiment_data[selected_test].columns:
                metrics = experiment_data[selected_test]["Metric"].unique().tolist()
                
                if metrics:
                    selected_metric = st.selectbox("Selecione a Métrica para Análise", metrics, key="metric_selector")
                    metric_data = experiment_data[selected_test][experiment_data[selected_test]["Metric"] == selected_metric]
                    metric_data["Teste"] = selected_test
                    
                    if not metric_data.empty:
                        metric_data["Test Order"] = metric_data["Source File"].apply(extract_test_order)
                        metric_data = metric_data.sort_values(by="Test Order")

                        # Gera o gráfico
                        st.subheader(selected_test)
                        plt.figure(figsize=(10, 6))
                        
                        if "miss_rate" in selected_metric.lower():
                            # Gráfico de linha para métricas com "miss_rate"
                            sns.lineplot(data=metric_data, x='Source File', y='Value', marker='o', color='b')
                            plt.title(f'Valor da Métrica {selected_metric} para {selected_test}')
                            plt.xlabel('Arquivo CSV')
                            plt.ylabel('Valor da Métrica (%)')
                            plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x * 100:.2f}%'))  # Formato de porcentagem
                            plt.xticks(rotation=45, ha='right')
                            
                        else:
                            # Gráfico de coluna para outras métricas
                            sns.barplot(data=metric_data, x='Source File', y='Value', color='b')
                            plt.title(f'Valor da Métrica {selected_metric} para {selected_test}')
                            plt.xlabel('Arquivo CSV')
                            plt.ylabel('Valor da Métrica')
                            plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(format_large_numbers))  # Formata valores grandes
                            plt.xticks(rotation=45, ha='right')
                        
                        st.pyplot(plt)
                        
                    else:
                        st.warning("Nenhum dado disponível para exibição de métricas.")
                else:
                    st.warning("Nenhuma métrica foi encontrada.")
            else:
                st.warning("A coluna 'Metric' não foi encontrada nos dados.")