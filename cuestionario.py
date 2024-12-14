from flask import Flask, render_template, request, url_for
import qrcode
import io
import base64
from flask import send_file

app = Flask(__name__)

@app.route('/', methods=['GET', 'POST'])
def questionnaire():
    if request.method == 'POST':
        data = {
            'health_card_number': request.form.get('health_card_number'),
            'full_name': request.form.get('full_name'),
            'age': request.form.get('age'),
            'sex': request.form.get('sex'),
            'diseases': request.form.get('diseases'),
            'medications': request.form.get('medications'),
            'smoker': request.form.get('smoker'),
            'sexual_activity': request.form.get('sexual_activity'),
            'blood_type': request.form.get('blood_type'),
            'MPID': request.form.get('MPID'),
            'asma': request.form.get('asma'),
            'base_treatment': request.form.get('base_treatment'),
            'immunosuppression': request.form.get('immunosuppression'),
            'comorbidities': request.form.get('comorbidities')
        }

        # Generate the profile URL
        profile_url = url_for('profile', health_card_number=data['health_card_number'], _external=True)

        # Generate the QR code
        qr = qrcode.QRCode(
            version=1,
            error_correction=qrcode.constants.ERROR_CORRECT_L,
            box_size=10,
            border=4,
        )
        qr.add_data(profile_url)
        qr.make(fit=True)

        img = qr.make_image(fill_color="black", back_color="white")
        buffer = io.BytesIO()
        img.save(buffer, format="PNG")
        buffer.seek(0)
        img_base64 = base64.b64encode(buffer.getvalue()).decode("utf-8")

        return render_template('QR.html', data=data, qr_code=img_base64)

    return render_template('cuestionario.html')

@app.route('/profile/<health_card_number>')
def profile(health_card_number):
    # Dummy data for demonstration (you can fetch real data from a database)
    user_profile = {
        "health_card_number": health_card_number,
        "name": "John Doe",
        "age": 30,
        "sex": "Male",
        "blood_type": "O+",
    }
    return render_template('profile.html', profile=user_profile)

if __name__ == '__main__':
    app.run(debug=True)
