# Import from application modules
from routes.Login import LoginApi
from routes.User import User2Api, UserApi, CheckPermissionAPI, GetCurrentUserAPI, ExportEmpDataAPI


# Function to initialize route to API Flask
def initialize_routes(api):
    api.add_resource(LoginApi, '/api/login')
    api.add_resource(User2Api, '/api/user')
    api.add_resource(UserApi, '/api/user/<id>')
    api.add_resource(CheckPermissionAPI, '/api/check_permission')
    api.add_resource(GetCurrentUserAPI, '/api/user/me')
    api.add_resource(ExportEmpDataAPI, '/api/user/export/<id>/<type>')
