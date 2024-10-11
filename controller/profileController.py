import io
import uuid
from flask import request, jsonify
from flasgger import swag_from
from bson import ObjectId, Binary
from datetime import datetime
from connection.database import *

connection = connectdataBase()
collection = connectdataBaseMongo()

def profileRoutes(app):
    @app.route('/uploadProfilePhoto', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'file',
                'description': 'Select profile photo to upload',
                'in': 'formData',
                'required': True,
                'type': 'file'
            },
            {
                'name': 'user_id',
                'description': 'User ID in MySQL to associate with the profile picture',
                'in': 'formData',
                'required': True,
                'type': 'integer'
            }
        ],
        'responses': {
            201: {
                'description': 'Image uploaded successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'file_id': {'type': 'string'}
                    }
                }
            },
            400: {
                'description': 'Upload error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'User not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def uploadImage():
        if 'file' not in request.files:
            return jsonify({'error': 'No file was uploaded'}), 400

        file = request.files['file']
        user_id = request.form.get('user_id') 
        if not user_id:
            return jsonify({'error': 'User ID is required'}), 400

        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'The file must be an image'}), 400

        try:
            with connection.cursor() as cursor:
                cursor.execute("SELECT user_id FROM Users WHERE user_id = %s", (user_id,))
                user_exists = cursor.fetchone() 

                if not user_exists:
                    return jsonify({'error': 'User not found'}), 404  
            file_content = file.read()
            unique_id = str(uuid.uuid4())
            # Guardar imagen en MongoDB
            collection.insert_one({
                'custom_id': unique_id,
                'filename': file.filename,
                'data': Binary(file_content),
                'upload_time': datetime.now(),
                'user_id': user_id 
            })

            with connection.cursor() as cursor:
                cursor.execute(
                    "INSERT INTO ProfilePictures (user_id, mongo_image_id, upload_time) VALUES (%s, %s, %s)",
                    (user_id, unique_id, datetime.now())
                )
                connection.commit()

            return jsonify({
                'message': 'Image uploaded successfully',
                'file_id': unique_id,
            }), 201
        except Exception as e:
            return jsonify({'error': 'Error uploading image', 'details': str(e)}), 500

    @app.route('/checkProfilePicture/<file_id>', methods=['GET'])
    @swag_from({
        'parameters': [
            {
                'name': 'file_id',
                'description': 'ID of the image file',
                'in': 'path',
                'required': True,
                'type': 'string'
            }
        ],
        'responses': {
            200: {
                'description': 'Information retrieved successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'file_id': {'type': 'string'},
                        'filename': {'type': 'string'},
                        'upload_time': {'type': 'string'},
                        'data': {'type': 'string', 'format': 'binary'}
                    }
                }
            },
            404: {
                'description': 'File not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def getImage(file_id):
        try:
            file_data = collection.find_one({'custom_id': file_id})
            if not file_data:
                return jsonify({'error': 'File not found'}), 404

            return jsonify({
                'file_id': file_data['custom_id'],
                'filename': file_data['filename'],
                'upload_time': file_data['upload_time'].strftime('%Y-%m-%d %H:%M:%S'),
                'data': file_data['data'].hex()
            }), 200

        except Exception as e:
            return jsonify({'error': 'Error retrieving image', 'details': str(e)}), 500

    @app.route('/updateProfilePicture/<file_id>', methods=['PUT'])
    @swag_from({
        'parameters': [
            {
                'name': 'file_id',
                'description': 'ID of the image file to update',
                'in': 'path',
                'required': True,
                'type': 'string'
            },
            {
                'name': 'file',
                'description': 'New image file',
                'in': 'formData',
                'required': True,
                'type': 'file'
            },
            {
                'name': 'user_id',
                'description': 'User ID in MySQL to update the profile picture',
                'in': 'formData',
                'required': False,
                'type': 'integer'
            }
        ],
        'responses': {
            200: {
                'description': 'Image updated successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'file_id': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'File not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            400: {
                'description': 'Update error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def updateImage(file_id):
        if 'file' not in request.files:
            return jsonify({'error': 'No file was uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'The file must be an image'}), 400

        try:
            file_content = file.read()
            result = collection.update_one(
                {'custom_id': file_id},
                {'$set': {
                    'filename': file.filename,
                    'data': Binary(file_content)
                }}
            )
            if result.matched_count == 0:
                return jsonify({'error': 'File not found'}), 404

            user_id = request.form.get('user_id')  
            if user_id:
                with connection.cursor() as cursor:
                    cursor.execute("SELECT user_id FROM Users WHERE user_id = %s", (user_id,))
                    user_exists = cursor.fetchone()  

                    if not user_exists:
                        return jsonify({'error': 'User not found'}), 404 

                collection.update_one(
                    {'custom_id': file_id},
                    {'$set': {'user_id': user_id}}  
                )

            return jsonify({
                'message': 'Image updated successfully',
                'file_id': file_id
            }), 200
        except Exception as e:
            return jsonify({'error': 'Error updating image', 'details': str(e)}), 500

    @app.route('/deleteProfilePicture/<file_id>', methods=['DELETE'])
    @swag_from({
        'parameters': [
            {
                'name': 'file_id',
                'description': 'ID of the image file to delete',
                'in': 'path',
                'required': True,
                'type': 'string'
            }
        ],
        'responses': {
            200: {
                'description': 'Image deleted successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'File not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def deleteImageProfile(file_id):
        try:
            result = collection.delete_one({'custom_id': file_id})
            if result.deleted_count == 0:
                return jsonify({'error': 'File not found'}), 404

            with connection.cursor() as cursor:
                cursor.execute("DELETE FROM ProfilePictures WHERE mongo_image_id = %s", (file_id,))
                connection.commit()

            return jsonify({'message': 'Image deleted successfully'}), 200
        except Exception as e:
            return jsonify({'error': 'Error deleting image', 'details': str(e)}), 500
