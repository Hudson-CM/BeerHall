from flask import Flask, render_template, session, redirect, request
from flask_app import app
from flask_app.models.user import User
from flask_app.models.beer import Beer
from flask import flash


@app.route("/beers/home")
def beers_home():
    if "user_id" not in session:
        flash("You must be logged in to access the dashboard.")
        return redirect("/")
    
    user = User.get_by_id(session["user_id"])
    beers = Beer.get_all()

    return render_template("home.html", user=user, beers=beers)

@app.route("/beers/<int:beer_id>")
def beer_detail(beer_id):
    user = User.get_by_id(session["user_id"])
    beer = Beer.get_by_id(beer_id)
    return render_template("beer_detail.html", user=user, beer=beer)

@app.route("/beers/create")
def beer_create_page():
    return render_template("create_beer.html")

@app.route("/beers/edit/<int:beer_id>")
def beer_edit_page(beer_id):
    beer = Beer.get_by_id(beer_id)
    return render_template("edit_beer.html", beer=beer)


@app.route("/beers", methods=["POST"])
def create_beer():
    valid_beer = Beer.create_valid_beer(request.form)
    if valid_beer:
        return redirect(f'/beers/{valid_beer.id}')
    return redirect('/beers/create')

@app.route("/beers/<int:beer_id>", methods=["POST"])
def update_beer(beer_id):

    valid_beer = Beer.update_beer(request.form, session["user_id"])

    if not valid_beer:
        return redirect(f"/beers/edit/{beer_id}")
        
    return redirect(f"/beers/{beer_id}")

@app.route("/beers/delete/<int:beer_id>")
def delete_by_id(beer_id):
    Beer.delete_beer_by_id(beer_id)
    return redirect("/beers/home")