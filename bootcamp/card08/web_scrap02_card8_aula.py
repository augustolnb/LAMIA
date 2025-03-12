from bs4 import BeautifulSoup
import requests
import time

def find_jobs():
    print('Descreva alguma habilidade com a qual você não está familiarizado')
    unfamiliar_skill =  input('> ')
    print('Filtrando . . . ')
    html_text = requests.get('https://www.timesjobs.com/candidate/parametricSearchResult.html?from=parametricSearch&clusterName=CLUSTER_COMP&hc=CLUSTER_COMP&compCluster=THE%20BOSTON%20GROUP').text
    soup = BeautifulSoup(html_text, 'lxml')
    jobs = soup.find_all('li', class_='clearfix job-bx wht-shd-bx')
    for index, job in enumerate(jobs):
        published_date = job.find('span', class_='sim-posted').span.text
        if 'few' in published_date:
            company_name = job.find('h3', class_='joblist-comp-name').text.replace('\n', '')
            skills = job.find('div', class_='more-skills-sections').text.replace('\n ', '')
            more_info = job.header.h2.a['href']
            if unfamiliar_skill not in skills: 
                with open(f'{index}.txt', 'w') as f:
                    #print(f'Publicação da vaga: {published_date}')
                    #print(f'Empresa: {company_name.strip()}')
                    #print(f'Habilidades: {skills.strip()}')
                    #print(f'Informações: {more_info}')
                    #print("\n############\n")
                    f.write(f'Publicação da vaga: {published_date}')
                    f.write(f'Empresa: {company_name.strip()}')
                    f.write(f'Informações: {more_info}')
                print(f'Arquivo salvo: posts/{index}')

                '''
                ATIVIDADE FINAL, RECEBER MULTIPLAS ENTRADAS DO USUARIOS
                E FILTRAR BASEADO NESSAS INFORMAÇÕES.
                '''

if __name__ == "__main__":
    while True:
        find_jobs()
        #time.wait = 10
        time.sleep(2)