
import paramiko
from flask import Flask, request, jsonify
from datetime import datetime
import requests
from io import BytesIO

app = Flask(__name__)


# def create_sftp_folder(sftp, folder_path):
#     try:
#         sftp.stat(folder_path)
#         return f"Folder '{folder_path}' already exists on the SFTP server."
#     except FileNotFoundError:
#         sftp.mkdir(folder_path)
#         return f"Folder '{folder_path}' created on the SFTP server."

def create_sftp_folder(sftp, folder_path):
    try:
        sftp.stat(folder_path)
        return f"Folder '{folder_path}' already exists on the SFTP server."
    except FileNotFoundError:
        parts = folder_path.split('/')
        current_path = ''

        for part in parts:
            current_path = f"{current_path}/{part}"
            try:
                sftp.stat(current_path)
            except FileNotFoundError:
                sftp.mkdir(current_path)

        return f"Folder '{folder_path}' created on the SFTP server."


def upload_file_to_sftp(sftp, local_file, remote_folder):
    landlord_name = request.json.get('landlord_name')
    invoice_date = request.json.get('invoice_date')

    invoice_date = datetime.strptime(invoice_date, "%d-%m-%Y")
    original_filename = f"{landlord_name}_{invoice_date.strftime('%Y_%m_%d')}.dat"

    remote_file_path = f"{remote_folder}/{original_filename}"

    sftp.putfo(local_file, remote_file_path)

    return f"File '{original_filename}' uploaded to '{remote_file_path}' on the SFTP server."


def download_file_from_url(file_url):
    try:
        response = requests.get(file_url)
        if response.status_code == 200:
            return BytesIO(response.content)
        else:
            return None
    except Exception as e:
        print(f"Error downloading file from URL: {e}")
        return None


@app.route('/upload', methods=['POST'])
def upload_file():
    host = 'indsftp.bata.com'
    port = 22
    username = 'lrhubler'
    password = 'L5Rhu$9!3r'

    invoice_date = request.json.get('invoice_date')

    invoice_date = datetime.strptime(invoice_date, "%d-%m-%Y")
    current_year = invoice_date.year
    current_month = invoice_date.strftime("%B")

    remote_base_dir = '/projhubler'
    remote_folder = f'{remote_base_dir}/{current_year}/{current_month}'

    file_url = request.json.get('file_url')
    downloaded_file = download_file_from_url(file_url)

    if downloaded_file is None:
        return jsonify(result="Error downloading file from URL")

    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    print("Connected to SFTP server successfully.")

    create_sftp_folder(sftp, remote_folder)

    result = upload_file_to_sftp(sftp, downloaded_file, remote_folder)

    sftp.close()
    transport.close()

    return jsonify(result=result)


if __name__ == '__main__':
    app.run()
