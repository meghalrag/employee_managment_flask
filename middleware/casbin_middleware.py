import casbin
# from functools import wraps
from flask import jsonify, abort
from flask_http_middleware import BaseHTTPMiddleware
from flask_jwt_extended import get_jwt_claims, jwt_required
from casbin_pymongo_adapter import Adapter

# casbin_enforcer = casbin.Enforcer("casbin/model.conf", "casbin/rbac_policy.csv")

adapter = Adapter('mongodb://localhost:27017/', "employee_management")
casbin_enforcer = casbin.Enforcer("casbin/model.conf", adapter)

#set policies at first time
if not casbin_enforcer.get_policy():
    rules = [
        ["manager", "*", "*"],
        ["employee", "*", "GET"]
    ]
    casbin_enforcer.add_policies(rules)
    casbin_enforcer.save_policy()

class CasbinMiddleware(BaseHTTPMiddleware):
    def __init__(self):
        super().__init__()

    def dispatch(self, request, call_next):
        uri = str(request.path)
        IGNORE_LIST = [
            "docs",
            "login",
            "register"
        ]
        uri_segments = uri.split("/")
        uri_segments = list(filter(lambda x: x != "", uri_segments))
        if uri_segments[-1] in IGNORE_LIST or uri_segments[-2] in ["docs", "static"]:
            return call_next(request)
        else:
            try:
                return self.authorize(request, uri, call_next)
            except PermissionError:
                return abort(403, "You dont have permission to do this")
        

    @jwt_required
    def authorize(self, request, uri, call_next):
        try:
            print("middleware invoked successs=============================")
            for role in get_jwt_claims()['roles']:
                if casbin_enforcer.enforce(role, uri, request.method):
                    return call_next(request)
            else:
                # user = g.current_user['username']
                raise PermissionError
        except PermissionError:
            raise PermissionError
        except Exception as err:
            print(f"ERROR in CasbinMiddleware====={err}")
            return call_next(request)