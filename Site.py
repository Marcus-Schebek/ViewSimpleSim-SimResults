import streamlit as st
import pandas as pd
import os
import seaborn as sns
import matplotlib.pyplot as plt
import matplotlib.ticker as mtick
st.set_page_config(layout="wide", page_title="Análise de Experimentos")

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
experiments_dir = "./" 
st.sidebar.title("Navegação")
selected_experiment = st.sidebar.selectbox("Selecione o Experimento", ["Experimento 1", "Experimento 2", "Experimento 3", "Experimento 4"])
experiment_path = os.path.join(experiments_dir, selected_experiment)
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
            metrics = [m for m in experiment_data[selected_test]["Metric"].unique().tolist() if "_rate" in m]
            
            if metrics:
                selected_metric = st.selectbox("Selecione a Métrica para Análise", metrics, key="metric_selector")
                metric_data = experiment_data[selected_test][experiment_data[selected_test]["Metric"] == selected_metric]
                metric_data["Teste"] = selected_test
                
                if not metric_data.empty:
                    st.subheader(selected_test)
                    plt.figure(figsize=(10, 6))
                    sns.lineplot(data=metric_data, x='Source File', y='Value', marker='o', color='b')
                    plt.title(f'Valor da Métrica {selected_metric} para {selected_test}')
                    plt.xlabel('Arquivo CSV')
                    plt.ylabel('Valor da Métrica (%)')
                    plt.gca().yaxis.set_major_formatter(mtick.FuncFormatter(lambda x, _: f'{x * 100:.2f}%'))
                    plt.xticks(rotation=45, ha='right')
                    st.pyplot(plt)
                    
                else:
                    st.warning("Nenhum dado disponível para exibição de métricas.")
            else:
                st.warning("Nenhuma métrica contendo '_rate' foi encontrada.")
        else:
            st.warning("A coluna 'Metric' não foi encontrada nos dados.")
