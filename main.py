from flask import Flask, jsonify, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap5

app = Flask(__name__)

# Connect to Database
app.config['DEBUG'] = True
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///cafes.db'
db = SQLAlchemy()
db.init_app(app)
Bootstrap5(app)


# Cafe TABLE Configuration
class Cafe(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(250), unique=True, nullable=False)
    map_url = db.Column(db.String(500), nullable=False)
    img_url = db.Column(db.String(500), nullable=False)
    location = db.Column(db.String(250), nullable=False)
    seats = db.Column(db.String(250), nullable=False)
    has_toilet = db.Column(db.Boolean, nullable=False)
    has_wifi = db.Column(db.Boolean, nullable=False)
    has_sockets = db.Column(db.Boolean, nullable=False)
    can_take_calls = db.Column(db.Boolean, nullable=False)
    coffee_price = db.Column(db.String(250), nullable=True)

    def to_dict(self):
        return {column.name: getattr(self, column.name) for column in self.__table__.columns}


with app.app_context():
    db.create_all()

# Home
@app.route("/")
def home():
    result = db.session.execute(db.select(Cafe))
    cafes = result.scalars().all()
    return render_template("index.html", cafes=cafes)


# Search for Cafe available in location
@app.route("/search", methods=["GET", "POST"])
def get_cafe_at_location():
    if request.method == "POST":
        query_location = request.form.get("loc")
        result = db.session.execute(db.select(Cafe).where(Cafe.location == query_location))
        all_cafes = result.scalars().all()
        if all_cafes:
            return render_template('search.html', cafes=all_cafes)
        else:
            return jsonify(error={"Not Found": "Sorry, we don't have a cafe at that location"}), 404

# Show cafe information
@app.route("/cafe", methods=["GET", "POST"])
def show_cafe():
    cafe_id = request.args.get("id")
    requested_cafe = db.get_or_404(Cafe, cafe_id)
    return render_template("cafe.html", cafe=requested_cafe)

# Add new Cafe information
@app.route("/add", methods=["GET", "POST"])
def post_new_cafe():
    if request.method == "POST":
        new_cafe = Cafe(
            name=request.form["name"],
            map_url=request.form["map_url"],
            img_url=request.form["img_url"],
            location=request.form["location"],
            has_sockets=bool(request.form["has_sockets"]),
            has_toilet=bool(request.form["has_toilet"]),
            has_wifi=bool(request.form["has_wifi"]),
            can_take_calls=bool(request.form["can_take_calls"]),
            seats=request.form["seats"],
            coffee_price=request.form["coffee_price"]
        )
        db.session.add(new_cafe)
        db.session.commit()
        return redirect(url_for('home'))
    return render_template('add.html', response={"success": "Successfully added the new cafe."})

# Update existing Cafe information
@app.route("/update", methods=["GET", "POST"])
def patch_new_price():
    if request.method == "POST":
        cafe_id = request.form.get("id")
        cafe = db.get_or_404(Cafe, cafe_id)
        new_price = request.form['new_price']

        cafe.coffee_price = f"£{new_price}"
        db.session.commit()

        return redirect(url_for('home'))
    cafe_id = request.args.get("id")
    cafe = db.get_or_404(Cafe, cafe_id)
    return render_template('update.html', cafe=cafe)

# Remove Cafe that no longer operate
@app.route("/delete")
def delete_cafe():
    cafe_id = request.args.get("id")
    cafe = db.get_or_404(Cafe, cafe_id)

    db.session.delete(cafe)
    db.session.commit()
    return redirect(url_for('home'))

if __name__ == '__main__':
    app.run(debug=True)
