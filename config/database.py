import os
import psycopg2
from psycopg2.extras import RealDictCursor
import pymongo
from pymongo import MongoClient
import logging

class DatabaseConfig:
    # PostgreSQL Configuration
    POSTGRES_CONFIG = {
        'host': os.getenv('POSTGRES_HOST', 'localhost'),
        'port': os.getenv('POSTGRES_PORT', '5432'),
        'database': os.getenv('POSTGRES_DB', 'cybersecurity_db'),
        'user': os.getenv('POSTGRES_USER', 'cyber_admin'),
        'password': os.getenv('POSTGRES_PASSWORD', 'cyber')
    }
    
    # MongoDB Configuration
    MONGODB_CONFIG = {
        'host': os.getenv('MONGODB_HOST', 'localhost'),
        'port': int(os.getenv('MONGODB_PORT', '27017')),
        'database': os.getenv('MONGODB_DB', 'cybersecurity_logs')
    }

class DatabaseManager:
    def __init__(self):
        self.postgres_conn = None
        self.mongo_client = None
        self.mongo_db = None
        self.connect_databases()
    
    def connect_databases(self):
        try:
            # PostgreSQL Connection
            self.postgres_conn = psycopg2.connect(**DatabaseConfig.POSTGRES_CONFIG)
            self.postgres_conn.autocommit = True
            
            # MongoDB Connection
            self.mongo_client = MongoClient(
                host=DatabaseConfig.MONGODB_CONFIG['host'],
                port=DatabaseConfig.MONGODB_CONFIG['port']
            )
            self.mongo_db = self.mongo_client[DatabaseConfig.MONGODB_CONFIG['database']]
            
            print("✅ Database connections established successfully")
            
        except Exception as e:
            logging.error(f"Database connection error: {str(e)}")
            raise
    
    def get_postgres_cursor(self):
        return self.postgres_conn.cursor(cursor_factory=RealDictCursor)
    
    def get_mongo_collection(self, collection_name):
        return self.mongo_db[collection_name]
    
    def close_connections(self):
        if self.postgres_conn:
            self.postgres_conn.close()
        if self.mongo_client:
            self.mongo_client.close()

# Global database manager instance
db_manager = DatabaseManager()