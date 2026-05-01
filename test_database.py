from config.database import db_manager

def test_connections():
    try:
        # Test PostgreSQL
        cursor = db_manager.get_postgres_cursor()
        cursor.execute("SELECT version();")
        postgres_version = cursor.fetchone()
        print(f"✅ PostgreSQL connected: {postgres_version['version']}")
        
        # Test MongoDB
        mongo_collection = db_manager.get_mongo_collection('test')
        mongo_collection.insert_one({'test': 'connection'})
        print("✅ MongoDB connected successfully")
        
        # Clean up test data
        mongo_collection.delete_one({'test': 'connection'})
        
    except Exception as e:
        print(f"❌ Database test failed: {str(e)}")

if __name__ == "__main__":
    test_connections()