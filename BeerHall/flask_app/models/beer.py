from flask_app import app
from flask_app.config.mysqlconnection import connectToMySQL
from flask import flash
from flask_bcrypt import Bcrypt
from flask_app.models import user
import re

DB = "beers"

class Beer:
    
    def __init__(self, beer):
        self.id = beer["id"]
        self.name = beer["name"]
        self.style = beer["style"]
        self.brewery = beer["brewery"]
        self.description = beer["description"]
        self.photo = beer["photo"]
        self.created_at = beer["created_at"]
        self.updated_at = beer["updated_at"]
        self.user = None

    @classmethod
    def create_valid_beer(cls, beer_dict):
        if not cls.is_valid(beer_dict):
            return None
        
        query = """INSERT INTO beers (name, style, brewery, description, photo, user_id) VALUES (%(name)s, %(style)s, %(brewery)s, %(description)s, %(photo)s, %(user_id)s);"""
        beer_id = connectToMySQL(DB).query_db(query, beer_dict)
        beer = cls.get_by_id(beer_id)

        return beer

    @classmethod
    def get_by_id(cls, beer_id):
        print(f"get beer by id {beer_id}")
        data = {"id": beer_id}
        query = """SELECT beers.id, beers.created_at, beers.updated_at, name, style, brewery, description, photo,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM beers
                    JOIN users on users.id = beers.user_id
                    WHERE beers.id = %(id)s;"""
        
        result = connectToMySQL(DB).query_db(query,data)
        print("result of query:")
        print(result)
        result = result[0]
        beer = cls(result)
        
        beer.user = user.User(
                {
                    "id": result["user_id"],
                    "first_name": result["first_name"],
                    "last_name": result["last_name"],
                    "email": result["email"],
                    "password": result["password"],
                    "created_at": result["uc"],
                    "updated_at": result["uu"]
                }
            )

        return beer

    @classmethod
    def delete_beer_by_id(cls, beer_id):

        data = {"id": beer_id}
        query = "DELETE from beers WHERE id = %(id)s;"
        connectToMySQL(DB).query_db(query,data)

        return beer_id


    @classmethod
    def update_beer(cls, beer_dict, session_id):

        beer = cls.get_by_id(beer_dict["id"])
        if beer.user.id != session_id:
            flash("You must be the creator to update this beer.")
            return False

        if not cls.is_valid(beer_dict):
            return False
        
        query = """UPDATE beers
                    SET name = %(name)s, style = %(style)s, brewery = %(brewery)s, description = %(description)s
                    WHERE id = %(id)s;"""
        result = connectToMySQL(DB).query_db(query,beer_dict)
        beer = cls.get_by_id(beer_dict["id"])
        
        return beer

    @classmethod
    def get_all(cls):
        query = """SELECT beers.id, beers.created_at, beers.updated_at, name, style, brewery, description, photo,
                    users.id as user_id, first_name, last_name, email, password, users.created_at as uc, users.updated_at as uu
                    FROM beers
                    JOIN users on users.id = beers.user_id;"""
        beer_data = connectToMySQL(DB).query_db(query)

        beers = []

        for beer in beer_data:

            beer_obj = cls(beer)

            beer_obj.user = user.User(
                {
                    "id": beer["user_id"],
                    "first_name": beer["first_name"],
                    "last_name": beer["last_name"],
                    "email": beer["email"],
                    "password": beer["password"],
                    "created_at": beer["uc"],
                    "updated_at": beer["uu"]
                }
            )
            beers.append(beer_obj)


        return beers

    @staticmethod
    def is_valid(beer_dict):
        valid = True
        flash_string = " field is required and must be at least 3 characters."
        if len(beer_dict["name"]) < 3:
            flash("Name " + flash_string)
            valid = False
        if len(beer_dict["description"]) < 3:
            flash("Descriptions " + flash_string)
            valid = False
        return valid