from flask import Response, request, render_template, send_from_directory, flash
import os
import base64
import json
from werkzeug import secure_filename
from dragencrypt import app
from dragencrypt.encryption import dragencrypt_aes256

from dragencrypt.models import Process

PUBLIC_DOWNLOAD_FOLDER = "/downloads/"
PROCESS_SUCCESS_MESSAGE = "success"
ENCRYPT_FILE_EXTENSION = ".encrypted"

@app.route("/<path:filename>")
def serve_css(filename):
    return send_from_directory(app.static_folder, filename)

@app.route('/downloads/<path:filename>', methods=['GET', 'POST'])
def download(filename):
    downloads = app.config['DOWNLOAD_FOLDER']
    return send_from_directory(directory=downloads, filename=filename)


# File encryption routes
@app.route('/encrypt', methods=['POST'])
def encrypt():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file:
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)
        
        # Move the file form the temporal folder to the upload folder
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        encrypted_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename + ENCRYPT_FILE_EXTENSION)
        file.save(upload_path)


        # Read contents of the file as binary
        with open(upload_path, "rb") as f:
            file_contents = f.read()
        
        # Create a password and salt for the file
        password = request.form['key']
        aes_key, hmac_key, salt, iterations = dragencrypt_aes256.make_keys(password)
        ciphertext, iv = dragencrypt_aes256.encrypt(file_contents, aes_key)
        hmac = dragencrypt_aes256.make_hmac(ciphertext, hmac_key)

        # Write salt and iteration data to file
        output = {
            "hmac": hmac,
            "iterations": iterations
        }

        # Encrypt data
        for key, value in ("ciphertext", ciphertext), ("iv", iv), ("salt", salt):
            output[key] = base64.b64encode(value).decode("utf-8")

        # Write encrypted to JSON
        output_data = json.dumps(output).encode("utf-8")

        # Write to file
        with open(encrypted_path, "wb") as f:
            f.write(output_data)
            f.close()

        # Generate download path
        download_path = PUBLIC_DOWNLOAD_FOLDER + filename + ENCRYPT_FILE_EXTENSION

        # Send response
        result = {"file_upload_status": PROCESS_SUCCESS_MESSAGE, \
                    "filename": download_path}
                    
        resp = Response(response=json.dumps(result), \
                    status=200, \
                    mimetype="application/json")

        return resp

# File decryption
@app.route('/decrypt', methods=['POST'])
def decrypt():
    # Get the name of the uploaded file
    file = request.files['file']
    # Check if the file is one of the allowed types/extensions
    if file:
        # Make the filename safe, remove unsupported chars
        filename = secure_filename(file.filename)

        # Move the file form the temporal folder to the upload folder
        upload_path = os.path.join(app.config['UPLOAD_FOLDER'], filename)
        decrypted_path = os.path.join(app.config['DOWNLOAD_FOLDER'], filename.replace(ENCRYPT_FILE_EXTENSION, ""))
        file.save(upload_path)

        # Read contents of the file as binary
        with open(upload_path, "rb") as f:
            file_contents = f.read()
        
        # Cipher and salt information
        password = request.form['key']
        data = json.loads(file_contents.decode("utf-8"))
        ciphertext = base64.b64decode(data["ciphertext"])
        iv = base64.b64decode(data["iv"])
        iterations = data["iterations"]
        salt = base64.b64decode(data["salt"])
        status = "success"

        # Generate Password
        aes_key, hmac_key, _, _ = dragencrypt_aes256.make_keys(password, salt, iterations)

        # Check HMAC Salt
        hmac = dragencrypt_aes256.make_hmac(ciphertext, hmac_key)
        if hmac != data["hmac"]:
            status = "Wrong encryption password"

        # Decrypt
        output_data = dragencrypt_aes256.decrypt(ciphertext, aes_key, iv)
        with open(decrypted_path, "wb") as f:
            f.write(output_data)
            f.close()

        # Generate download path
        download_path = PUBLIC_DOWNLOAD_FOLDER + filename.replace(ENCRYPT_FILE_EXTENSION, "")

        # Send response
        result = {"file_upload_status": status if status else PROCESS_SUCCESS_MESSAGE, \
                    "filename": download_path }

        resp = Response(response=json.dumps(result), \
                    status=200, \
                    mimetype="application/json")

        return resp