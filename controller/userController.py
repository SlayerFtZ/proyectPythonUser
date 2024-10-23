import os
import re
import secrets
from flask import  request, jsonify
from flask_mail import Mail, Message
from werkzeug.security import generate_password_hash
from werkzeug.security import check_password_hash
from datetime import datetime, timezone, timedelta
from flasgger import swag_from
from services.webScrap import *
from connection.database import *
from services.openAI import *
from services.emailResourse import *
from model.user import *
from services.facialRecognitionService import *
from services.fireBaseServices import *
from services.extractINEData import *


def registerRoutes(app):
    mail = Mail(app)
    @app.route('/login', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'body',
                'description': 'User login credentials',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string', 'format': 'email'},
                        'password': {'type': 'string'}
                    },
                    'required': ['email', 'password']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Login successful',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'user_id': {'type': 'integer'}
                    }
                }
            },
            400: {
                'description': 'Login failed - Invalid email or password',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def loginUser():
        connection = None
        cursor = None
        try:
            data = request.json
            email = data.get('email')
            password = data.get('password')

            if not email or not password:
                return jsonify({'error': 'Email and password are required'}), 400

            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_pattern, email):
                return jsonify({'error': 'Invalid email format'}), 400

            connection = connectdataBase()
            if connection is None:
                return jsonify({'error': 'Database connection error'}), 500

            cursor = connection.cursor()

            cursor.execute("SELECT password, user_id FROM User WHERE email = %s LIMIT 1", (email,))
            user = cursor.fetchone()

            if user is None:
                return jsonify({'error': 'Email not found'}), 400

            stored_password = user[0]
            user_id = user[1]

            if not check_password_hash(stored_password, password):
                return jsonify({'error': 'Incorrect password'}), 400

            return jsonify({'message': 'Login successful', 'user_id': user_id}), 200

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'Login error'}), 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    @app.route('/User', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'body',
                'description': 'New user data',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'first_name': {'type': 'string'},
                        'last_name_father': {'type': 'string'},
                        'last_name_mother': {'type': 'string'},
                        'birth_date': {'type': 'string', 'format': 'date'},
                        'phone_number': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                        'password': {'type': 'string'},
                        'license': {'type': 'string'}
                    },
                    'required': ['first_name', 'last_name_father', 'last_name_mother', 'birth_date', 'phone_number', 'email', 'password']
                }
            },
        ],
        'responses': {
            201: {
                'description': 'User registered successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'},
                        'user_id': {'type': 'integer'}
                    }
                }
            },
            400: {
                'description': 'Registration error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def registerUser():
        connection = None
        cursor = None
        try:
            data = request.json
            user = User.from_dict(data)

            required_fields = ['first_name', 'last_name_father', 'last_name_mother', 'birth_date', 'phone_number', 'email', 'password']
            for field in required_fields:
                if not getattr(user, field):
                    return jsonify({'error': f'Missing field: {field}'}), 400

            # Validación de formato de email
            email_pattern = r'^[\w\.-]+@[\w\.-]+\.\w+$'
            if not re.match(email_pattern, user.email):
                return jsonify({'error': 'Invalid email format'}), 400

            connection = connectdataBase()
            if connection is None:
                return jsonify({'error': 'Database connection error'}), 500

            cursor = connection.cursor()

            cursor.execute("SELECT 1 FROM User WHERE email = %s LIMIT 1", (user.email,))
            existing_email = cursor.fetchone()

            if existing_email:
                return jsonify({'error': 'Email is already in use'}), 400

            user_id = None
            # Se usa la URL de imagen por defecto en caso de no proporcionar una
            profile_picture_url = user.profilePictureUrl

            if user.license:
                driver = startDriver()
                try:
                    navigatePage(driver)
                    filloutForm(driver, user)
                    defClickConsult(driver)
                    results = extractResults(driver, user.license)

                    if selectRowById(driver, user.license):
                        detail_data = extractDataDetails(driver)

                        profession = detail_data.get("Profesión", "Not available")

                        cursor.execute("SELECT 1 FROM ChefLicense WHERE license = %s LIMIT 1", (detail_data.get("Cédula", "Not available"),))
                        existing_cedula = cursor.fetchone()

                        if existing_cedula:
                            return jsonify({'error': 'User with this ID already exists'}), 400

                        if not checkTheContextOfTheProfession(profession):
                            return jsonify({'error': 'The career is not related to gastronomy'}), 400

                        cursor.execute("SELECT profession_id FROM Profession WHERE profession = %s LIMIT 1", (profession,))
                        profession_in_career = cursor.fetchone()

                        if profession_in_career is None:
                            cursor.execute("INSERT INTO Profession (profession) VALUES (%s)", (profession,))
                            connection.commit()

                        cursor.execute("SELECT profession_id FROM Profession WHERE profession = %s LIMIT 1", (profession,))
                        profession_id = cursor.fetchone()[0]

                        sql_user = """
                        INSERT INTO User (first_name, last_name_father, last_name_mother, birth_date, phone_number, email, password)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        user_values = (user.first_name, user.last_name_father, user.last_name_mother, user.birth_date, user.phone_number, user.email, generate_password_hash(user.password))
                        cursor.execute(sql_user, user_values)
                        connection.commit()
                        user_id = cursor.lastrowid

                        sql_chef_license = """
                        INSERT INTO ChefLicense (user_id, profession_id, license, gender, profession, year_of_issue, institution)
                        VALUES (%s, %s, %s, %s, %s, %s, %s)
                        """
                        chef_license_values = (user_id, profession_id, detail_data.get("Cédula"), detail_data.get("Género"), profession, detail_data.get("Año de expedición"), detail_data.get("Institución"))

                        cursor.execute(sql_chef_license, chef_license_values)
                        connection.commit()
                    else:
                        return jsonify({'error': 'Could not select ID'}), 400
                except Exception as e:
                    if user_id is not None:
                        cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
                        connection.commit()
                    return jsonify({'error': 'Web scraping error: ' + str(e)}), 400
                finally:
                    closedriver(driver)
            else:
                # Insertar usuario sin licencia
                sql_user = """
                INSERT INTO User (first_name, last_name_father, last_name_mother, birth_date, phone_number, email, password)
                VALUES (%s, %s, %s, %s, %s, %s, %s)
                """
                user_values = (user.first_name, user.last_name_father, user.last_name_mother, user.birth_date, user.phone_number, user.email, generate_password_hash(user.password))
                cursor.execute(sql_user, user_values)
                connection.commit()
                user_id = cursor.lastrowid

            # Inserta la imagen de perfil en la tabla ProfilePicture
            sql_profile_picture = """
            INSERT INTO ProfilePicture (user_id, image_url, upload_time)
            VALUES (%s, %s, NOW())
            """
            cursor.execute(sql_profile_picture, (user_id, profile_picture_url))
            connection.commit()

            return jsonify({'message': 'User registered successfully', 'user_id': user_id}), 201

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'Registration error'}), 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()



    @app.route('/User/<string:license>', methods=['GET'])
    @swag_from({
        'parameters': [
            {
                'name': 'license',
                'description': 'License number of the user to be queried',
                'in': 'path',
                'required': True,
                'type': 'string'
            }
        ],
        'responses': {
            200: {
                'description': 'User data retrieved successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'first_name': {'type': 'string'},
                        'last_name_father': {'type': 'string'},
                        'last_name_mother': {'type': 'string'},
                        'birth_date': {'type': 'string', 'format': 'date'},
                        'phone_number': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                        'license': {'type': 'string'},
                        'profession': {'type': 'string'},
                        'year_of_issue': {'type': 'string'},
                        'institution': {'type': 'string'},
                        'gender': {'type': 'string'}
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
            },
            400: {
                'description': 'Invalid license format',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def getUserByLicense(license):
        
        if not license.isdigit():
            return jsonify({'error': 'License format is invalid, only numbers are allowed'}), 400

        connection = None
        cursor = None
        try:
            connection = connectdataBase()
            if connection is None:
                return jsonify({'error': 'Database connection error'}), 500

            cursor = connection.cursor()

            sql_query = """
            SELECT u.first_name, u.last_name_father, u.last_name_mother,
                u.birth_date, u.phone_number, u.email, cl.license,
                p.profession, cl.year_of_issue, cl.institution, cl.gender
            FROM User u
            JOIN ChefLicense cl ON u.user_id = cl.user_id
            JOIN Profession p ON cl.profession_id = p.profession_id
            WHERE cl.license = %s
            """
            cursor.execute(sql_query, (license,))
            user_data = cursor.fetchone()

            if user_data is None:
                return jsonify({'error': 'User not found'}), 404

            result = {
                'first_name': user_data[0],
                'last_name_father': user_data[1],
                'last_name_mother': user_data[2],
                'birth_date': user_data[3],
                'phone_number': user_data[4],
                'email': user_data[5],
                'license': user_data[6],
                'profession': user_data[7],
                'year_of_issue': user_data[8],
                'institution': user_data[9],
                'gender': user_data[10]
            }

            return jsonify(result), 200

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'Server error'}), 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    @app.route('/User/email/<string:email>', methods=['GET'])
    @swag_from({
        'parameters': [
            {
                'name': 'email',
                'description': 'Email of the user to be queried',
                'in': 'path',
                'required': True,
                'type': 'string'
            }
        ],
        'responses': {
            200: {
                'description': 'User data retrieved successfully',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'first_name': {'type': 'string'},
                        'last_name_father': {'type': 'string'},
                        'last_name_mother': {'type': 'string'},
                        'birth_date': {'type': 'string', 'format': 'date'},
                        'phone_number': {'type': 'string'},
                        'email': {'type': 'string', 'format': 'email'},
                        'license': {'type': 'string'},
                        'profession': {'type': 'string'},
                        'year_of_issue': {'type': 'string'},
                        'institution': {'type': 'string'},
                        'gender': {'type': 'string'}
                    }
                }
            },
            400: {
                'description': 'Invalid email format',
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
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def getUserByEmail(email):
        email_regex = r'^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$'
        if not re.match(email_regex, email):
            return jsonify({'error': 'Invalid email format'}), 400

        connection = None
        cursor = None
        try:
            connection = connectdataBase()
            if connection is None:
                return jsonify({'error': 'Database connection error'}), 500

            cursor = connection.cursor()

            sql_query = """
            SELECT u.first_name, u.last_name_father, u.last_name_mother,
                u.birth_date, u.phone_number, u.email, cl.license,
                p.profession, cl.year_of_issue, cl.institution, cl.gender
            FROM User u
            LEFT JOIN ChefLicense cl ON u.user_id = cl.user_id
            LEFT JOIN Profession p ON cl.profession_id = p.profession_id
            WHERE u.email = %s
            """
            cursor.execute(sql_query, (email,))
            user_data = cursor.fetchone()

            if user_data is None:
                return jsonify({'error': 'User not found'}), 404

            result = {
                'first_name': user_data[0],
                'last_name_father': user_data[1],
                'last_name_mother': user_data[2],
                'birth_date': user_data[3],
                'phone_number': user_data[4],
                'email': user_data[5],
                'license': user_data[6],
                'profession': user_data[7],
                'year_of_issue': user_data[8],
                'institution': user_data[9],
                'gender': user_data[10]
            }

            return jsonify(result), 200

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'Server error'}), 500
        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()
                
    @app.route('/User/search', methods=['GET'])
    @swag_from({
        'parameters': [
            {
                'name': 'first_name',
                'description': 'First name of the User to be queried',
                'in': 'query',
                'required': True,
                'type': 'string'
            },
            {
                'name': 'last_name_father',
                'description': 'Father\'s last name of the User to be queried',
                'in': 'query',
                'required': True,
                'type': 'string'
            },
            {
                'name': 'last_name_mother',
                'description': 'Mother\'s last name of the User to be queried',
                'in': 'query',
                'required': True,
                'type': 'string'
            }
        ],
        'responses': {
            200: {
                'description': 'User data retrieved successfully',
                'schema': {
                    'type': 'array',
                    'items': {
                        'type': 'object',
                        'properties': {
                            'first_name': {'type': 'string'},
                            'last_name_father': {'type': 'string'},
                            'last_name_mother': {'type': 'string'},
                            'birth_date': {'type': 'string', 'format': 'date'},
                            'phone_number': {'type': 'string'},
                            'email': {'type': 'string', 'format': 'email'},
                            'license': {'type': 'string'},
                            'profession': {'type': 'string'},
                            'year_of_issue': {'type': 'string'},
                            'institution': {'type': 'string'},
                            'gender': {'type': 'string'}
                        }
                    }
                }
            },
            404: {
                'description': 'No User found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def getUserByNames():
        first_name = request.args.get('first_name')
        last_name_father = request.args.get('last_name_father')
        last_name_mother = request.args.get('last_name_mother')

        connection = None
        cursor = None
        try:
            connection = connectdataBase()
            if connection is None:
                return jsonify({'error': 'Database connection error'}), 500

            cursor = connection.cursor()

            sql_query = """
            SELECT u.first_name, u.last_name_father, u.last_name_mother,
                u.birth_date, u.phone_number, u.email, cl.license,
                p.profession, cl.year_of_issue, cl.institution, cl.gender
            FROM User u
            LEFT JOIN ChefLicense cl ON u.user_id = cl.user_id
            LEFT JOIN Profession p ON cl.profession_id = p.profession_id
            WHERE u.first_name = %s AND u.last_name_father = %s AND u.last_name_mother = %s
            """
            cursor.execute(sql_query, (first_name, last_name_father, last_name_mother))
            
            User_data = cursor.fetchall()

            if not User_data:
                return jsonify({'error': 'No User found'}), 404

            result = []
            for user_data in User_data:
                result.append({
                    'first_name': user_data[0],
                    'last_name_father': user_data[1],
                    'last_name_mother': user_data[2],
                    'birth_date': user_data[3],
                    'phone_number': user_data[4],
                    'email': user_data[5],
                    'license': user_data[6],
                    'profession': user_data[7],
                    'year_of_issue': user_data[8],
                    'institution': user_data[9],
                    'gender': user_data[10]
                })

            return jsonify(result), 200

        except Exception as e:
            print(f"An error occurred: {e}")
            return jsonify({'error': 'Server error'}), 500
        finally:
            if cursor:
                try:
                    cursor.close()
                except Exception as e:
                    print(f"Error closing cursor: {e}")
            if connection:
                try:
                    connection.close()
                except Exception as e:
                    print(f"Error closing connection: {e}")

    @app.route('/deleteUserProfessionalLicense/<license>', methods=['DELETE'])
    @swag_from({
        'parameters': [
            {
                'name': 'license',
                'description': 'Professional license to delete',
                'in': 'path',
                'type': 'string',
                'required': True
            }
        ],
        'responses': {
            200: {
                'description': 'License and associated user successfully deleted',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'License not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def deleteProfessionalLicense(license):
        connection = None
        cursor = None
        try:
            connection = connectdataBase()
            cursor = connection.cursor()

            # Obtener user_id de la licencia
            cursor.execute("""
                SELECT cl.user_id 
                FROM ChefLicense cl
                WHERE cl.license = %s
            """, (license,))
            result = cursor.fetchone()

            if result:
                user_id = result[0]

                # Eliminar registros en la base de datos SQL
                cursor.execute("DELETE FROM ChefLicense WHERE license = %s", (license,))
                cursor.execute("DELETE FROM ProfilePicture WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM User WHERE user_id = %s", (user_id,))
                connection.commit()

                return jsonify({'message': 'License and associated user successfully deleted'}), 200
            else:
                return jsonify({'error': 'License not found'}), 404

        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': 'Server error'}), 500

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    @app.route('/deleteUser', methods=['DELETE'])
    @swag_from({
        'parameters': [
            {
                'name': 'body',
                'description': 'User email to delete',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string', 'format': 'email'}
                    },
                    'required': ['email']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'User successfully deleted',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
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
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'error': {'type': 'string'}
                    }
                }
            }
        }
    })
    def deleteUser():
        connection = None
        cursor = None
        try:
            data = request.json
            email = data.get('email')

            if not email:
                return jsonify({'error': 'Email is required'}), 400

            connection = connectdataBase()
            cursor = connection.cursor()

            cursor.execute("""
                SELECT u.user_id 
                FROM User u
                WHERE u.email = %s
            """, (email,))
            user = cursor.fetchone()

            if user:
                user_id = user[0]

                cursor.execute("DELETE FROM ProfilePicture WHERE user_id = %s", (user_id,))
                cursor.execute("DELETE FROM User WHERE email = %s", (email,))
                connection.commit()

                return jsonify({'message': 'User and associated profile pictures successfully deleted'}), 200
            else:
                return jsonify({'error': 'User not found'}), 404

        except Exception as e:
            print(f"Error: {str(e)}")
            return jsonify({'error': 'Server error'}), 500

        finally:
            if cursor:
                cursor.close()
            if connection:
                connection.close()


    @app.route('/resetPassword', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'body',
                'description': 'Email to reset the password',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'email': {'type': 'string', 'format': 'email'}
                    },
                    'required': ['email']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Email sent',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            404: {
                'description': 'Email not found',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
    def resetPassword():
        email = request.json.get('email')
        token, expiration = generateToken()

        connection = connectdataBase()
        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM User WHERE email = %s", (email,))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            cursor.execute("INSERT INTO Token (user_id, reset_token, token_expiration) VALUES (%s, %s, %s) "
                        "ON DUPLICATE KEY UPDATE reset_token = %s, token_expiration = %s", 
                        (user_id, token, expiration, token, expiration))
            connection.commit()
            cursor.close()
            connection.close()

            msg = Message('Password Recovery', sender='your_email@gmail.com', recipients=[email])
            msg.body = f'Use this token to reset your password: {token}'

            try:
                mail.send(msg)
            except Exception as e:
                return jsonify({"message": "Error sending email"}), 500
            
            return jsonify({"message": "Email sent"}), 200
        else:
            cursor.close()
            connection.close()
            return jsonify({"message": "Email not found"}), 404


    @app.route('/recoverPasswordToken/<token>', methods=['POST'])
    @swag_from({
        'parameters': [
            {
                'name': 'token',
                'description': 'Token to reset the password',
                'in': 'path',
                'required': True,
                'type': 'string'
            },
            {
                'name': 'body',
                'description': 'New password',
                'in': 'body',
                'required': True,
                'schema': {
                    'type': 'object',
                    'properties': {
                        'new_password': {'type': 'string'}
                    },
                    'required': ['new_password']
                }
            }
        ],
        'responses': {
            200: {
                'description': 'Password updated',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            400: {
                'description': 'Invalid or expired token',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            },
            500: {
                'description': 'Server error',
                'schema': {
                    'type': 'object',
                    'properties': {
                        'message': {'type': 'string'}
                    }
                }
            }
        }
    })
    def recoverPasswordToken(token):
        new_password = request.json.get('new_password')

        connection = connectdataBase()
        cursor = connection.cursor()

        cursor.execute("SELECT user_id FROM Token WHERE reset_token = %s AND token_expiration > %s", 
                        (token, datetime.now(timezone.utc)))
        user = cursor.fetchone()

        if user:
            user_id = user[0]
            hashed_password = generate_password_hash(new_password)

            cursor.execute("UPDATE User SET password = %s WHERE user_id = %s", (hashed_password, user_id))
            cursor.execute("DELETE FROM Token WHERE user_id = %s", (user_id,))
            connection.commit()
            cursor.close()
            connection.close()
            return jsonify({"message": "Password updated"}), 200
        else:
            cursor.close()
            connection.close()
            return jsonify({"message": "Invalid or expired token"}), 400