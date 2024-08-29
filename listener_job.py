import os
import time
import boto3
import logging
from botocore.exceptions import NoCredentialsError

# Configura o logger
logging.basicConfig(filename='listener_job.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

def monitor_backup(backup_path):
    logging.info(f"Monitorando {backup_path} para backup...")
    initial_mod_time = os.path.getmtime(backup_path)
    while True:
        time.sleep(10)  # Aguarda 10 segundos antes de verificar novamente
        mod_time = os.path.getmtime(backup_path)
        if mod_time > initial_mod_time:
            logging.info("Backup finalizado.")
            break

def upload_to_aws(local_file, bucket, s3_file):
    s3 = boto3.client('s3')

    try:
        s3.upload_file(local_file, bucket, s3_file)
        logging.info(f"Upload do {local_file} para o bucket {bucket} com sucesso!")
        return True
    except FileNotFoundError:
        logging.error("O arquivo não foi encontrado.")
        return False
    except NoCredentialsError:
        logging.error("Credenciais AWS não encontradas.")
        return False

def listener_job(backup_path, bucket_name, s3_filename):
    try:
        monitor_backup(backup_path)
        success = upload_to_aws(backup_path, bucket_name, s3_filename)
        if success:
            logging.info("Job finalizado com sucesso.")
        else:
            logging.error("Job falhou durante o upload.")
    except Exception as e:
        logging.error(f"Erro no job: {str(e)}")
