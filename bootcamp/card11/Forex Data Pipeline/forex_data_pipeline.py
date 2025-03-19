from airflow import DAG
from datetime import datetime, timedelta
# importando sensores http
from airflow.sensors.http_sensor import HttpSensor
from airflow.sensors.filesystem import FileSensor
from airflow.operators.python_operator import PythonOperator
from airflow.operators.bash import BashOperator
from airflow.operators.hive_operator import HiveOperator
from airflow.providers.apache.spark.operators.spark_submit import SparkSubmitOperator
from airflow.operators.email_operator import EmailOperator
from airflow.operators.slack_operator import SlackAPIPostOperator

import csv
import requests
import json

default_args ={
    "owner" : "airflow",
    "start_date" : datetime(2025, 3, 18 ), # Data de inicio
    "depends_on_past" : False,
    "email_on_failure" : False,
    "email_on_retry" : False, 
    "email" : "email_teste@gmail.com",
    "retries" : 1,
    "retry_delay" : timedelta(minutes=5)
}

def download_rates():
    ''' 
   with open('/usr/local/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        for row in reader:
            base = row['base']
            with_pairs = row['with_pairs'].split(' ')
            indata = requests.get('https://api.exchangeratesapi.io/latest?base=' + base).json()
            outdata = {'base': base, 'rates': {}, 'last_update': indata['date']}
            for pair in with_pairs:
                outdata['rates'][pair] = indata['rates'][pair]
            with open('/usr/local/airflow/dags/files/forex_rates.json', 'a') as outfile:
                json.dump(outdata, outfile)
                outfile.write('\n')
    '''
    with open('/usr/local/airflow/dags/files/forex_currencies.csv') as forex_currencies:
        reader = csv.DictReader(forex_currencies, delimiter=';')
        
        # Itera sobre cada linha do CSV
        for row in reader:
            base = row['base']  # Moeda base
            with_pairs = row['with_pairs'].split(' ')  # Pares de moedas

            # Faz a requisição à API
            url = f"https://api.exchangerate-api.com/v4/latest/{base}"
            response = requests.get(url)
            
            # Verifica se a requisição foi bem-sucedida
            if response.status_code == 200:
                indata = response.json()  # Converte a resposta para JSON

                # Verifica se a chave 'rates' está presente na resposta
                if 'rates' in indata:
                    # Cria o dicionário de saída
                    outdata = {
                        'base': base,
                        'rates': {},
                        'last_update': indata.get('date', 'N/A')  # Usa 'N/A' se 'date' não existir
                    }

                    # Itera sobre os pares de moedas
                    for pair in with_pairs:
                        if pair in indata['rates']:
                            outdata['rates'][pair] = indata['rates'][pair]
                        else:
                            print(f"Par {pair} não encontrado nas taxas da API.")

                    # Salva os dados no arquivo JSON
                    with open('/usr/local/airflow/dags/files/forex_rates.json', 'a') as outfile:
                        json.dump(outdata, outfile)
                        outfile.write('\n')  # Adiciona uma nova linha para o próximo registro
                else:
                    print(f"Resposta da API não contém 'rates' para a moeda base {base}.")
            else:
                print(f"Erro na requisição para a moeda base {base}. Código de status: {response.status_code}")



with DAG(dag_id="forex_data_pipeline", schedule_interval="@daily", default_args=default_args, catchup=False) as dag:
    
    is_forex_rates_available = HttpSensor(
        task_id="is_forex_rates_available",
        method="GET",
        http_conn_id="forex_api", # Nome da conexão com o airflow
        endpoint="latest",
        response_check=lambda response: "rates" in response.text,
        poke_interval=5,
        timeout=20
    )

    is_forex_currencies_file_available = FileSensor(
        task_id="is_forex_currencies_file_available",
        fs_conn_id="forex_path",
        filepath="forex_currencies.csv",
        poke_interval=5,
        timeout=20
    )

    downloading_rates = PythonOperator(
            task_id="downloading_rates",
            python_callable=download_rates
    )

    saving_rates = BashOperator(
        task_id="saving_rates",
        bash_command="""
            hdfs dfs -mkdir -p /forex && \
            hdfs dfs -put -f $AIRFLOW_HOME/dags/files/forex_rates.json /forex
            """
    )

    creating_forex_rates_table = HiveOperator(
        task_id="creating_forex_rates_table",
        hive_cli_conn_id="hive_conn",
        hql="""
            CREATE EXTERNAL TABLE IF NOT EXISTS forex_rates(
                base STRING,
                last_update DATE,
                eur DOUBLE,
                usd DOUBLE,
                nzd DOUBLE,
                gbp DOUBLE,
                jpy DOUBLE,
                cad DOUBLE
                )
            ROW FORMAT DELIMITED
            FIELDS TERMINATED BY ','
            STORED AS TEXTFILE
        """
    )

    forex_processing = SparkSubmitOperator(
        task_id="forex_processing",
        conn_id="spark_conn",
        application="/usr/local/airflow/dags/scripts/forex_processing.py",
        verbose=True
    )

    sending_email_notification = EmailOperator(
        task_id="sending_email",
        to="augustolnb@gmail.com",
        subject="forex_data_pipeline",
        html_content="""
            <h3>forex_data_pipeline succeeded</h3>
        """
    )

        sending_slack_notification = SlackAPIPostOperator(
        task_id="sending_slack",
        token="",
        username="airflow",
        text="DAG forex_data_pipeline: DONE",
        channel="#airflow-exploit"
    )

    is_forex_rates_available >> is_forex_currencies_file_available >> downloading_rates >> saving_rates >> sending_email_notification >> sending_slack_notification