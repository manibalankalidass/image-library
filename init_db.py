import os
import MySQLdb
from MySQLdb.constants import CLIENT
import config

def init_database():
    try:
        print(f"Connecting to MySQL at {config.MYSQL_HOST} (user: {config.MYSQL_USER})...")
        # Connect strictly without the database selected
        conn = MySQLdb.connect(
            host=config.MYSQL_HOST,
            user=config.MYSQL_USER,
            passwd=config.MYSQL_PASSWORD,
            client_flag=CLIENT.MULTI_STATEMENTS
        )
        cursor = conn.cursor()
        
        sql_file = os.path.join(os.path.dirname(os.path.abspath(__file__)), "database.sql")
        
        if os.path.exists(sql_file):
            print("Applying database.sql...")
            with open(sql_file, "r", encoding="utf-8") as f:
                sql = f.read()
                cursor.execute(sql)
                
                # Fetch all remaining query results from multi-statement execution
                while cursor.nextset() is not None:
                    pass
            
            conn.commit()
            print("Database setup complete! 'imagelibrary' and all tables are ready.")
        else:
            print("Warning: database.sql not found.")
            
        cursor.close()
        conn.close()
    except Exception as e:
        print(f"Database setup failed! Make sure your MySQL credentials in config.py / .env are correct.")
        print(f"Error details: {e}")

if __name__ == "__main__":
    init_database()
