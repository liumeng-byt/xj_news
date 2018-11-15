from flask import Blueprint
profile_blu = Blueprint("user",__name__,url_prefix="/user")


from . import views