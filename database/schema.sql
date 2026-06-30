CREATE TABLE patients (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL,
    email VARCHAR(255) NOT NULL UNIQUE,
    password VARCHAR(255) NOT NULL
);

CREATE TABLE appointments (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    provider VARCHAR(255) NOT NULL,
    datetime TIMESTAMP NOT NULL,
    repeat VARCHAR(50) NOT NULL,
    end_date DATE,
    CONSTRAINT fk_patient_appointments
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE
);

CREATE TABLE prescriptions (
    id SERIAL PRIMARY KEY,
    patient_id INTEGER NOT NULL,
    medication VARCHAR(255) NOT NULL,
    dosage VARCHAR(50) NOT NULL,
    quantity INTEGER NOT NULL,
    refill_on DATE NOT NULL,
    refill_schedule VARCHAR(50) NOT NULL,
    CONSTRAINT fk_patient_prescriptions
        FOREIGN KEY (patient_id)
        REFERENCES patients(id)
        ON DELETE CASCADE
);

CREATE TABLE medication_options (
    id SERIAL PRIMARY KEY,
    name VARCHAR(255) NOT NULL UNIQUE
);

CREATE TABLE dosage_options (
    id SERIAL PRIMARY KEY,
    value VARCHAR(50) NOT NULL UNIQUE
);
