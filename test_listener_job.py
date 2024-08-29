import unittest
from unittest.mock import patch, MagicMock
import os
import logging
from listener_job import monitor_backup, upload_to_aws, listener_job

# Configura o logger
logging.basicConfig(filename='test_listener_job.log', level=logging.INFO, 
                    format='%(asctime)s - %(levelname)s - %(message)s')

class TestListenerJob(unittest.TestCase):

    @patch('os.path.getmtime')
    @patch('time.sleep', return_value=None)
    def test_monitor_backup(self, mock_sleep, mock_getmtime):
        logging.info("Iniciando teste: test_monitor_backup")
        backup_path = "/fake/path/backup.sql"
        initial_time = 100
        final_time = 200
        
        mock_getmtime.side_effect = [initial_time, initial_time, final_time]

        monitor_backup(backup_path)
        self.assertEqual(mock_getmtime.call_count, 3)
        mock_sleep.assert_called()
        logging.info("Teste test_monitor_backup concluído com sucesso.")

    @patch('boto3.client')
    def test_upload_to_aws_success(self, mock_boto_client):
        logging.info("Iniciando teste: test_upload_to_aws_success")
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3

        result = upload_to_aws('/fake/path/backup.sql', 'fake-bucket', 'backup.sql')
        self.assertTrue(result)
        mock_s3.upload_file.assert_called_with('/fake/path/backup.sql', 'fake-bucket', 'backup.sql')
        logging.info("Teste test_upload_to_aws_success concluído com sucesso.")

    @patch('boto3.client')
    def test_upload_to_aws_failure(self, mock_boto_client):
        logging.info("Iniciando teste: test_upload_to_aws_failure")
        mock_s3 = MagicMock()
        mock_boto_client.return_value = mock_s3
        mock_s3.upload_file.side_effect = FileNotFoundError

        result = upload_to_aws('/fake/path/backup.sql', 'fake-bucket', 'backup.sql')
        self.assertFalse(result)
        mock_s3.upload_file.assert_called()
        logging.info("Teste test_upload_to_aws_failure concluído com sucesso.")

    @patch('listener_job.monitor_backup')
    @patch('listener_job.upload_to_aws')
    def test_listener_job(self, mock_upload_to_aws, mock_monitor_backup):
        logging.info("Iniciando teste: test_listener_job")
        backup_path = '/fake/path/backup.sql'
        bucket_name = 'fake-bucket'
        s3_filename = 'backup.sql'
        
        mock_monitor_backup.return_value = None
        mock_upload_to_aws.return_value = True

        listener_job(backup_path, bucket_name, s3_filename)

        mock_monitor_backup.assert_called_with(backup_path)
        mock_upload_to_aws.assert_called_with(backup_path, bucket_name, s3_filename)
        logging.info("Teste test_listener_job concluído com sucesso.")

if __name__ == '__main__':
    unittest.main()
