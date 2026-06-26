import pymysql

def migrate_db():
    connection = pymysql.connect(host='localhost', user='root', password='', database='fundgrow')
    cursor = connection.cursor()

    # Users
    try: cursor.execute("ALTER TABLE users ADD COLUMN national_id_path VARCHAR(255);")
    except: pass
    try: cursor.execute("ALTER TABLE users ADD COLUMN employer_company VARCHAR(150);")
    except: pass
    
    # Projects
    try: cursor.execute("ALTER TABLE projects ADD COLUMN est_cost DECIMAL(15, 2);")
    except: pass
    try: cursor.execute("ALTER TABLE projects ADD COLUMN exp_revenue DECIMAL(15, 2);")
    except: pass
    try: cursor.execute("ALTER TABLE projects ADD COLUMN target_market TEXT;")
    except: pass
    try: cursor.execute("ALTER TABLE projects ADD COLUMN rejection_reason TEXT;")
    except: pass

    # Messages
    try: cursor.execute("""
        CREATE TABLE IF NOT EXISTS messages (
            id INT AUTO_INCREMENT PRIMARY KEY,
            project_id INT NOT NULL,
            sender_id INT NOT NULL,
            receiver_id INT NOT NULL,
            content TEXT NOT NULL,
            is_read BOOLEAN DEFAULT FALSE,
            created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY (project_id) REFERENCES projects(id) ON DELETE CASCADE,
            FOREIGN KEY (sender_id) REFERENCES users(id) ON DELETE CASCADE,
            FOREIGN KEY (receiver_id) REFERENCES users(id) ON DELETE CASCADE
        );
    """)
    except Exception as e:
        print("Error creating messages:", e)

    try: cursor.execute("ALTER TABLE messages ADD COLUMN is_read BOOLEAN DEFAULT FALSE;")
    except: pass

    connection.commit()
    connection.close()
    print("Migration successful.")

if __name__ == '__main__':
    migrate_db()
