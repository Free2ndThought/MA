#TODO create configuration tool to keep .env files in sync

#TODO create check to determine if any crawler or postgre instances are running currently
import os
import re


def get_running_dockers() -> ([str],[str]):
    running_docker_names , bound_docker_ports = [],[]
    docker_port_table = os.popen('docker container ls --format "table {{.Names}}\t{{.Ports}}" -a').read()
    service_table = os.popen('docker service ls --format "{{.Name}}')
    docker_entries = docker_port_table.split(sep='\n')
    for entry in docker_entries:
        entry_as_list = entry.split()
        if ['NAMES', 'PORTS'] == entry_as_list:
            continue
        elif entry_as_list.__len__() > 0:
            running_docker_names.append(entry_as_list.pop(0))
            for port in entry_as_list:
                if '0.0.0.0' in port:
                    bound_docker_ports.append(port.split(sep=':')[1].split(sep='-')[0])

    return running_docker_names, bound_docker_ports


def extract_services(file_contents: [str]):
    service_lines = []
    services = False
    for line in file_contents:
        if 'services:' in line:
            services = True
        elif re.match('^\S', line):
            services = False
        if re.match('^\s\s\S*:\n', line) and services:
            service_lines.append(line.lstrip().split(sep=':')[0])

    return service_lines


def match_env_variables():
    with open('./producer/.env', 'rb') as prod_env_file:
        producer_env_entries = prod_env_file.readlines()

    with open('./consumer/.env', 'rb') as cons_env_file:
        consumer_env_entries = cons_env_file.readlines()




def get_compose_service_names():
    with open('./producer/docker-compose.yml', 'r') as producer_compose_file:
        producer_compose_config = producer_compose_file.readlines()
        p_service_lines = extract_services(producer_compose_config)
        print(p_service_lines)

    with open('./consumer/docker-compose.yml', 'r') as consumer_compose_file:
        consumer_compose_config = consumer_compose_file.readlines()
        c_service_lines = extract_services(consumer_compose_config)
        print(c_service_lines)

if __name__ == '__main__':

    services_and_ports = get_running_dockers()
    print(services_and_ports)
    get_compose_service_names()

