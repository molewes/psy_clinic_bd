from datetime import datetime
from flask import Flask, flash, render_template, request, redirect, url_for
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import or_, func, create_engine, text
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = 'postgresql://postgres:Molewes1103!@localhost:5432/psy_clinic'
db = SQLAlchemy(app)
app.static_folder = 'static'



class Patient(db.Model):
    __tablename__ = 'patients'
    patient_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    date_of_birth = db.Column(db.Date)
    gender = db.Column(db.String(10))
    address = db.Column(db.String(100))
    phone_number = db.Column(db.String(15))
    email = db.Column(db.String(100))

class Specialist(db.Model):
    __tablename__ = 'specialists'
    specialist_id = db.Column(db.Integer, primary_key=True)
    name = db.Column(db.String(50))
    surname = db.Column(db.String(50))
    timetable = db.Column(db.String(100))
    contact_info = db.Column(db.String(100))
    specialization_name = db.Column(db.String(50), db.ForeignKey('specializations.specialization_name'))

class Specialization(db.Model):
    __tablename__ = 'specializations'
    specialization_name = db.Column(db.String(50), primary_key=True)
    specialists = db.relationship('Specialist', backref='specialization', lazy=True) 

class Diagnosis(db.Model):
    __tablename__ = 'diagnoses'
    diagnosis_id = db.Column(db.Integer, primary_key=True)
    diagnosis_name = db.Column(db.String(100))
    description = db.Column(db.String(200))
    date_diagnosed = db.Column(db.Date)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    specialist_id = db.Column(db.Integer, db.ForeignKey('specialists.specialist_id'))
    patient = db.relationship('Patient', backref='diagnoses')
    specialist = db.relationship('Specialist', backref='diagnoses')

class Session(db.Model):
    __tablename__ = 'sessions'
    sessions_id = db.Column(db.Integer, primary_key=True)
    start_datetime = db.Column(db.TIMESTAMP(timezone=True))
    duration = db.Column(db.Interval)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    specialist_id = db.Column(db.Integer, db.ForeignKey('specialists.specialist_id'))
    session_type = db.Column(db.String(50))
    notes = db.Column(db.Text)
    patient = db.relationship('Patient', backref='sessions')
    specialist = db.relationship('Specialist', backref='sessions')



class TreatmentPlan(db.Model):
    __tablename__ = 'treatment_plans'
    plan_id = db.Column(db.Integer, primary_key=True)
    plan_descriptions = db.Column(db.Text)
    methods = db.Column(db.Text)
    start_date = db.Column(db.Date)
    end_date = db.Column(db.Date)
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    specialist_id = db.Column(db.Integer, db.ForeignKey('specialists.specialist_id'))
    
    patient = db.relationship('Patient', backref='treatment_plans')
    specialist = db.relationship('Specialist', backref='treatment_plans')

class Prescription(db.Model):
    __tablename__ = 'medicament_prescriptions'
    prescription_id = db.Column(db.Integer, primary_key=True)
    medicament_name = db.Column(db.String(100), db.ForeignKey('medicaments.medicament_name'))
    patient_id = db.Column(db.BigInteger, db.ForeignKey('patients.patient_id'))
    specialist_id = db.Column(db.BigInteger, db.ForeignKey('specialists.specialist_id'))
    prescription_date = db.Column(db.Date)
    instruction = db.Column(db.Text)

    medicament = db.relationship('Medicament', backref='prescriptions')
    patient = db.relationship('Patient', backref='prescriptions')
    specialist = db.relationship('Specialist', backref='prescriptions')

class Medicament(db.Model):
    __tablename__ = 'medicaments'
    medicament_name = db.Column(db.String(100), primary_key=True)
    dosage = db.Column(db.String(100))
    instruction = db.Column(db.Text)

class Appointment(db.Model):
    __tablename__ = 'appointments'
    appointment_id = db.Column(db.Integer, primary_key=True)
    specialist_id = db.Column(db.Integer, db.ForeignKey('specialists.specialist_id'))
    patient_id = db.Column(db.Integer, db.ForeignKey('patients.patient_id'))
    appointment_datetime = db.Column(db.TIMESTAMP, nullable=False)
    status_name = db.Column(db.String(50), db.ForeignKey('appointments_status.status_name'), nullable=False)
    notes = db.Column(db.Text)

    specialist = db.relationship('Specialist', backref='appointments')
    patient = db.relationship('Patient', backref='appointments')
    status = db.relationship("AppointmentStatus", backref="appointments_status")

class AppointmentStatus(db.Model):
    __tablename__ = 'appointments_status'
    status_name = db.Column(db.String(50), primary_key=True)

@app.route('/', methods=['GET', 'POST'])
def index():
    if request.method == 'POST':
        start_date_str = request.form.get('start_date')
        end_date_str = request.form.get('end_date')
        specialist_id = request.form.get('specialist_id')
        patient_id = request.form.get('patient_id')

        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')

        query = Appointment.query.filter(Appointment.appointment_datetime.between(start_date, end_date))

        if specialist_id:
            query = query.filter_by(specialist_id=specialist_id)

        if patient_id:
            query = query.filter_by(patient_id=patient_id)

        appointments = query.all()
    else:
        appointments = Appointment.query.all()

    appointments_status = AppointmentStatus.query.all()
    specialists = Specialist.query.all()
    patients = Patient.query.all()

    return render_template('index.html', appointments=appointments, appointments_status=appointments_status, specialists=specialists, patients=patients)

    
@app.route('/patients')
def patients():
    patients = Patient.query.all()
    return render_template('patients.html', patients=patients)

@app.route('/specialists')
def specialists():
    specialists = Specialist.query.all()
    specializations = Specialization.query.all()
    return render_template('specialists.html', specialists=specialists, specializations=specializations)

@app.route('/diagnoses')
def diagnoses():
    diagnoses = Diagnosis.query.all()
    return render_template('diagnoses.html', diagnoses=diagnoses)

@app.route('/sessions')
def sessions():
    sessions = Session.query.all()
    return render_template('sessions.html', sessions=sessions)

@app.route('/treatment_plans')
def treatment_plans():
    treatment_plans = TreatmentPlan.query.all()
    return render_template('treatment_plans.html',treatment_plans=treatment_plans)

@app.route('/prescriptions')
def prescriptions():
    prescriptions = Prescription.query.all()
    return render_template('prescriptions.html', prescriptions=prescriptions)

@app.route('/medicaments')
def medicaments():
    medicaments = Medicament.query.all()
    return render_template('medicaments.html', medicaments=medicaments)

@app.route('/', methods=['GET', 'POST'])
def main_page():
    if request.method == 'POST':
        query = request.form.get('query')
        appointments = search_appointments(query)
        return render_template('index.html', appointments=appointments, query=query)
    else:
        return render_template('index.html')

@app.route('/search_appointments')
def search_appointments():
    query = request.args.get('query')

    appointments = Appointment.query.join(Patient, Appointment.patient_id == Patient.patient_id) \
                                    .join(Specialist, Appointment.specialist_id == Specialist.specialist_id) \
                                    .filter(or_(
                                        Patient.name.ilike(f'%{query}%'),  
                                        Patient.surname.ilike(f'%{query}%'), 
                                        Specialist.name.ilike(f'%{query}%'),  
                                        Specialist.surname.ilike(f'%{query}%'),  
                                        func.to_char(Appointment.appointment_datetime, 'YYYY-MM-DD HH24:MI:SS').ilike(f'%{query}%')  
                                    )).all()

    return render_template('index.html', appointments=appointments)


@app.route('/add_appointment_form')
def add_appointment_form():
    patients = Patient.query.all()
    specialists = Specialist.query.all()
    appointments_status = AppointmentStatus.query.all()  
    return render_template('add_appointment.html', patients=patients, specialists=specialists, appointments_status=appointments_status)

@app.route('/add_appointment', methods=['POST'])
def add_appointment():
    patient_id = request.form['patient_id']
    specialist_id = request.form['specialist_id']
    appointment_datetime = request.form['appointment_datetime']
    status_name = request.form['status_name']
    notes = request.form['notes']

    patient = Patient.query.get(patient_id)
    specialist = Specialist.query.get(specialist_id)

    if patient is None or specialist is None:
        flash('Пациент или специалист не найдены', 'error')
        return redirect(url_for('index'))

    new_appointment = Appointment(
        patient_id=patient.patient_id,
        specialist_id=specialist.specialist_id,
        appointment_datetime=appointment_datetime,
        status_name=status_name,
        notes=notes
    )
    db.session.add(new_appointment)
    db.session.commit()

    return redirect(url_for('index'))

@app.route('/edit_appointment/<int:appointment_id>', methods=['GET', 'POST'])
def edit_appointment(appointment_id):
    # Находим запись о приеме по ее ID
    appointment = Appointment.query.get_or_404(appointment_id)
    appointments_status = AppointmentStatus.query.all()
    
    if request.method == 'GET':
        # Отображаем форму редактирования при GET-запросе
        return render_template('edit_appointment.html', appointment=appointment, appointments_status=appointments_status)
    elif request.method == 'POST':
        print(request.form)
        # Обрабатываем данные из формы при POST-запросе
        patient_name = request.form['patient_name']
        patient_surname = request.form['patient_surname']
        specialist_name = request.form['specialist_name']
        specialist_surname = request.form['specialist_surname']
        appointment_datetime = request.form['appointment_datetime']
        status_name = request.form['status_name']
        notes = request.form['notes']

        # Находим пациента и специалиста по именам и фамилиям
        patient = Patient.query.filter_by(name=patient_name, surname=patient_surname).first()
        specialist = Specialist.query.filter_by(name=specialist_name, surname=specialist_surname).first()

        if patient and specialist:
            # Обновляем данные записи о приеме
            appointment.patient_id = patient.patient_id
            appointment.specialist_id = specialist.specialist_id
            appointment.appointment_datetime = appointment_datetime
            appointment.status_name = status_name
            appointment.notes = notes

            # Сохраняем изменения в базе данных
            db.session.commit()

            # Перенаправляем пользователя после сохранения изменений
            return redirect(url_for('index'))
        else:
            return redirect(url_for('index'))

@app.route('/delete_appointment/<int:appointment_id>', methods=['POST'])
def delete_appointment(appointment_id):
    appointment = Appointment.query.get_or_404(appointment_id)
    db.session.delete(appointment)
    db.session.commit()
    flash('Запись о приеме удалена успешно', 'success')
    return redirect(url_for('index'))

@app.route('/add_patient', methods=['POST'])
def add_patient():
    name = request.form['name']
    surname = request.form['surname']
    date_of_birth = request.form['date_of_birth']
    gender = request.form['gender']
    address = request.form['address']
    phone_number = request.form['phone_number']
    email = request.form['email']

    # Создаем нового пациента
    new_patient = Patient(name=name, surname=surname, date_of_birth=date_of_birth, gender=gender, address=address, phone_number=phone_number, email=email)
    # Добавляем пациента в базу данных
    db.session.add(new_patient)
    db.session.commit()

    return redirect(url_for('patients'))

@app.route('/delete_patient/<int:patient_id>', methods=['POST'])
def delete_patient(patient_id):
    patient = Patient.query.get_or_404(patient_id)
    db.session.delete(patient)
    db.session.commit()

    return redirect(url_for('patients'))

@app.route('/edit_patient/<int:patient_id>', methods=['GET', 'POST'])
def edit_patient(patient_id):
    # Находим пациента по его ID
    patient = Patient.query.get_or_404(patient_id)
    
    if request.method == 'GET':
        # Отображаем форму редактирования при GET-запросе
        return render_template('edit_patient.html', patient=patient)
    elif request.method == 'POST':
        # Обрабатываем данные из формы при POST-запросе
        name = request.form['name']
        surname = request.form['surname']
        address = request.form['address']
        date_of_birth = request.form['date_of_birth']
        gender = request.form['gender']
        phone_number = request.form['phone_number']
        email = request.form['email']

        # Обновляем данные пациента
        patient.name = name
        patient.surname = surname
        patient.date_of_birth = date_of_birth
        patient.gender = gender
        patient.address = address
        patient.phone_number = phone_number
        patient.email = email

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Перенаправляем пользователя после сохранения изменений
        flash('Данные пациента успешно обновлены', 'success')
        return redirect(url_for('patients'))

@app.route('/', methods=['GET', 'POST'])
def main_pages():
    if request.method == 'POST':
        query = request.form.get('query')
        patients = search_patients(query)
        return render_template('patients.html', patients=patients, query=query)
    else:
        return render_template('patients.html')

@app.route('/search_patients')
def search_patients():
    query = request.args.get('query')

    # Поиск пациентов в базе данных по запросу пользователя
    patients = Patient.query.filter(or_(
        Patient.name.ilike(f'%{query}%'),  # Поиск по имени пациента
        Patient.surname.ilike(f'%{query}%'),  # Поиск по фамилии пациента
        func.to_char(Patient.date_of_birth, 'YYYY-MM-DD').ilike(f'%{query}%'),
        Patient.gender.ilike(f'%{query}%'),  # Поиск по полу пациента
        Patient.address.ilike(f'%{query}%'),  # Поиск по адресу пациента
        Patient.phone_number.ilike(f'%{query}%'),  # Поиск по номеру телефона пациента
        Patient.email.ilike(f'%{query}%')  # Поиск по адресу электронной почты пациента
    )).all()

    return render_template('patients.html', patients=patients)

@app.route('/add_specialist', methods=['POST'])
def add_specialist():
    name = request.form['name']
    surname = request.form['surname']
    timetable = request.form['timetable']
    contact_info = request.form['contact_info']
    specialization_name = request.form['specialization_name']

    new_specialist = Specialist(
        name=name,
        surname=surname,
        timetable=timetable,
        contact_info=contact_info,
        specialization_name=specialization_name
    )

    db.session.add(new_specialist)
    db.session.commit()

    flash('Специалист успешно добавлен', 'success')
    return redirect(url_for('specialists'))


@app.route('/edit_specialist/<int:specialist_id>', methods=['GET', 'POST'])
def edit_specialist(specialist_id):
    # Находим специалиста по его ID
    specialist = Specialist.query.get_or_404(specialist_id)

    # Получаем все специализации для отображения в выпадающем списке
    specializations = Specialization.query.all()
    
    if request.method == 'GET':
        # Отображаем форму редактирования при GET-запросе
        return render_template('edit_specialist.html', specialist=specialist, specializations=specializations)
    elif request.method == 'POST':
        # Обрабатываем данные из формы при POST-запросе
        name = request.form['name']
        surname = request.form['surname']
        timetable = request.form['timetable']
        contact_info = request.form['contact_info']
        specialization_name = request.form['specialization_name']

        # Обновляем данные специалиста
        specialist.name = name
        specialist.surname = surname
        specialist.timetable = timetable
        specialist.contact_info = contact_info
        specialist.specialization_name = specialization_name

        # Сохраняем изменения в базе данных
        db.session.commit()

        # Перенаправляем пользователя после сохранения изменений
        flash('Данные специалиста успешно обновлены', 'success')
        return redirect(url_for('specialists'))


@app.route('/delete_specialist/<int:specialist_id>', methods=['POST'])
def delete_specialist(specialist_id):
    specialist = Specialist.query.get_or_404(specialist_id)
    db.session.delete(specialist)
    db.session.commit()
    flash('Специалист успешно удален', 'success')
    return redirect(url_for('specialists'))

@app.route('/search_specialists')
def search_specialists():
    query = request.args.get('query')
        
    specialists = Specialist.query.filter(or_(
        (Specialist.name.ilike(f'%{query}%')),
        (Specialist.surname.ilike(f'%{query}%')),
        (Specialist.timetable.ilike(f'%{query}%')),
        (Specialist.contact_info.ilike(f'%{query}%')),
        (Specialist.specialization_name.ilike(f'%{query}%'))
    )).all()
    return render_template('specialists.html', specialists=specialists)

engine = create_engine('postgresql://postgres:Molewes1103!@localhost/psy_clinic')


@app.route('/add_diagnosis', methods=['POST'])
def add_diagnosis():
    diagnosis_name = request.form['diagnosis_name']
    description = request.form['description']
    date_diagnosed = datetime.strptime(request.form['date_diagnosed'], '%Y-%m-%d')
    patient_name = request.form['patient_name']
    patient_surname = request.form['patient_surname']
    specialist_name = request.form['specialist_name']
    specialist_surname = request.form['specialist_surname']

    # Получаем объекты пациента и специалиста из базы данных по их именам и фамилиям
    patient = Patient.query.filter_by(name=patient_name, surname=patient_surname).first()
    specialist = Specialist.query.filter_by(name=specialist_name, surname=specialist_surname).first()

    if not patient:
        # Обработка случая, если пациент не найден в базе данных
        return "Patient not found", 404

    if not specialist:
        # Обработка случая, если специалист не найден в базе данных
        return "Specialist not found", 404

    # Создаем новый объект диагноза, используя полученные объекты пациента и специалиста
    new_diagnosis = Diagnosis(
        diagnosis_name=diagnosis_name,
        description=description,
        date_diagnosed=date_diagnosed,
        patient=patient,
        specialist=specialist
    )

    # Добавляем диагноз в базу данных
    db.session.add(new_diagnosis)
    db.session.commit()

    # Перенаправляем пользователя на страницу со всеми диагнозами
    return redirect(url_for('diagnoses'))

@app.route('/search_diagnoses')
def search_diagnoses():
    query = request.args.get('query')
        
    diagnoses = Diagnosis.query.join(Patient).join(Specialist).filter(or_(
        (Diagnosis.diagnosis_name.ilike(f'%{query}%')),
        (Diagnosis.description.ilike(f'%{query}%')),
        func.to_char(Diagnosis.date_diagnosed, 'YYYY-MM-DD').ilike(f'%{query}%'),
        ((Patient.name + ' ' + Patient.surname).ilike(f'%{query}%')),
        ((Specialist.name + ' ' + Specialist.surname).ilike(f'%{query}%')))).all()
    return render_template('diagnoses.html', diagnoses=diagnoses)

@app.route('/delete_diagnosis/<int:diagnosis_id>', methods=['POST'])
def delete_diagnosis(diagnosis_id):
    # Находим запись о диагнозе по её ID
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)
    
    # Удаляем запись из базы данных
    db.session.delete(diagnosis)
    db.session.commit()
    
    # Перенаправляем пользователя после удаления
    return redirect(url_for('diagnoses'))  

@app.route('/edit_diagnosis/<int:diagnosis_id>', methods=['GET', 'POST'])
def edit_diagnosis(diagnosis_id):
    diagnosis = Diagnosis.query.get_or_404(diagnosis_id)

    if request.method == 'POST':
        diagnosis.diagnosis_name = request.form['diagnosis_name']
        diagnosis.description = request.form['description']
        diagnosis.date_diagnosed = request.form['date_diagnosed']

        db.session.commit()

        return redirect(url_for('diagnoses'))

    return render_template('edit_diagnosis.html', diagnosis=diagnosis)

@app.route('/edit_session/<int:sessions_id>', methods=['GET', 'POST'])
def edit_session(sessions_id):
    session = Session.query.get_or_404(sessions_id)

    if request.method == 'POST':
        session.start_datetime = request.form['start_datetime']
        session.duration = request.form['duration']
        session.session_type = request.form['session_type']
        session.notes = request.form['notes']
        db.session.commit()

        return redirect(url_for('sessions'))

    # Преобразование start_datetime в нужный формат
    session.start_datetime_str = session.start_datetime.strftime('%Y-%m-%dT%H:%M')

    return render_template('edit_session.html', session=session)

@app.route('/delete_session/<int:sessions_id>', methods=['POST'])
def delete_session(sessions_id):
    session = Session.query.get_or_404(sessions_id)
    db.session.delete(session)
    db.session.commit()

    return redirect(url_for('sessions'))


@app.route('/total_session_duration_per_patient', methods=['GET'])
def total_session_duration_per_patient():
    # Выполнение запроса SQL для получения суммарной продолжительности сеансов для каждого пациента
    query = """
        SELECT patients.name, patients.surname, SUM(EXTRACT(EPOCH FROM duration)) as total_duration_seconds
        FROM patients
        JOIN sessions ON patients.patient_id = sessions.patient_id
        GROUP BY patients.patient_id, patients.name, patients.surname;
    """
    query = text(query)
    result = db.session.execute(query)

    # Подготовка данных для передачи в шаблон
    data = [{'name': row[0], 'surname': row[1], 'total_duration_seconds': row[2]/3600} for row in result]



    # Отображение результата на веб-странице
    return render_template('total_session_duration_per_patient.html', data=data)


if __name__ == '__main__':
    app.run(debug=True)
