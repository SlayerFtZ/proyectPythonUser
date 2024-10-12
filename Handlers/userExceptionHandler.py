from flask import jsonify

class ExceptionHandler:

    @staticmethod
    def handle_not_found(e):
        return jsonify({'error': 'Resource not found'}), 404

    @staticmethod
    def handle_bad_request(e):
        return jsonify({'error': 'Bad request: ' + str(e)}), 400

    @staticmethod
    def handle_internal_server_error(e):
        return jsonify({'error': 'Internal server error'}), 500

    @staticmethod
    def handle_validation_error(e):
        return jsonify({'error': 'Validation error: ' + str(e)}), 400

    @staticmethod
    def handle_type_error(e):
        return jsonify({'error': 'Type mismatch error: ' + str(e)}), 400
