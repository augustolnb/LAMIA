from airflow import DAG
from airflow.operators.python import PythonOperator
from airflow.operators.dummy import DummyOperator
from airflow.utils.trigger_rule import TriggerRule
from datetime import datetime

def download_website(url):
    # Implementação fictícia do download
    import random
    if random.random() > 0.5:  # 50% de chance de falha para demonstração
        raise Exception(f"Falha ao baixar {url}")
    print(f"Sucesso ao baixar {url}")
    return True

def process_data():
    print("Processando dados...")
    return True

def notify_success():
    print("Notificação de sucesso enviada")
    return True

def notify_failure():
    print("Notificação de falha enviada")
    return True

default_args = {
    'owner': 'airflow',
    'start_date': datetime(2023, 1, 1),
    'retries': 1,
}

with DAG(
    'website_download_pipeline',
    default_args=default_args,
    schedule_interval=None,
    catchup=False,
) as dag:
    
    # Tarefas de download
    download_a = PythonOperator(
        task_id='download_website_A',
        python_callable=download_website,
        op_kwargs={'url': 'http://website_a.com'},
    )
    
    download_b = PythonOperator(
        task_id='download_website_B',
        python_callable=download_website,
        op_kwargs={'url': 'http://website_b.com'},
    )
    
    # Tarefa que roda se AMBOS downloads falharem
    download_failed = DummyOperator(
        task_id='download_failed',
        trigger_rule=TriggerRule.ALL_FAILED,
    )
    
    # Tarefa que roda se AMBOS downloads tiverem sucesso
    download_succeed = DummyOperator(
        task_id='download_succeed',
        trigger_rule=TriggerRule.ALL_SUCCESS,
    )
    
    # Tarefa que roda se PELO MENOS UM download tiver sucesso
    process = PythonOperator(
        task_id='process',
        python_callable=process_data,
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )
    
    # Tarefa de notificação que roda se PELO MENOS UM download tiver sucesso
    notif_a = PythonOperator(
        task_id='notif_a',
        python_callable=notify_success,
        trigger_rule=TriggerRule.ONE_SUCCESS,
    )
    
    # Tarefa de notificação que roda se PELO MENOS UM download falhar
    notif_b = PythonOperator(
        task_id='notif_b',
        python_callable=notify_failure,
        trigger_rule=TriggerRule.ONE_FAILED,
    )
    
    # Definindo as dependências
    [download_a, download_b] >> download_failed
    [download_a, download_b] >> download_succeed
    [download_a, download_b] >> process
    process >> notif_a
    [download_a, download_b] >> notif_b