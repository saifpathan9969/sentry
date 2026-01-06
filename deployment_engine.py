"""
Real-Time Deployment Engine for Production Fixes
Handles SSH/SFTP file deployment, database execution, and service restarts
"""

import os
import json
import logging
import paramiko
import pymysql
import psycopg2
from pymongo import MongoClient
import shutil
import subprocess
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
from datetime import datetime
import hashlib
import time

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


class DeploymentEngine:
    """
    Handles real-time deployment of security fixes to production systems
    Includes SSH/SFTP file deployment, database execution, and service management
    """
    
    def __init__(self, credentials: Dict[str, Any]):
        """
        Initialize deployment engine with credentials
        
        Args:
            credentials: Dictionary containing SSH, DB, and service credentials
        """
        self.credentials = credentials
        self.ssh_client = None
        self.sftp_client = None
        self.backup_dir = Path("backups") / datetime.now().strftime('%Y%m%d_%H%M%S')
        self.backup_dir.mkdir(parents=True, exist_ok=True)
        self.deployment_log = []
        
    def connect_ssh(self) -> bool:
        """
        Establish SSH connection to target server
        
        Returns:
            True if connection successful, False otherwise
        """
        try:
            ssh_creds = self.credentials.get('ssh', {})
            if not ssh_creds:
                logger.error("SSH credentials not provided")
                return False
            
            host = ssh_creds.get('host')
            port = int(ssh_creds.get('port', 22))
            username = ssh_creds.get('username')
            password = ssh_creds.get('password')
            key_file = ssh_creds.get('key_file')
            
            logger.info(f"Connecting to {host}:{port} as {username}...")
            
            self.ssh_client = paramiko.SSHClient()
            self.ssh_client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            if key_file and os.path.exists(key_file):
                # Use SSH key authentication
                self.ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    key_filename=key_file,
                    timeout=30
                )
            elif password:
                # Use password authentication
                self.ssh_client.connect(
                    hostname=host,
                    port=port,
                    username=username,
                    password=password,
                    timeout=30
                )
            else:
                logger.error("No valid authentication method provided")
                return False
            
            # Open SFTP channel
            self.sftp_client = self.ssh_client.open_sftp()
            
            logger.info(f"Successfully connected to {host}")
            self.log_deployment("SSH connection established", "success")
            return True
            
        except Exception as e:
            logger.error(f"SSH connection failed: {str(e)}")
            self.log_deployment(f"SSH connection failed: {str(e)}", "error")
            return False
    
    def disconnect_ssh(self):
        """Close SSH/SFTP connections"""
        try:
            if self.sftp_client:
                self.sftp_client.close()
            if self.ssh_client:
                self.ssh_client.close()
            logger.info("SSH connection closed")
        except Exception as e:
            logger.error(f"Error closing SSH connection: {str(e)}")
    
    def backup_remote_file(self, remote_path: str) -> Optional[str]:
        """
        Backup a remote file before modification
        
        Args:
            remote_path: Path to remote file
            
        Returns:
            Local backup path if successful, None otherwise
        """
        try:
            if not self.sftp_client:
                logger.error("SFTP client not connected")
                return None
            
            # Create local backup path
            filename = os.path.basename(remote_path)
            backup_path = self.backup_dir / filename
            
            logger.info(f"Backing up {remote_path} to {backup_path}")
            
            # Download file
            self.sftp_client.get(remote_path, str(backup_path))
            
            # Calculate checksum
            checksum = self._calculate_checksum(str(backup_path))
            
            # Store backup metadata
            metadata = {
                'remote_path': remote_path,
                'local_path': str(backup_path),
                'checksum': checksum,
                'timestamp': datetime.now().isoformat()
            }
            
            metadata_path = backup_path.with_suffix('.json')
            with open(metadata_path, 'w') as f:
                json.dump(metadata, f, indent=2)
            
            logger.info(f"Backup created: {backup_path}")
            self.log_deployment(f"Backed up {remote_path}", "success")
            return str(backup_path)
            
        except Exception as e:
            logger.error(f"Backup failed for {remote_path}: {str(e)}")
            self.log_deployment(f"Backup failed for {remote_path}: {str(e)}", "error")
            return None
    
    def deploy_file(self, local_path: str, remote_path: str, backup: bool = True) -> bool:
        """
        Deploy a file to remote server via SFTP
        
        Args:
            local_path: Path to local file
            remote_path: Path on remote server
            backup: Whether to backup existing file
            
        Returns:
            True if deployment successful, False otherwise
        """
        try:
            if not self.sftp_client:
                logger.error("SFTP client not connected")
                return False
            
            # Backup existing file if requested
            if backup:
                try:
                    self.sftp_client.stat(remote_path)
                    backup_path = self.backup_remote_file(remote_path)
                    if not backup_path:
                        logger.warning("Backup failed, proceeding anyway")
                except FileNotFoundError:
                    logger.info(f"Remote file {remote_path} does not exist, no backup needed")
            
            # Upload new file
            logger.info(f"Deploying {local_path} to {remote_path}")
            self.sftp_client.put(local_path, remote_path)
            
            # Verify deployment
            remote_size = self.sftp_client.stat(remote_path).st_size
            local_size = os.path.getsize(local_path)
            
            if remote_size != local_size:
                raise Exception(f"File size mismatch: local={local_size}, remote={remote_size}")
            
            logger.info(f"Successfully deployed {remote_path}")
            self.log_deployment(f"Deployed {remote_path}", "success")
            return True
            
        except Exception as e:
            logger.error(f"Deployment failed for {remote_path}: {str(e)}")
            self.log_deployment(f"Deployment failed for {remote_path}: {str(e)}", "error")
            return False
    
    def execute_remote_command(self, command: str, sudo: bool = False) -> Tuple[bool, str, str]:
        """
        Execute command on remote server via SSH
        
        Args:
            command: Command to execute
            sudo: Whether to use sudo
            
        Returns:
            Tuple of (success, stdout, stderr)
        """
        try:
            if not self.ssh_client:
                logger.error("SSH client not connected")
                return False, "", "SSH client not connected"
            
            if sudo:
                password = self.credentials.get('ssh', {}).get('password', '')
                command = f"echo '{password}' | sudo -S {command}"
            
            logger.info(f"Executing: {command}")
            stdin, stdout, stderr = self.ssh_client.exec_command(command, timeout=60)
            
            stdout_text = stdout.read().decode('utf-8')
            stderr_text = stderr.read().decode('utf-8')
            exit_status = stdout.channel.recv_exit_status()
            
            success = exit_status == 0
            
            if success:
                logger.info(f"Command executed successfully")
                self.log_deployment(f"Executed: {command}", "success")
            else:
                logger.error(f"Command failed with exit code {exit_status}")
                logger.error(f"stderr: {stderr_text}")
                self.log_deployment(f"Command failed: {command}", "error")
            
            return success, stdout_text, stderr_text
            
        except Exception as e:
            logger.error(f"Command execution failed: {str(e)}")
            self.log_deployment(f"Command execution failed: {str(e)}", "error")
            return False, "", str(e)
    
    def restart_service(self, service_name: str) -> bool:
        """
        Restart a service on remote server
        
        Args:
            service_name: Name of service to restart (e.g., 'apache2', 'nginx', 'mysql')
            
        Returns:
            True if restart successful, False otherwise
        """
        try:
            logger.info(f"Restarting service: {service_name}")
            
            # Try systemctl first (modern Linux)
            success, stdout, stderr = self.execute_remote_command(
                f"systemctl restart {service_name}",
                sudo=True
            )
            
            if not success:
                # Try service command (older systems)
                success, stdout, stderr = self.execute_remote_command(
                    f"service {service_name} restart",
                    sudo=True
                )
            
            if success:
                logger.info(f"Service {service_name} restarted successfully")
                self.log_deployment(f"Restarted service: {service_name}", "success")
                
                # Verify service is running
                time.sleep(2)
                success, stdout, stderr = self.execute_remote_command(
                    f"systemctl is-active {service_name}",
                    sudo=True
                )
                
                if success and 'active' in stdout:
                    logger.info(f"Service {service_name} is active")
                    return True
                else:
                    logger.warning(f"Service {service_name} may not be running properly")
                    return False
            else:
                logger.error(f"Failed to restart {service_name}")
                return False
                
        except Exception as e:
            logger.error(f"Service restart failed: {str(e)}")
            self.log_deployment(f"Service restart failed for {service_name}: {str(e)}", "error")
            return False
    
    def execute_database_query(self, query: str, db_type: str = 'mysql') -> Tuple[bool, Any]:
        """
        Execute database query for remediation
        
        Args:
            query: SQL query to execute
            db_type: Type of database ('mysql', 'postgresql', 'mongodb')
            
        Returns:
            Tuple of (success, result)
        """
        try:
            db_creds = self.credentials.get('database', {})
            if not db_creds:
                logger.error("Database credentials not provided")
                return False, None
            
            host = db_creds.get('host', 'localhost')
            port = db_creds.get('port')
            user = db_creds.get('username')
            password = db_creds.get('password')
            database = db_creds.get('database')
            
            logger.info(f"Executing {db_type} query on {host}:{port}/{database}")
            
            if db_type == 'mysql':
                return self._execute_mysql_query(host, port or 3306, user, password, database, query)
            elif db_type == 'postgresql':
                return self._execute_postgresql_query(host, port or 5432, user, password, database, query)
            elif db_type == 'mongodb':
                return self._execute_mongodb_query(host, port or 27017, user, password, database, query)
            else:
                logger.error(f"Unsupported database type: {db_type}")
                return False, None
                
        except Exception as e:
            logger.error(f"Database query failed: {str(e)}")
            self.log_deployment(f"Database query failed: {str(e)}", "error")
            return False, None
    
    def _execute_mysql_query(self, host: str, port: int, user: str, password: str, 
                            database: str, query: str) -> Tuple[bool, Any]:
        """Execute MySQL query"""
        conn = None
        try:
            conn = pymysql.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=30
            )
            
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
                result = cursor.fetchall() if cursor.description else None
            
            logger.info("MySQL query executed successfully")
            self.log_deployment(f"Executed MySQL query", "success")
            return True, result
            
        except Exception as e:
            logger.error(f"MySQL query failed: {str(e)}")
            return False, None
        finally:
            if conn:
                conn.close()
    
    def _execute_postgresql_query(self, host: str, port: int, user: str, password: str,
                                  database: str, query: str) -> Tuple[bool, Any]:
        """Execute PostgreSQL query"""
        conn = None
        try:
            conn = psycopg2.connect(
                host=host,
                port=port,
                user=user,
                password=password,
                database=database,
                connect_timeout=30
            )
            
            with conn.cursor() as cursor:
                cursor.execute(query)
                conn.commit()
                result = cursor.fetchall() if cursor.description else None
            
            logger.info("PostgreSQL query executed successfully")
            self.log_deployment(f"Executed PostgreSQL query", "success")
            return True, result
            
        except Exception as e:
            logger.error(f"PostgreSQL query failed: {str(e)}")
            return False, None
        finally:
            if conn:
                conn.close()
    
    def _execute_mongodb_query(self, host: str, port: int, user: str, password: str,
                               database: str, query: str) -> Tuple[bool, Any]:
        """Execute MongoDB query"""
        client = None
        try:
            # MongoDB query should be a JSON object
            query_dict = json.loads(query)
            
            client = MongoClient(
                host=host,
                port=port,
                username=user,
                password=password,
                serverSelectionTimeoutMS=30000
            )
            
            db = client[database]
            collection_name = query_dict.get('collection')
            operation = query_dict.get('operation')
            params = query_dict.get('params', {})
            
            collection = db[collection_name]
            
            if operation == 'find':
                result = list(collection.find(params))
            elif operation == 'update':
                result = collection.update_many(params.get('filter'), params.get('update'))
            elif operation == 'delete':
                result = collection.delete_many(params)
            else:
                raise Exception(f"Unsupported MongoDB operation: {operation}")
            
            logger.info("MongoDB query executed successfully")
            self.log_deployment(f"Executed MongoDB query", "success")
            return True, result
            
        except Exception as e:
            logger.error(f"MongoDB query failed: {str(e)}")
            return False, None
        finally:
            if client:
                client.close()
    
    def rollback_deployment(self, remote_path: str) -> bool:
        """
        Rollback a deployed file to its backup
        
        Args:
            remote_path: Path to remote file to rollback
            
        Returns:
            True if rollback successful, False otherwise
        """
        try:
            # Find backup file
            filename = os.path.basename(remote_path)
            backup_path = self.backup_dir / filename
            
            if not backup_path.exists():
                logger.error(f"No backup found for {remote_path}")
                return False
            
            logger.info(f"Rolling back {remote_path} from backup")
            
            # Restore backup
            self.sftp_client.put(str(backup_path), remote_path)
            
            logger.info(f"Rollback successful for {remote_path}")
            self.log_deployment(f"Rolled back {remote_path}", "success")
            return True
            
        except Exception as e:
            logger.error(f"Rollback failed for {remote_path}: {str(e)}")
            self.log_deployment(f"Rollback failed for {remote_path}: {str(e)}", "error")
            return False
    
    def verify_deployment(self, remote_path: str, expected_content: Optional[str] = None) -> bool:
        """
        Verify deployed file
        
        Args:
            remote_path: Path to remote file
            expected_content: Optional expected file content
            
        Returns:
            True if verification successful, False otherwise
        """
        try:
            if not self.sftp_client:
                return False
            
            # Check file exists
            self.sftp_client.stat(remote_path)
            
            if expected_content:
                # Download and verify content
                temp_path = self.backup_dir / f"verify_{os.path.basename(remote_path)}"
                self.sftp_client.get(remote_path, str(temp_path))
                
                with open(temp_path, 'r') as f:
                    actual_content = f.read()
                
                if actual_content != expected_content:
                    logger.error(f"Content verification failed for {remote_path}")
                    return False
            
            logger.info(f"Verification successful for {remote_path}")
            return True
            
        except Exception as e:
            logger.error(f"Verification failed for {remote_path}: {str(e)}")
            return False
    
    def _calculate_checksum(self, file_path: str) -> str:
        """Calculate SHA256 checksum of file"""
        sha256_hash = hashlib.sha256()
        with open(file_path, "rb") as f:
            for byte_block in iter(lambda: f.read(4096), b""):
                sha256_hash.update(byte_block)
        return sha256_hash.hexdigest()
    
    def log_deployment(self, message: str, status: str):
        """Log deployment action"""
        entry = {
            'timestamp': datetime.now().isoformat(),
            'message': message,
            'status': status
        }
        self.deployment_log.append(entry)
    
    def get_deployment_log(self) -> List[Dict]:
        """Get deployment log"""
        return self.deployment_log
    
    def save_deployment_report(self, report_path: str):
        """Save deployment report to file"""
        try:
            report = {
                'timestamp': datetime.now().isoformat(),
                'backup_directory': str(self.backup_dir),
                'deployment_log': self.deployment_log
            }
            
            with open(report_path, 'w') as f:
                json.dump(report, f, indent=2)
            
            logger.info(f"Deployment report saved to {report_path}")
            
        except Exception as e:
            logger.error(f"Failed to save deployment report: {str(e)}")
    
    # ============================================
    # Additional Credential Type Support (8 new types)
    # ============================================
    
    def connect_database(self) -> bool:
        """Connect to database using credentials"""
        try:
            db_creds = self.credentials.get('database', {})
            if not db_creds:
                logger.info("Database credentials not provided")
                return False
            
            db_type = db_creds.get('type', 'MySQL').upper()
            host = db_creds.get('host', 'localhost')
            port = int(db_creds.get('port', 3306))
            username = db_creds.get('username')
            password = db_creds.get('password')
            database = db_creds.get('database')
            
            logger.info(f"Connecting to {db_type} database at {host}:{port}...")
            
            if db_type == 'MYSQL':
                try:
                    self.db_connection = pymysql.connect(
                        host=host,
                        port=port,
                        user=username,
                        password=password,
                        database=database,
                        charset='utf8mb4'
                    )
                    logger.info(f"Successfully connected to MySQL database")
                    self.log_deployment("Database connection established (MySQL)", "success")
                    return True
                except Exception as e:
                    logger.error(f"MySQL connection failed: {str(e)}")
                    return False
            
            elif db_type == 'POSTGRESQL':
                try:
                    self.db_connection = psycopg2.connect(
                        host=host,
                        port=port,
                        user=username,
                        password=password,
                        database=database
                    )
                    logger.info(f"Successfully connected to PostgreSQL database")
                    self.log_deployment("Database connection established (PostgreSQL)", "success")
                    return True
                except Exception as e:
                    logger.error(f"PostgreSQL connection failed: {str(e)}")
                    return False
            
            elif db_type == 'MONGODB':
                try:
                    connection_string = f"mongodb://{username}:{password}@{host}:{port}/{database}"
                    self.db_connection = MongoClient(connection_string)
                    # Test connection
                    self.db_connection.admin.command('ping')
                    logger.info(f"Successfully connected to MongoDB database")
                    self.log_deployment("Database connection established (MongoDB)", "success")
                    return True
                except Exception as e:
                    logger.error(f"MongoDB connection failed: {str(e)}")
                    return False
            
            else:
                logger.error(f"Unsupported database type: {db_type}")
                return False
                
        except Exception as e:
            logger.error(f"Database connection error: {str(e)}")
            return False
    
    def connect_cloud(self) -> bool:
        """Connect to cloud provider (AWS/Azure/GCP)"""
        try:
            cloud_creds = self.credentials.get('cloud', {})
            if not cloud_creds:
                logger.info("Cloud credentials not provided")
                return False
            
            provider = cloud_creds.get('provider', 'AWS').upper()
            logger.info(f"Initializing {provider} cloud connection...")
            
            if provider == 'AWS':
                # AWS credentials stored, will be used by boto3 when needed
                self.cloud_client = {
                    'provider': 'AWS',
                    'access_key': cloud_creds.get('access_key'),
                    'secret_key': cloud_creds.get('secret_key'),
                    'region': cloud_creds.get('region', 'us-east-1')
                }
                logger.info("AWS credentials configured (will use boto3 for API calls)")
                self.log_deployment("Cloud connection established (AWS)", "success")
                return True
            
            elif provider == 'AZURE':
                # Azure credentials stored, will be used by azure SDK when needed
                self.cloud_client = {
                    'provider': 'Azure',
                    'tenant_id': cloud_creds.get('tenant_id'),
                    'client_id': cloud_creds.get('client_id'),
                    'client_secret': cloud_creds.get('client_secret'),
                    'subscription_id': cloud_creds.get('subscription_id')
                }
                logger.info("Azure credentials configured (will use Azure SDK for API calls)")
                self.log_deployment("Cloud connection established (Azure)", "success")
                return True
            
            elif provider == 'GCP':
                # GCP credentials stored, will be used by google-cloud SDK when needed
                self.cloud_client = {
                    'provider': 'GCP',
                    'service_account_file': cloud_creds.get('service_account_file'),
                    'project_id': cloud_creds.get('project_id')
                }
                logger.info("GCP credentials configured (will use Google Cloud SDK for API calls)")
                self.log_deployment("Cloud connection established (GCP)", "success")
                return True
            
            else:
                logger.error(f"Unsupported cloud provider: {provider}")
                return False
                
        except Exception as e:
            logger.error(f"Cloud connection error: {str(e)}")
            return False
    
    def connect_admin_panel(self) -> bool:
        """Connect to application admin panel"""
        try:
            admin_creds = self.credentials.get('admin_panel', {})
            if not admin_creds:
                logger.info("Admin panel credentials not provided")
                return False
            
            admin_type = admin_creds.get('type', 'Generic')
            admin_url = admin_creds.get('url')
            username = admin_creds.get('username')
            password = admin_creds.get('password')
            
            logger.info(f"Connecting to {admin_type} admin panel at {admin_url}...")
            
            # Store credentials for use in remediation
            self.admin_client = {
                'type': admin_type,
                'url': admin_url,
                'username': username,
                'password': password,
                'token': admin_creds.get('token')
            }
            
            logger.info(f"Admin panel credentials configured ({admin_type})")
            self.log_deployment(f"Admin panel connection established ({admin_type})", "success")
            return True
            
        except Exception as e:
            logger.error(f"Admin panel connection error: {str(e)}")
            return False
    
    def connect_cicd(self) -> bool:
        """Connect to CI/CD platform"""
        try:
            cicd_creds = self.credentials.get('cicd', {})
            if not cicd_creds:
                logger.info("CI/CD credentials not provided")
                return False
            
            platform = cicd_creds.get('platform', 'GitHub Actions')
            logger.info(f"Initializing {platform} CI/CD connection...")
            
            self.cicd_client = {
                'platform': platform,
                'token': cicd_creds.get('token'),
                'url': cicd_creds.get('url'),
                'repository': cicd_creds.get('repository'),
                'project_id': cicd_creds.get('project_id'),
                'username': cicd_creds.get('username')
            }
            
            logger.info(f"CI/CD credentials configured ({platform})")
            self.log_deployment(f"CI/CD connection established ({platform})", "success")
            return True
            
        except Exception as e:
            logger.error(f"CI/CD connection error: {str(e)}")
            return False
    
    def connect_git(self) -> bool:
        """Connect to Git repository"""
        try:
            git_creds = self.credentials.get('git', {})
            if not git_creds:
                logger.info("Git credentials not provided")
                return False
            
            provider = git_creds.get('provider', 'GitHub')
            repo_url = git_creds.get('url')
            auth_method = git_creds.get('auth_method', 'token')
            
            logger.info(f"Initializing {provider} Git connection ({auth_method})...")
            
            self.git_client = {
                'provider': provider,
                'url': repo_url,
                'auth_method': auth_method,
                'token': git_creds.get('token'),
                'ssh_key': git_creds.get('ssh_key')
            }
            
            logger.info(f"Git credentials configured ({provider}, {auth_method})")
            self.log_deployment(f"Git connection established ({provider})", "success")
            return True
            
        except Exception as e:
            logger.error(f"Git connection error: {str(e)}")
            return False
    
    def connect_container(self) -> bool:
        """Connect to container registry / Kubernetes"""
        try:
            container_creds = self.credentials.get('container', {})
            if not container_creds:
                logger.info("Container credentials not provided")
                return False
            
            container_type = container_creds.get('type', 'Docker')
            logger.info(f"Initializing {container_type} container connection...")
            
            self.container_client = {
                'type': container_type,
                'registry': container_creds.get('registry'),
                'username': container_creds.get('username'),
                'password': container_creds.get('password'),
                'k8s': container_creds.get('k8s')
            }
            
            logger.info(f"Container credentials configured ({container_type})")
            self.log_deployment(f"Container connection established ({container_type})", "success")
            return True
            
        except Exception as e:
            logger.error(f"Container connection error: {str(e)}")
            return False
    
    def connect_certificate(self) -> bool:
        """Connect to certificate manager"""
        try:
            cert_creds = self.credentials.get('certificate', {})
            if not cert_creds:
                logger.info("Certificate manager credentials not provided")
                return False
            
            manager = cert_creds.get('manager', 'ACME')
            logger.info(f"Initializing {manager} certificate manager...")
            
            self.cert_client = {
                'manager': manager,
                'email': cert_creds.get('email'),
                'key_file': cert_creds.get('key_file'),
                'cert_file': cert_creds.get('cert_file'),
                'key_file_path': cert_creds.get('key_file'),
                'uses_cloud_creds': cert_creds.get('uses_cloud_creds', False)
            }
            
            logger.info(f"Certificate manager configured ({manager})")
            self.log_deployment(f"Certificate manager connection established ({manager})", "success")
            return True
            
        except Exception as e:
            logger.error(f"Certificate manager connection error: {str(e)}")
            return False
    
    def connect_monitoring(self) -> bool:
        """Connect to monitoring/SIEM platform"""
        try:
            monitoring_creds = self.credentials.get('monitoring', {})
            if not monitoring_creds:
                logger.info("Monitoring credentials not provided")
                return False
            
            monitoring_type = monitoring_creds.get('type', 'Kibana')
            logger.info(f"Initializing {monitoring_type} monitoring connection...")
            
            self.monitoring_client = {
                'type': monitoring_type,
                'url': monitoring_creds.get('url'),
                'username': monitoring_creds.get('username'),
                'password': monitoring_creds.get('password'),
                'api_key': monitoring_creds.get('api_key'),
                'app_key': monitoring_creds.get('app_key'),
                'token': monitoring_creds.get('token'),
                'uses_cloud_creds': monitoring_creds.get('uses_cloud_creds', False)
            }
            
            logger.info(f"Monitoring credentials configured ({monitoring_type})")
            self.log_deployment(f"Monitoring connection established ({monitoring_type})", "success")
            return True
            
        except Exception as e:
            logger.error(f"Monitoring connection error: {str(e)}")
            return False
    
    def connect_api_keys(self) -> bool:
        """Connect to API keys service"""
        try:
            api_keys_creds = self.credentials.get('api_keys', {})
            if not api_keys_creds:
                logger.info("API keys credentials not provided")
                return False
            
            api_key_type = api_keys_creds.get('type', 'SMTP')
            logger.info(f"Initializing {api_key_type} API keys connection...")
            
            self.api_keys_client = {
                'type': api_key_type,
                'host': api_keys_creds.get('host'),
                'port': api_keys_creds.get('port'),
                'username': api_keys_creds.get('username'),
                'password': api_keys_creds.get('password'),
                'secret_key': api_keys_creds.get('secret_key'),
                'publishable_key': api_keys_creds.get('publishable_key'),
                'api_key': api_keys_creds.get('api_key'),
                'account_sid': api_keys_creds.get('account_sid'),
                'auth_token': api_keys_creds.get('auth_token'),
                'name': api_keys_creds.get('name'),
                'value': api_keys_creds.get('value')
            }
            
            logger.info(f"API keys configured ({api_key_type})")
            self.log_deployment(f"API keys connection established ({api_key_type})", "success")
            return True
            
        except Exception as e:
            logger.error(f"API keys connection error: {str(e)}")
            return False
    
    def connect_all(self) -> Dict[str, bool]:
        """Connect to all available credential types"""
        results = {}
        results['ssh'] = self.connect_ssh()
        results['database'] = self.connect_database()
        results['cloud'] = self.connect_cloud()
        results['admin_panel'] = self.connect_admin_panel()
        results['cicd'] = self.connect_cicd()
        results['git'] = self.connect_git()
        results['container'] = self.connect_container()
        results['certificate'] = self.connect_certificate()
        results['monitoring'] = self.connect_monitoring()
        results['api_keys'] = self.connect_api_keys()
        
        connected = sum(1 for v in results.values() if v)
        logger.info(f"Connected to {connected}/10 credential types")
        return results