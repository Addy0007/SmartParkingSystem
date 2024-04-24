import pymysql
import datetime
import socket

host = 'localhost'
database = 'parking_system'
user = 'root'
password = 'root1234'

def enter_details(reg_no):
    conn = pymysql.connect(host=host, user=user, password=password, database=database)
    cursor = conn.cursor()
    try:
        current_time = datetime.datetime.now().time()
        current_date = datetime.date.today()
        pslot = push(reg_no)  # Pass reg_no to push function
        sql_insert = """INSERT INTO entry (reg_no, entry_time, entry_date, slot_no)
                        VALUES (%s, %s, %s, %s)"""

        # Define the values to be inserted
        values = (reg_no, current_time, current_date, pslot)

        # Execute the SQL query with the values
        cursor.execute(sql_insert, values)

        conn.commit()

        return pslot

    except Exception as e:
        print("Database Error:", e)
        return False

    finally:
        cursor.close()
        conn.close()


def push(reg_no):
    try:
        conn = pymysql.connect(host=host, user=user, password=password, database=database)

        # Create a cursor object
        cursor = conn.cursor()

        # Find the topmost vacant parking slot (last in the stack)
        cursor.execute("SELECT slot_no FROM parking_slots WHERE is_occupied = FALSE ORDER BY slot_no DESC LIMIT 1")

        slot = cursor.fetchone()[0]
        if slot:
            # Mark the slot as occupied
            cursor.execute("UPDATE parking_slots SET is_occupied = TRUE WHERE slot_no = %s", (slot,))
            cursor.execute("UPDATE parking_slots SET car_number = %s WHERE slot_no = %s", (reg_no, slot))

        conn.commit()

        # Close the cursor and connection
        cursor.close()
        conn.close()
        return slot

    except pymysql.Error as e:
        print(f"Error:{e}")

def sender(text):
    PI2_IP = '192.168.1.15'  # Replace with Pi 2's IP address
    PORT = 39969

    try:

        if isinstance(text, int):
            text = str(text)

        # Create a UDP socket
        with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as sock:
            # Send a message to Raspberry Pi
            message = text.encode()  # Encode the text message to bytes
            sock.sendto(message, (PI2_IP, PORT))
            print(f"Successfully sent '{text}' to Raspberry Pi.")
    except Exception as e:
        print(f"Error occurred while sending data: {e}")