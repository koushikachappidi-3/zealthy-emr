import React, { useEffect, useMemo, useState } from "react";
import { createRoot } from "react-dom/client";
import "./styles.css";

const defaultEmail = "mark@some-email-provider.net";
const defaultPassword = "Password123!";

async function api(path, options = {}) {
  const response = await fetch(path, {
    headers: {
      "Content-Type": "application/json",
      ...(options.headers || {}),
    },
    ...options,
  });

  if (!response.ok) {
    const error = await response.json().catch(() => ({}));
    throw new Error(error.detail || "Request failed");
  }

  if (response.status === 204) {
    return null;
  }

  return response.json();
}

function formatDateTime(value) {
  return new Date(value).toLocaleString([], {
    dateStyle: "medium",
    timeStyle: "short",
  });
}

function formatDate(value) {
  return new Date(`${value}T00:00:00`).toLocaleDateString([], {
    dateStyle: "medium",
  });
}

function toDateInputValue(value) {
  if (!value) {
    return "";
  }

  return value.slice(0, 10);
}

function toDateTimeLocalInputValue(value) {
  if (!value) {
    return "";
  }

  const date = new Date(value);
  const offsetDate = new Date(date.getTime() - date.getTimezoneOffset() * 60000);

  return offsetDate.toISOString().slice(0, 16);
}

function getNextRefill(prescriptions) {
  const today = new Date();
  today.setHours(0, 0, 0, 0);

  return (
    prescriptions
      .filter((prescription) => new Date(`${prescription.refill_on}T00:00:00`) >= today)
      .sort((first, second) => first.refill_on.localeCompare(second.refill_on))[0] || null
  );
}

function Shell({ active, patient, onLogout, children }) {
  const showAdminLink = active === "admin";
  const showPatientPortalLink = active === "portal";

  return (
    <div className="shell">
      <header className="topbar">
        <div className="brand">Zealthy EMR</div>
        <nav className="nav">
          {showPatientPortalLink && (
            <a className="active" href="/">
              Patient Portal
            </a>
          )}
          {showAdminLink && (
            <a className="active" href="/admin">
              Admin
            </a>
          )}
          {patient && (
            <button className="link-button" type="button" onClick={onLogout}>
              Log out
            </button>
          )}
        </nav>
      </header>
      <section className="page">{children}</section>
    </div>
  );
}

function AppointmentsTable({ appointments }) {
  if (!appointments.length) {
    return <div className="card muted">No appointments found.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Date & Time</th>
            <th>Repeat</th>
            <th>Ends</th>
          </tr>
        </thead>
        <tbody>
          {appointments.map((appointment) => (
            <tr key={`${appointment.appointment_id || appointment.id}-${appointment.datetime}`}>
              <td>{appointment.provider}</td>
              <td>{formatDateTime(appointment.datetime)}</td>
              <td>{appointment.repeat}</td>
              <td>{appointment.end_date ? formatDate(appointment.end_date) : "Not set"}</td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function PrescriptionsTable({ prescriptions, onDelete, onEdit }) {
  if (!prescriptions.length) {
    return <div className="card muted">No prescriptions found.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Medication</th>
            <th>Dosage</th>
            <th>Quantity</th>
            <th>Refill</th>
            <th>Schedule</th>
            {(onDelete || onEdit) && <th></th>}
          </tr>
        </thead>
        <tbody>
          {prescriptions.map((prescription) => (
            <tr key={prescription.id}>
              <td>{prescription.medication}</td>
              <td>{prescription.dosage}</td>
              <td>{prescription.quantity}</td>
              <td>{formatDate(prescription.refill_on)}</td>
              <td>{prescription.refill_schedule}</td>
              {(onDelete || onEdit) && (
                <td>
                  <div className="row-actions">
                    {onEdit && (
                      <button
                        className="button secondary"
                        type="button"
                        onClick={() => onEdit(prescription)}
                      >
                        Edit
                      </button>
                    )}
                    {onDelete && (
                      <button
                        className="button danger"
                        type="button"
                        onClick={() => onDelete(prescription.id)}
                      >
                        Delete
                      </button>
                    )}
                  </div>
                </td>
              )}
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function Login({ onLogin }) {
  const [error, setError] = useState("");

  async function handleSubmit(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);

    try {
      const patient = await api("/auth/login", {
        method: "POST",
        body: JSON.stringify({
          email: form.get("email"),
          password: form.get("password"),
        }),
      });
      onLogin(patient);
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  return (
    <section className="page login-page">
      <div className="intro">
        <div className="brand">Zealthy EMR</div>
        <h1>Patient Portal</h1>
        <p>
          View upcoming appointments, medication refills, and current prescription details using
          the sample credentials or credentials created by the admin.
        </p>
      </div>
      <form className="card" onSubmit={handleSubmit}>
        <h2>Patient Login</h2>
        <label className="field">
          <span>Email</span>
          <input name="email" type="email" required defaultValue={defaultEmail} />
        </label>
        <label className="field">
          <span>Password</span>
          <input name="password" type="password" required defaultValue={defaultPassword} />
        </label>
        <div className="actions">
          <button className="button" type="submit">
            Log in
          </button>
        </div>
        {error && <div className="error">{error}</div>}
      </form>
    </section>
  );
}

function PatientPortal({ patient, onLogout }) {
  const [dashboard, setDashboard] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [error, setError] = useState("");
  const [activePortalTab, setActivePortalTab] = useState("dashboard");

  useEffect(() => {
    async function loadPortal() {
      try {
        const [dashboardData, appointmentsData, prescriptionsData] = await Promise.all([
          api(`/patients/${patient.id}/dashboard`),
          api(`/patients/${patient.id}/appointments/upcoming`),
          api(`/patients/${patient.id}/prescriptions`),
        ]);
        setDashboard(dashboardData);
        setAppointments(appointmentsData);
        setPrescriptions(prescriptionsData);
      } catch (requestError) {
        setError(requestError.message);
      }
    }

    loadPortal();
  }, [patient.id]);

  if (error) {
    return (
      <Shell active="portal" patient={patient} onLogout={onLogout}>
        <div className="card error">{error}</div>
      </Shell>
    );
  }

  if (!dashboard) {
    return (
      <Shell active="portal" patient={patient} onLogout={onLogout}>
        <div className="card muted">Loading patient dashboard...</div>
      </Shell>
    );
  }

  return (
    <Shell active="portal" patient={patient} onLogout={onLogout}>
      <div className="detail-title">
        <div>
          <h1>{dashboard.name}</h1>
          <div className="muted">{dashboard.email}</div>
        </div>
      </div>

      <div className="grid three">
        <div className="stat">
          Appointments next 7 days<strong>{dashboard.upcoming_appointments.length}</strong>
        </div>
        <div className="stat">
          Refills next 7 days<strong>{dashboard.refills_due.length}</strong>
        </div>
        <div className="stat">
          Upcoming through 3 months<strong>{appointments.length}</strong>
        </div>
      </div>

      <div className="tabs" role="tablist" aria-label="Patient portal sections">
        <button
          aria-selected={activePortalTab === "dashboard"}
          className={activePortalTab === "dashboard" ? "tab active" : "tab"}
          type="button"
          onClick={() => setActivePortalTab("dashboard")}
        >
          Dashboard
        </button>
        <button
          aria-selected={activePortalTab === "appointments"}
          className={activePortalTab === "appointments" ? "tab active" : "tab"}
          type="button"
          onClick={() => setActivePortalTab("appointments")}
        >
          Appointments
        </button>
        <button
          aria-selected={activePortalTab === "prescriptions"}
          className={activePortalTab === "prescriptions" ? "tab active" : "tab"}
          type="button"
          onClick={() => setActivePortalTab("prescriptions")}
        >
          Prescriptions
        </button>
      </div>

      {activePortalTab === "dashboard" && (
        <div className="section grid two">
          <div>
            <h2>Appointments Within Next 7 Days</h2>
            <AppointmentsTable appointments={dashboard.upcoming_appointments} />
          </div>
          <div>
            <h2>Refills Within Next 7 Days</h2>
            <PrescriptionsTable prescriptions={dashboard.refills_due} />
          </div>
        </div>
      )}

      {activePortalTab === "appointments" && (
        <div className="section">
          <h2>Full Upcoming Appointment Schedule</h2>
          <AppointmentsTable appointments={appointments} />
        </div>
      )}

      {activePortalTab === "prescriptions" && (
        <div className="section">
          <h2>All Prescriptions</h2>
          <PrescriptionsTable prescriptions={prescriptions} />
        </div>
      )}
    </Shell>
  );
}

function Admin() {
  const [patients, setPatients] = useState([]);
  const [selectedPatientId, setSelectedPatientId] = useState(null);
  const [selectedPatient, setSelectedPatient] = useState(null);
  const [appointments, setAppointments] = useState([]);
  const [prescriptions, setPrescriptions] = useState([]);
  const [medications, setMedications] = useState([]);
  const [dosages, setDosages] = useState([]);
  const [error, setError] = useState("");
  const [activeAdminTab, setActiveAdminTab] = useState("patient");
  const [editingAppointment, setEditingAppointment] = useState(null);
  const [appointmentForm, setAppointmentForm] = useState({
    provider: "",
    datetime: "",
    repeat: "weekly",
    end_date: "",
  });
  const [editingPrescription, setEditingPrescription] = useState(null);
  const [prescriptionForm, setPrescriptionForm] = useState({
    medication: "",
    dosage: "",
    quantity: "1",
    refill_on: "",
    refill_schedule: "monthly",
  });

  const selectedId = useMemo(() => selectedPatientId || null, [selectedPatientId]);

  async function loadAdminData(nextPatientId = selectedPatientId) {
    try {
      const [patientList, medicationOptions, dosageOptions] = await Promise.all([
        api("/patients"),
        api("/options/medications"),
        api("/options/dosages"),
      ]);
      const patientSummaries = await Promise.all(
        patientList.map(async (patient) => {
          const [upcomingAppointments, prescriptionList] = await Promise.all([
            api(`/patients/${patient.id}/appointments/upcoming`),
            api(`/patients/${patient.id}/prescriptions`),
          ]);
          const nextAppointment = upcomingAppointments[0] || null;
          const nextRefill = getNextRefill(prescriptionList);

          return {
            ...patient,
            activePrescriptionCount: prescriptionList.length,
            nextAppointment,
            nextRefill,
            upcomingAppointmentCount: upcomingAppointments.length,
          };
        }),
      );
      const nextSelectedId = nextPatientId || null;

      setPatients(patientSummaries);
      setMedications(medicationOptions);
      setDosages(dosageOptions);
      setSelectedPatientId(nextSelectedId);

      if (nextSelectedId) {
        const [patient, appointmentList, prescriptionList] = await Promise.all([
          api(`/patients/${nextSelectedId}`),
          api(`/patients/${nextSelectedId}/appointments`),
          api(`/patients/${nextSelectedId}/prescriptions`),
        ]);
        setSelectedPatient(patient);
        setAppointments(appointmentList);
        setPrescriptions(prescriptionList);
      } else {
        setSelectedPatient(null);
        setAppointments([]);
        setPrescriptions([]);
      }
    } catch (requestError) {
      setError(requestError.message);
    }
  }

  useEffect(() => {
    loadAdminData();
  }, []);

  useEffect(() => {
    setPrescriptionForm((currentForm) => ({
      ...currentForm,
      medication: currentForm.medication || medications[0]?.name || "",
    }));
  }, [medications]);

  useEffect(() => {
    setPrescriptionForm((currentForm) => ({
      ...currentForm,
      dosage: currentForm.dosage || dosages[0]?.value || "",
    }));
  }, [dosages]);

  function resetAppointmentForm() {
    setEditingAppointment(null);
    setAppointmentForm({
      provider: "",
      datetime: "",
      repeat: "weekly",
      end_date: "",
    });
  }

  function resetPrescriptionForm() {
    setEditingPrescription(null);
    setPrescriptionForm({
      medication: medications[0]?.name || "",
      dosage: dosages[0]?.value || "",
      quantity: "1",
      refill_on: "",
      refill_schedule: "monthly",
    });
  }

  async function createPatient(event) {
    event.preventDefault();
    const formElement = event.currentTarget;
    const form = new FormData(formElement);
    const patient = await api("/patients", {
      method: "POST",
      body: JSON.stringify(Object.fromEntries(form.entries())),
    });
    formElement.reset();
    setActiveAdminTab("patient");
    await loadAdminData(patient.id);
  }

  async function updatePatient(event) {
    event.preventDefault();
    const form = new FormData(event.currentTarget);
    const body = {
      name: form.get("name") || null,
      email: form.get("email") || null,
    };

    if (form.get("password")) {
      body.password = form.get("password");
    }

    await api(`/patients/${selectedId}`, {
      method: "PUT",
      body: JSON.stringify(body),
    });
    await loadAdminData(selectedId);
  }

  async function saveAppointment(event) {
    event.preventDefault();
    const path = editingAppointment
      ? `/appointments/${editingAppointment.id}`
      : `/patients/${selectedId}/appointments`;
    const method = editingAppointment ? "PUT" : "POST";

    await api(path, {
      method,
      body: JSON.stringify({
        provider: appointmentForm.provider,
        datetime: new Date(appointmentForm.datetime).toISOString(),
        repeat: appointmentForm.repeat,
        end_date: appointmentForm.end_date || null,
      }),
    });
    resetAppointmentForm();
    await loadAdminData(selectedId);
  }

  async function savePrescription(event) {
    event.preventDefault();
    const path = editingPrescription
      ? `/prescriptions/${editingPrescription.id}`
      : `/patients/${selectedId}/prescriptions`;
    const method = editingPrescription ? "PUT" : "POST";

    await api(path, {
      method,
      body: JSON.stringify({
        medication: prescriptionForm.medication,
        dosage: prescriptionForm.dosage,
        quantity: Number(prescriptionForm.quantity),
        refill_on: prescriptionForm.refill_on,
        refill_schedule: prescriptionForm.refill_schedule,
      }),
    });
    resetPrescriptionForm();
    await loadAdminData(selectedId);
  }

  function startAppointmentEdit(appointment) {
    setActiveAdminTab("appointments");
    setEditingAppointment(appointment);
    setAppointmentForm({
      provider: appointment.provider,
      datetime: toDateTimeLocalInputValue(appointment.datetime),
      repeat: appointment.repeat,
      end_date: toDateInputValue(appointment.end_date),
    });
  }

  function startPrescriptionEdit(prescription) {
    setActiveAdminTab("prescriptions");
    setEditingPrescription(prescription);
    setPrescriptionForm({
      medication: prescription.medication,
      dosage: prescription.dosage,
      quantity: String(prescription.quantity),
      refill_on: toDateInputValue(prescription.refill_on),
      refill_schedule: prescription.refill_schedule,
    });
  }

  async function deleteAppointment(appointmentId) {
    await api(`/appointments/${appointmentId}`, { method: "DELETE" });
    if (editingAppointment?.id === appointmentId) {
      resetAppointmentForm();
    }
    await loadAdminData(selectedId);
  }

  async function deletePrescription(prescriptionId) {
    await api(`/prescriptions/${prescriptionId}`, { method: "DELETE" });
    if (editingPrescription?.id === prescriptionId) {
      resetPrescriptionForm();
    }
    await loadAdminData(selectedId);
  }

  return (
    <Shell active="admin">
      <div className="detail-title admin-page-title">
        <h1>Admin EMR</h1>
        <span>Manage patients, appointments, and prescriptions.</span>
      </div>
      {error && <div className="card error">{error}</div>}
      <div className="section">
        <h2>Patients</h2>
        <AdminPatientTable
          patients={patients}
          selectedId={selectedId}
          onSelect={(patientId) => {
            resetAppointmentForm();
            resetPrescriptionForm();
            setActiveAdminTab("patient");
            loadAdminData(patientId);
          }}
        />
      </div>
      <div className="section">
        <form className="card create-patient-card" onSubmit={createPatient}>
          <h2>Create New Patient</h2>
          <div className="grid three">
            <label className="field">
              <span>Name</span>
              <input name="name" required />
            </label>
            <label className="field">
              <span>Email</span>
              <input name="email" type="email" required />
            </label>
            <label className="field">
              <span>Password</span>
              <input name="password" required />
            </label>
          </div>
          <div className="actions">
            <button className="button" type="submit">
              Create Patient
            </button>
          </div>
        </form>
      </div>
      <section className="section workspace">
        {selectedPatient ? (
          <AdminPatientDetail
            activeTab={activeAdminTab}
            appointments={appointments}
            appointmentForm={appointmentForm}
            dosages={dosages}
            editingAppointment={editingAppointment}
            editingPrescription={editingPrescription}
            medications={medications}
            onAppointmentFormChange={setAppointmentForm}
            onCancelAppointmentEdit={resetAppointmentForm}
            onCancelPrescriptionEdit={resetPrescriptionForm}
            onPrescriptionFormChange={setPrescriptionForm}
            onSaveAppointment={saveAppointment}
            onSavePrescription={savePrescription}
            onDeleteAppointment={deleteAppointment}
            onDeletePrescription={deletePrescription}
            onEditAppointment={startAppointmentEdit}
            onEditPrescription={startPrescriptionEdit}
            onTabChange={setActiveAdminTab}
            onUpdatePatient={updatePatient}
            patient={selectedPatient}
            prescriptionForm={prescriptionForm}
            prescriptions={prescriptions}
          />
        ) : (
          <div className="card muted empty-state">
            Select a patient to manage details, appointments, and prescriptions.
          </div>
        )}
      </section>
    </Shell>
  );
}

function AdminPatientTable({ patients, selectedId, onSelect }) {
  if (!patients.length) {
    return <div className="card muted">No patients found.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Patient</th>
            <th>Email</th>
            <th>Upcoming</th>
            <th>Next Appointment</th>
            <th>Prescriptions</th>
            <th>Next Refill</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {patients.map((patient) => (
            <tr
              className={patient.id === selectedId ? "selected-row" : ""}
              key={patient.id}
            >
              <td>{patient.name}</td>
              <td>{patient.email}</td>
              <td>{patient.upcomingAppointmentCount}</td>
              <td>
                {patient.nextAppointment
                  ? `${formatDateTime(patient.nextAppointment.datetime)} with ${patient.nextAppointment.provider}`
                  : "None scheduled"}
              </td>
              <td>{patient.activePrescriptionCount}</td>
              <td>
                {patient.nextRefill
                  ? `${formatDate(patient.nextRefill.refill_on)} - ${patient.nextRefill.medication}`
                  : "None scheduled"}
              </td>
              <td>
                <button
                  className="button secondary"
                  type="button"
                  onClick={() => onSelect(patient.id)}
                >
                  View
                </button>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function AdminPatientDetail({
  activeTab,
  appointments,
  appointmentForm,
  dosages,
  editingAppointment,
  editingPrescription,
  medications,
  onAppointmentFormChange,
  onCancelAppointmentEdit,
  onCancelPrescriptionEdit,
  onPrescriptionFormChange,
  onSaveAppointment,
  onSavePrescription,
  onDeleteAppointment,
  onDeletePrescription,
  onEditAppointment,
  onEditPrescription,
  onTabChange,
  onUpdatePatient,
  patient,
  prescriptionForm,
  prescriptions,
}) {
  return (
    <div className="workspace-card">
      <div className="workspace-header">
        <div>
          <h2>Managing: {patient.name}</h2>
          <div className="muted">{patient.email}</div>
        </div>
      </div>

      <div className="tabs workspace-tabs" role="tablist" aria-label="Admin patient workspace">
        <button
          aria-selected={activeTab === "patient"}
          className={activeTab === "patient" ? "tab active" : "tab"}
          type="button"
          onClick={() => onTabChange("patient")}
        >
          Patient Info
        </button>
        <button
          aria-selected={activeTab === "appointments"}
          className={activeTab === "appointments" ? "tab active" : "tab"}
          type="button"
          onClick={() => onTabChange("appointments")}
        >
          Appointments
        </button>
        <button
          aria-selected={activeTab === "prescriptions"}
          className={activeTab === "prescriptions" ? "tab active" : "tab"}
          type="button"
          onClick={() => onTabChange("prescriptions")}
        >
          Prescriptions
        </button>
      </div>

      {activeTab === "patient" && (
        <div className="workspace-panel">
          <div className="card">
            <h2>Patient Info</h2>
            <form className="grid two" key={patient.id} onSubmit={onUpdatePatient}>
              <label className="field">
                <span>Name</span>
                <input name="name" defaultValue={patient.name} />
              </label>
              <label className="field">
                <span>Email</span>
                <input name="email" type="email" defaultValue={patient.email} />
              </label>
              <label className="field">
                <span>New Password</span>
                <input name="password" placeholder="Leave blank to keep current" />
              </label>
              <div className="actions">
                <button className="button" type="submit">
                  Save Patient
                </button>
              </div>
            </form>
          </div>
        </div>
      )}

      {activeTab === "appointments" && (
        <div className="workspace-panel grid two">
          <form className="card" onSubmit={onSaveAppointment}>
            <h2>{editingAppointment ? "Edit Appointment" : "Add Appointment"}</h2>
            <label className="field">
              <span>Provider</span>
              <input
                name="provider"
                required
                value={appointmentForm.provider}
                onChange={(event) =>
                  onAppointmentFormChange({
                    ...appointmentForm,
                    provider: event.target.value,
                  })
                }
              />
            </label>
            <label className="field">
              <span>First Date/Time</span>
              <input
                name="datetime"
                type="datetime-local"
                required
                value={appointmentForm.datetime}
                onChange={(event) =>
                  onAppointmentFormChange({
                    ...appointmentForm,
                    datetime: event.target.value,
                  })
                }
              />
            </label>
            <label className="field">
              <span>Repeat</span>
              <select
                name="repeat"
                value={appointmentForm.repeat}
                onChange={(event) =>
                  onAppointmentFormChange({
                    ...appointmentForm,
                    repeat: event.target.value,
                  })
                }
              >
                <option value="weekly">Weekly</option>
                <option value="monthly">Monthly</option>
                <option value="none">None</option>
              </select>
            </label>
            <label className="field">
              <span>End Date</span>
              <input
                name="end_date"
                type="date"
                value={appointmentForm.end_date}
                onChange={(event) =>
                  onAppointmentFormChange({
                    ...appointmentForm,
                    end_date: event.target.value,
                  })
                }
              />
            </label>
            <div className="actions">
              <button className="button" type="submit">
                {editingAppointment ? "Update Appointment" : "Add Appointment"}
              </button>
              {editingAppointment && (
                <button
                  className="button secondary"
                  type="button"
                  onClick={onCancelAppointmentEdit}
                >
                  Cancel Edit
                </button>
              )}
            </div>
          </form>

          <div>
            <h2>Appointments</h2>
            <AdminAppointmentsTable
              appointments={appointments}
              onDelete={onDeleteAppointment}
              onEdit={onEditAppointment}
            />
          </div>
        </div>
      )}

      {activeTab === "prescriptions" && (
        <div className="workspace-panel grid two">
          <form className="card" onSubmit={onSavePrescription}>
            <h2>{editingPrescription ? "Edit Prescription" : "Add Prescription"}</h2>
            <label className="field">
              <span>Medication</span>
              <select
                name="medication"
                value={prescriptionForm.medication}
                onChange={(event) =>
                  onPrescriptionFormChange({
                    ...prescriptionForm,
                    medication: event.target.value,
                  })
                }
              >
                {medications.map((option) => (
                  <option key={option.id}>{option.name}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Dosage</span>
              <select
                name="dosage"
                value={prescriptionForm.dosage}
                onChange={(event) =>
                  onPrescriptionFormChange({
                    ...prescriptionForm,
                    dosage: event.target.value,
                  })
                }
              >
                {dosages.map((option) => (
                  <option key={option.id}>{option.value}</option>
                ))}
              </select>
            </label>
            <label className="field">
              <span>Quantity</span>
              <input
                name="quantity"
                type="number"
                min="1"
                required
                value={prescriptionForm.quantity}
                onChange={(event) =>
                  onPrescriptionFormChange({
                    ...prescriptionForm,
                    quantity: event.target.value,
                  })
                }
              />
            </label>
            <label className="field">
              <span>Refill Date</span>
              <input
                name="refill_on"
                type="date"
                required
                value={prescriptionForm.refill_on}
                onChange={(event) =>
                  onPrescriptionFormChange({
                    ...prescriptionForm,
                    refill_on: event.target.value,
                  })
                }
              />
            </label>
            <label className="field">
              <span>Refill Schedule</span>
              <select
                name="refill_schedule"
                value={prescriptionForm.refill_schedule}
                onChange={(event) =>
                  onPrescriptionFormChange({
                    ...prescriptionForm,
                    refill_schedule: event.target.value,
                  })
                }
              >
                <option value="monthly">Monthly</option>
                <option value="weekly">Weekly</option>
              </select>
            </label>
            <div className="actions">
              <button className="button" type="submit">
                {editingPrescription ? "Update Prescription" : "Add Prescription"}
              </button>
              {editingPrescription && (
                <button
                  className="button secondary"
                  type="button"
                  onClick={onCancelPrescriptionEdit}
                >
                  Cancel Edit
                </button>
              )}
            </div>
          </form>

          <div>
            <h2>Prescriptions</h2>
            <PrescriptionsTable
              prescriptions={prescriptions}
              onDelete={onDeletePrescription}
              onEdit={onEditPrescription}
            />
          </div>
        </div>
      )}
    </div>
  );
}

function AdminAppointmentsTable({ appointments, onDelete, onEdit }) {
  if (!appointments.length) {
    return <div className="card muted">No appointments found.</div>;
  }

  return (
    <div className="table-wrap">
      <table>
        <thead>
          <tr>
            <th>Provider</th>
            <th>Date & Time</th>
            <th>Repeat</th>
            <th>Ends</th>
            <th></th>
          </tr>
        </thead>
        <tbody>
          {appointments.map((appointment) => (
            <tr key={appointment.id}>
              <td>{appointment.provider}</td>
              <td>{formatDateTime(appointment.datetime)}</td>
              <td>{appointment.repeat}</td>
              <td>{appointment.end_date ? formatDate(appointment.end_date) : "Not set"}</td>
              <td>
                <div className="row-actions">
                  <button
                    className="button secondary"
                    type="button"
                    onClick={() => onEdit(appointment)}
                  >
                    Edit
                  </button>
                  <button
                    className="button danger"
                    type="button"
                    onClick={() => onDelete(appointment.id)}
                  >
                    Delete
                  </button>
                </div>
              </td>
            </tr>
          ))}
        </tbody>
      </table>
    </div>
  );
}

function App() {
  const [patient, setPatient] = useState(() =>
    JSON.parse(sessionStorage.getItem("patient") || "null"),
  );
  const isAdmin = window.location.pathname.startsWith("/admin");

  function handleLogin(nextPatient) {
    sessionStorage.setItem("patient", JSON.stringify(nextPatient));
    setPatient(nextPatient);
  }

  function handleLogout() {
    sessionStorage.removeItem("patient");
    setPatient(null);
  }

  if (isAdmin) {
    return <Admin />;
  }

  if (!patient) {
    return <Login onLogin={handleLogin} />;
  }

  return <PatientPortal patient={patient} onLogout={handleLogout} />;
}

createRoot(document.querySelector("#app")).render(<App />);
