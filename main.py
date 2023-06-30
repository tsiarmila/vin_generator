from flask import Flask, render_template, request, jsonify, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from flask_bootstrap import Bootstrap

app = Flask(__name__)
app.secret_key = 'K705k705'
app.app_context().push()
app.config['SQLALCHEMY_DATABASE_URI'] = 'sqlite:///vins.db'
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db = SQLAlchemy(app)
bootstrap = Bootstrap(app)

# Available options for equipment code
EQUIPMENT_OPTIONS = {
    '': '',
    '000': '000 - Base platform',
    '014': '014 - Bumper',
    '037': '037 - Drum Mulcher',
    '036': '036 - Side Trimmer',
    '038': '038 - Sprayer',
    '027': '027 - Lawn Mower'
}

# Available options for place of production
PLACE_OPTIONS = {
    '': '',
    '00': '00 - Slovenia',
    '01': '01 - Turkey'
}


class Vin(db.Model):
    id = db.Column(db.Integer, primary_key=True)
    version = db.Column(db.String(3), nullable=False)
    equipment = db.Column(db.String(3), nullable=False)
    year = db.Column(db.Integer(), nullable=False)
    serial_number = db.Column(db.Integer(), nullable=False)
    place = db.Column(db.String(2), nullable=False)


db.create_all()


@app.route('/', methods=['GET', 'POST'])
def vin_generator():
    if request.method == 'POST':
        version = request.form['version']
        equipment = request.form['equipment']
        year = int(request.form['year'])
        place = request.form['place']
        serial_number = request.form['serialNumber']

        # Generate the VIN
        vin = f'{version}{equipment}{year:02d}{serial_number}{place}'

        return render_template('index.html', vin=vin, equipment_options=EQUIPMENT_OPTIONS, place_options=PLACE_OPTIONS)

    return render_template('index.html', equipment_options=EQUIPMENT_OPTIONS, place_options=PLACE_OPTIONS)


@app.route('/search', methods=['POST'])
def search_serial_number():
    data = request.get_json()
    version = data['version']
    equipment = data['equipment']
    year = data['year']
    place = data['place']

    serial_number = 1000000

    while db.session.query(Vin).filter_by(version=f"{version}", equipment=f"{equipment}", year=year, serial_number=serial_number, place=f"{place}").scalar() is not None:

        serial_number += 1
        print(serial_number)

    return jsonify({'serialNumber': serial_number})


@app.route("/add", methods=["GET", "POST"])
def add():
    vin = request.get_json()['vin']
    # Extract information from the VIN
    version = vin[:3]
    equipment = vin[3:6]
    year = int(vin[6:8])
    serial_number = vin[8:15]
    place = vin[-2:]

    # Create a new Vin object
    new_vin = Vin(
        version=f"{version}",
        equipment=f"{equipment}",
        year=year,
        serial_number=serial_number,
        place=f"{place}"
    )

    try:
        # Add the new VIN to the database
        db.session.add(new_vin)
        db.session.commit()

        return jsonify({'message': 'VIN number added successfully'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500


@app.route('/vins')
def vins():
    all_vins = db.session.query(Vin).all()
    db.session.commit()

    return render_template('vins.html', all_vins=all_vins)


@app.route('/delete', methods=["GET", "POST"])
def delete():
    if request.method == 'POST':
        vin_id = request.form["id"]
        vin_to_delete = Vin.query.filter_by(id=vin_id).first()

        if vin_to_delete:
            db.session.delete(vin_to_delete)
            db.session.commit()
            return redirect(url_for('vins', success='VIN deleted successfully.'))
        else:
            return redirect(url_for('vins', error='VIN not found.'))

    vin_id = request.args.get('id')
    vin_to_delete = Vin.query.get(vin_id)
    vin_selected = f'{vin_to_delete.version}{vin_to_delete.equipment}{vin_to_delete.year}{vin_to_delete.serial_number}{vin_to_delete.place}'

    return render_template('delete.html', vin=vin_selected, vin_to_delete=vin_to_delete)


if __name__ == '__main__':
    app.run(debug=True)
