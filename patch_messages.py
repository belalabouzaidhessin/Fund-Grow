import pymysql

def patch_db():
    try:
        connection = pymysql.connect(host='localhost', user='root', password='', database='fundgrow')
        cursor = connection.cursor()
        
        try:
            cursor.execute("ALTER TABLE messages ADD COLUMN is_read BOOLEAN DEFAULT FALSE;")
            connection.commit()
            print("Added is_read column to messages.")
        except Exception as e:
            print("Column 'is_read' might already exist or error:", e)
            
        connection.close()
    except Exception as e:
        print("Database error:", e)

if __name__ == '__main__':
    patch_db()
