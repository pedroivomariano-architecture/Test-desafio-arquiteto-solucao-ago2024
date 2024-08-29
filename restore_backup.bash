#!/bin/bash

# Configurações
BACKUP_DIR="/caminho/para/backups"  # Diretório onde estão os arquivos de backup
DB_NAME="nome_do_banco"             # Nome do banco de dados no RDS
DB_USER="usuario"                   # Usuário do banco de dados no RDS
DB_PASS="senha"                     # Senha do banco de dados no RDS
DB_HOST="rds-endpoint.amazonaws.com" # Endpoint do RDS
LOG_FILE="/caminho/para/log/restauracao.log"  # Arquivo de log

# Função para logar mensagens
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" >> $LOG_FILE
}

# Função para restaurar um arquivo de backup
restore_backup() {
    local backup_file=$1
    local checksum_file="${backup_file}.md5"
    
    # Verifica se o arquivo de backup existe
    if [[ ! -f $backup_file ]]; then
        log_message "Arquivo de backup não encontrado: $backup_file"
        exit 1
    fi
    
    # Verifica se o arquivo de checksum existe
    if [[ ! -f $checksum_file ]]; then
        log_message "Arquivo de checksum não encontrado: $checksum_file"
        exit 1
    fi
    
    # Verifica a integridade do arquivo de backup
    log_message "Verificando integridade do arquivo: $backup_file"
    cd $BACKUP_DIR
    md5sum -c $checksum_file
    if [[ $? -ne 0 ]]; then
        log_message "Erro: Arquivo de backup corrompido: $backup_file"
        exit 1
    fi
    
    # Descomprime o arquivo de backup se estiver comprimido
    if [[ $backup_file == *.gz ]]; then
        log_message "Descomprimindo arquivo de backup: $backup_file"
        gunzip -c $backup_file > "${backup_file%.gz}"
        backup_file="${backup_file%.gz}"
    fi
    
    # Restaura o arquivo de backup no banco de dados RDS
    log_message "Restaurando backup no RDS: $backup_file"
    mysql -h $DB_HOST -u $DB_USER -p$DB_PASS $DB_NAME < $backup_file
    if [[ $? -ne 0 ]]; then
        log_message "Erro: Falha ao restaurar o backup: $backup_file"
        exit 1
    fi
    
    log_message "Restauração concluída com sucesso: $backup_file"
}

# Função principal para restaurar os backups incrementais
main() {
    log_message "Iniciando restauração incremental de backups no RDS"

    for backup_file in $(ls -1 $BACKUP_DIR/*.sql.gz $BACKUP_DIR/*.sql 2>/dev/null | sort); do
        restore_backup $backup_file
    done

    log_message "Restauração incremental de backups no RDS concluída"
}

# Execução do script
main
