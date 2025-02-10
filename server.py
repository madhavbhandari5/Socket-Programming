# server.py
import socket
import xml.etree.ElementTree as ET
import sqlite3
from lxml import etree

# Database setup
conn = sqlite3.connect('patients.db')
cursor = conn.cursor()
cursor.execute('''CREATE TABLE IF NOT EXISTS Patients
                  (PatientID INT PRIMARY KEY, Name TEXT, Age INT, Diagnosis TEXT)''')
conn.commit()

# Load XSD schema for validation
def load_xsd(schema_path):
    with open(schema_path, 'rb') as f:
        schema_root = etree.XML(f.read())
    return etree.XMLSchema(schema_root)

patient_xsd = load_xsd('patient_info.xsd')

def handle_client(data):
    try:
        # # Log received data
        # print("\nReceived data from client:")
        # print(data)

        # Validate XML against XSD
        xml_root = etree.fromstring(data)
        if not patient_xsd.validate(xml_root):
            raise ValueError("Invalid XML data: Does not conform to XSD schema")
        print("XML data is valid and conforms to the schema.")

        # Parse XML data
        root = ET.fromstring(data)
        patient_id = int(root.find('PatientID').text)
        name = root.find('Name').text
        age = int(root.find('Age').text)
        diagnosis = root.find('Diagnosis').text

        # Log parsed data
        print("Parsed patient data:")
        print(f"Patient ID: {patient_id}, Name: {name}, Age: {age}, Diagnosis: {diagnosis}")

        # Insert into database
        cursor.execute("INSERT INTO Patients (PatientID, Name, Age, Diagnosis) VALUES (?, ?, ?, ?)",
                       (patient_id, name, age, diagnosis))
        conn.commit()
        print("Patient data successfully added to the database.")

        # Create success response
        response = ET.Element('Response')
        ET.SubElement(response, 'Status').text = 'Success'
        ET.SubElement(response, 'Message').text = 'Patient data added successfully'
        return ET.tostring(response)
    except Exception as e:
        # Log error
        print("Error:", e)

        # Create failure response
        response = ET.Element('Response')
        ET.SubElement(response, 'Status').text = 'Failure'
        ET.SubElement(response, 'Message').text = str(e)
        return ET.tostring(response)

def start_server():
    server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    server.bind(('localhost', 12345))
    server.listen(1)
    print("Server listening on port 12345...")

    while True:
        client, addr = server.accept()
        print(f"\nConnection from {addr}")
        data = client.recv(1024).decode()
        response = handle_client(data)
        client.send(response)
        client.close()

if __name__ == '__main__':
    start_server()