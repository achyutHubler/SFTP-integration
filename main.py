import paramiko
from flask import Flask, request, jsonify
from datetime import datetime

app = Flask(__name__)


def create_sftp_folder(sftp, folder_path):
    try:
        sftp.stat(folder_path)
        return f"Folder '{folder_path}' already exists on the SFTP server."
    except FileNotFoundError:
        sftp.mkdir(folder_path)
        return f"Folder '{folder_path}' created on the SFTP server."


# def upload_file_to_sftp(sftp, local_file_path, remote_file_path):
#     sftp.put(local_file_path, remote_file_path)
#     return f"File '{local_file_path}' uploaded to '{remote_file_path}' on the SFTP server."
def upload_file_to_sftp(sftp, local_file_storage, remote_folder):
    original_filename = local_file_storage.filename

    remote_file_path = f"{remote_folder}/{original_filename}"

    sftp.putfo(local_file_storage.stream, remote_file_path)

    return f"File '{original_filename}' uploaded to '{remote_file_path}' on the SFTP server."


@app.route('/upload', methods=['POST'])
def upload_file():
    # SFTP server details
    host = 'eu-central-1.sftpcloud.io'
    port = 22
    username = '3c4b8be3ac7e4db99d5f33e7b91f8769'
    password = '1qNtMWFcFMnD0GEvSFoih6ETExVOItnc'

    # Remote directory details
    remote_base_dir = '..'
    current_year = datetime.now().year
    current_month = datetime.now().strftime("%B")
    remote_folder = f'{remote_base_dir}/{current_year}/{current_month}'

    # Local file path
    local_file = request.files['file']

    # Connect to the SFTP server
    transport = paramiko.Transport((host, port))
    transport.connect(username=username, password=password)
    sftp = paramiko.SFTPClient.from_transport(transport)

    # Print a success message for the connection
    print("Connected to SFTP server successfully.")

    # Create the folder if it doesn't exist
    create_sftp_folder(sftp, remote_folder)

    # Upload the file to the remote folder
    result = upload_file_to_sftp(sftp, local_file, remote_folder)

    # Disconnect from the SFTP server
    sftp.close()
    transport.close()

    return jsonify(result=result)


if __name__ == '__main__':
    app.run()
