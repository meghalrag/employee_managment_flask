from flask import Response, request, json
from flask_jwt_extended import jwt_required, get_jwt_claims, get_jwt_identity
from flask_jwt_extended.exceptions import NoAuthorizationError
from flask_restful import Resource
from mongoengine import FieldDoesNotExist, NotUniqueError, DoesNotExist, InvalidQueryError

from errors import NoAuthorizationError, InternalServerError, SchemaValidationError, EmailAlreadyExistsError, \
    DeletingUserError, UpdatingUserError
from models.User import User, UserProfile, UserFileMapping
from common.export_helper import export_to_csv_and_save, export_to_json_and_save, export_to_xlsx_and_save


class User2Api(Resource):
    @jwt_required
    def get(self):
        res = []
        try:
            users = UserProfile.objects().all()
            for each in users:
                temp = {}
                temp["user_id"] = str(each.user.id)
                temp["role"] = each.user.roles[0]
                temp["name"] = each.name
                temp["email"] = each.email
                temp["phone_number"] = each.phone_number
                temp["designation"] = each.designation
                temp["department"] = each.department
                temp["manager"] = each.manager
                temp["hired_date"] = str(each.hired_date)
                res.append(temp)
                del temp
            res = json.dumps(res)
            return Response(res, mimetype='application/json', status=200)
        except NoAuthorizationError:
            return {"error": "No Authorization Error"}, 400
        except Exception:
            return {"error": "Internal Server Error"}, 500

    @jwt_required
    def post(self):
        try:
            body = request.get_json()
            user_schema = {
                "username": body["email"],
                "phone_number": body["phone_number"],
                "password": body["password"]
            }
            user = User(**user_schema)
            user.hash_password()
            user.save()
            del body["password"]
            user_profile = UserProfile(**body)
            user_profile.user = user
            user_profile.save()
            id = user.id
            del user, user_profile
            return {'id': str(id)}, 201
        except FieldDoesNotExist:
            return {"error": "Schema Validation Error"}, 400
        except NotUniqueError:
            return {"error": "Email/Phone Number AlreadyExists Error"}, 400
        except Exception:
            return {"error": "Internal Server Error"}, 500


class UserApi(Resource):
    @jwt_required
    def get(self, id):
        res = []
        try:
            user = User.objects().get(id=id)
            user_prof = UserProfile.objects.get(user=user)
            temp = {}
            temp["user_id"] = str(user_prof.user.id)
            temp["role"] = user_prof.user.roles[0]
            temp["name"] = user_prof.name
            temp["email"] = user_prof.email
            temp["phone_number"] = user_prof.phone_number
            temp["designation"] = user_prof.designation
            temp["department"] = user_prof.department
            temp["manager"] = user_prof.manager
            temp["hired_date"] = str(user_prof.hired_date)
            res = json.dumps(temp)
            return Response(res, mimetype='application/json', status=200)
        except DoesNotExist:
            return {"error": "User DoesNotExist with id"}, 500
        except Exception:
            return {"error": "Internal Server Error"}, 500
        
    @jwt_required
    def delete(self, id):
        try:
            user = User.objects().get(id=id)
            UserProfile.objects.get(user=user).delete()
            user.delete()
            return Response(json.dumps({"message":'Deleted Successfully'}), mimetype='application/json', status=204)
        except DoesNotExist:
            return {"error": "DeletingUserError"}, 400
        except Exception:
            return {"error": "Internal Server Error"}, 500

    @jwt_required
    def put(self, id):
        try:
            user = User.objects.get(id=id)
            body = request.get_json()
            UserProfile.objects.get(user=user).update(**body)
            return Response(json.dumps({"message":'Updated Successfully'}), mimetype='application/json', status=204)
        except SchemaValidationError as err:
            return {"error": "SchemaValidationError"}, 400
        except DoesNotExist:
            return {"error": "UpdatingUserError"}, 400
        except Exception:
            return {"error": "Internal Server Error"}, 500
        

class CheckPermissionAPI(Resource):
    @jwt_required
    def get(self):
        try:
            return Response({"msg": "Permitted"}, status=200)
        except Exception:
            raise InternalServerError
        

class GetCurrentUserAPI(Resource):
    @jwt_required
    def get(self):
        try:
            user_obj = User.objects.get(username=get_jwt_identity())
            res = {}
            res["user_id"] = str(user_obj.id)
            res["email"] = user_obj.username
            res["phone_number"] = user_obj.phone_number
            res["role"] = user_obj.roles
            res = json.dumps(res)
            return Response(res, status=200)
        except Exception:
            return {"error": "Internal Server Error"}, 500
        

class ExportEmpDataAPI(Resource):
    @jwt_required
    def get(self, id, type):
        try:
            user_data = User.objects.get(id=id)
            prof = UserProfile.objects.get(user=user_data) 
            if type == "csv":
                file_id = export_to_csv_and_save(prof)
            elif type == "xlsx":
                file_id = export_to_xlsx_and_save(prof)
            else:
                file_id = export_to_json_and_save(prof)
            UserFileMapping(user=user_data, file_id=str(file_id)).save()
            return {"message": "Data Exported Successfully"}, 200
        except Exception as err:
            return {"error": "Internal Server Error"}, 500
