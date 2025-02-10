# client.py
import socket
from lxml import etree

# Load XSD schema for server response validation
def load_xsd(schema_path):
    with open(schema_path, 'rb') as f:
        schema_root = etree.XML(f.read())
    return etree.XMLSchema(schema_root)

response_xsd = load_xsd('server_response.xsd')

def validate_response(xml_data):
    try:
        xml_root = etree.fromstring(xml_data)
        if not response_xsd.validate(xml_root):
            raise ValueError("Invalid server response: Does not conform to XSD schema")
        
        # Check if the response status is "Success"
        status = xml_root.find("Status").text
        if status != "Success":
            raise ValueError(f"Operation failed: {xml_root.find('Message').text}")
        
        return True
    except Exception as e:
        print("Validation Error:", e)
        return False

def send_patient_data():
    # Read XML data from file (or input manually)
    xml_file = input("Enter the XML file name (e.g., valid_patient.xml): ")
    with open(xml_file, 'r') as f:
        xml_data = f.read()

    # Send data to server
    client = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    client.connect(('localhost', 12345))
    client.send(xml_data.encode())

    # Receive and validate server response
    response = client.recv(1024).decode()
    if validate_response(response):
        print("Server Response is valid and operation was successful:", response)
    else:
        print("Server Response is invalid or operation failed:", response)

    client.close()

if __name__ == '__main__':
    send_patient_data()