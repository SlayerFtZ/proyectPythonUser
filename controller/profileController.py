import io
from flask import request, jsonify, send_file
from flasgger import swag_from
from bson import ObjectId, Binary
from datetime import datetime
from connection.database import *

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
            }
        }
    })
    def uploadImage():
        if 'file' not in request.files:
            return jsonify({'error': 'No file was uploaded'}), 400

        file = request.files['file']
        if file.filename == '':
            return jsonify({'error': 'No file selected'}), 400

        # File type validation
        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'The file must be an image'}), 400

        try:
            file_content = file.read()
            file_id = collection.insert_one({
                'filename': file.filename,
                'data': Binary(file_content),
                'upload_time': datetime.now()  # Adding upload time
            }).inserted_id

            return jsonify({
                'message': 'Image uploaded successfully',
                'file_id': str(file_id),
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
            file_data = collection.find_one({'_id': ObjectId(file_id)})
            if not file_data:
                return jsonify({'error': 'File not found'}), 404

            return jsonify({
                'file_id': str(file_data['_id']),
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

        # File type validation
        if not file.content_type.startswith('image/'):
            return jsonify({'error': 'The file must be an image'}), 400

        try:
            file_content = file.read()
            result = collection.update_one(
                {'_id': ObjectId(file_id)},
                {'$set': {
                    'filename': file.filename,
                    'data': Binary(file_content)
                }}
            )
            if result.matched_count == 0:
                return jsonify({'error': 'File not found'}), 404

            return jsonify({
                'message': 'Image updated successfully',
                'file_id': str(file_id)
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
            204: {
                'description': 'Image deleted successfully'
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
            result = collection.delete_one({'_id': ObjectId(file_id)})
            if result.deleted_count == 0:
                return jsonify({'error': 'File not found'}), 404
            
            return '', 204 
        except Exception as e:
            return jsonify({'error': 'Error deleting image', 'details': str(e)}), 500
