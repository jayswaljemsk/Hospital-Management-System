<template>
    <div class="user-page">
        <div class="page-header">
            <h2 class="page-title">Upcoming Appointments</h2>
        </div>

        <div class="table-wrap">
            <table class="data-table">
                <thead>
                    <tr>
                        <th>ID</th>
                        <th>Patient Name</th>
                        <th>Date</th>
                        <th>Slot</th>
                        <th>Status</th>
                        <th>History</th>
                        <th>Action</th>
                    </tr>
                </thead>
                <tbody>
                    <tr v-if="loadingAppointments"><td colspan="7" class="loading-text">Loading appointments...</td></tr>
                    <tr v-else-if="appointments.length === 0">
                        <td colspan="7" class="empty-state">No appointments found</td>
                    </tr>
                    <template v-else>
                        <tr v-for="appointment in appointments" :key="appointment.id">
                            <td>{{ appointment.id }}</td>
                            <td>{{ appointment.patient_name }}</td>
                            <td>{{ appointment.date }}</td>
                            <td>{{ appointment.slot }}</td>
                            <td>
                                <span :class="['status', appointment.status]">
                                    {{ appointment.status }}
                                </span>
                            </td>
                            <td>
                                <button class="action-btn action-view" @click="openHistoryModal(appointment)">View</button>
                                <span v-if="appointment.status=='booked'">| </span>
                                <button v-if="appointment.status=='booked'" class="action-btn action-edit" @click="editTreatment(appointment.id)" >Update</button>
                            </td>
                            <td>
                                <div v-if="appointment.status=='booked'">
                                    <button class="action-btn action-complete" @click="completeAppointment(appointment.id)" >Complete</button>
                                    <span>| </span>
                                    <button class="action-btn action-delete" @click="cancelAppointment(appointment.id)" >Cancel</button>
                                </div>
                                <span v-else>-</span>
                            </td>
                        </tr>
                    </template>
                </tbody>
            </table>
        </div>

        <div v-if="showHistoryModal" class="modal-overlay">
            <div class="modal-card modal-content">
                <div class="modal-top">
                    <h3>Patient History of {{ selectedPatientName }}</h3>
                    <button @click="closeHistoryModal" class="close-btn">×</button>
                </div>
                <table class="data-table">
                    <thead>
                        <tr>
                            <th>ID</th>
                            <th>Date</th>
                            <th>Doctor</th>
                            <th>Department</th>
                            <th>Tests Done</th>
                            <th>Diagnosis</th>
                            <th>Prescription</th>
                            <th>Medicines</th>
                        </tr>
                    </thead>
                    <tbody>
                        <tr v-if="selectedPatientHistory.length === 0">
                            <td colspan="8" class="empty-state">No history found</td>
                        </tr>
                        <template v-else>
                            <tr v-for="record in selectedPatientHistory" :key="record.id">
                                <td>{{ record.id }}</td>
                                <td>{{ record.date }}</td>
                                <td>{{ record.doctor_name }}</td>
                                <td>{{ record.department || '-' }}</td>
                                <td>{{ record.tests_done || '-' }}</td>
                                <td>{{ record.diagnosis || '-' }}</td>
                                <td>{{ record.prescription || '-' }}</td>
                                <td>{{ record.medicines || '-' }}</td>
                            </tr>
                        </template>
                    </tbody>
                </table>
            </div>
        </div>

        <div v-if="showEditForm" class="modal-overlay">
            <div class="modal-card">
                <div class="modal-top">
                    <h3>Update Treatment Details</h3>
                    <button @click="closeEditForm" class="close-btn">×</button>
                </div>
                <form @submit.prevent="updateTreatment" class="form-stack">
                    <div class="form-group">
                        <label for="tests_done">Tests Done:</label>
                        <input id="tests_done" v-model="editTreatmentData.tests_done" type="text" />
                    </div>
                    <div class="form-group">
                        <label for="diagnosis">Diagnosis:</label>
                        <input id="diagnosis" v-model="editTreatmentData.diagnosis" type="text" />
                    </div>
                    <div class="form-group">
                        <label for="prescription">Prescription:</label>
                        <input id="prescription" v-model="editTreatmentData.prescription" type="text" />
                    </div>
                    <div class="form-group">
                        <label for="medicines">Medicines:</label>
                        <input id="medicines" v-model="editTreatmentData.medicines" type="text" />
                    </div>
                    <div class="form-actions">
                        <button type="submit" class="action-btn action-edit">Save</button>
                    </div>
                </form>
            </div>
        </div>

    </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

const initialEditTreatment = () => ({
    id: null,
    tests_done: '',
    diagnosis: '',
    prescription: '',
    medicines: '',
});

const appointments = ref([]);
const loadingAppointments = ref(false);
const showHistoryModal = ref(false);
const selectedPatientName = ref('');
const selectedPatientHistory = ref([]);
const showEditForm = ref(false);
const editTreatmentData = ref(initialEditTreatment());

const loadAppointments = async () => {
    loadingAppointments.value = true;
    try {
        const response = await api.get('/appointments');
        appointments.value = response.data || [];
        appointments.value.sort((a, b) => new Date(a.date) - new Date(b.date));
    } catch (error) {
        alert('Failed to load appointments: ' + (error?.message || ''));
        appointments.value = [];
    } finally {
        loadingAppointments.value = false;
    }
};

const openHistoryModal = (appointment) => {
    selectedPatientName.value = appointment.patient_name || 'Patient';
    selectedPatientHistory.value = appointment.history || [];
    showHistoryModal.value = true;
};

const closeHistoryModal = () => {
    showHistoryModal.value = false;
    selectedPatientName.value = '';
    selectedPatientHistory.value = [];
};

const loadTreatment = async (appointmentId) => {
    try {
        const response = await api.get(`/treatments/${appointmentId}`);
        return response.data || {};
    } catch (error) {
        alert('Failed to load treatment details: ' + (error?.message || ''));
        return {};
    }
};

const editTreatment = async (appointmentId) => {
    const treatment = await loadTreatment(appointmentId);

    editTreatmentData.value = {
        id: treatment.appointment_id || appointmentId,
        tests_done: treatment.tests_done || '',
        diagnosis: treatment.diagnosis || '',
        prescription: treatment.prescription || '',
        medicines: treatment.medicines || '',
    };
    showEditForm.value = true;
};

const updateTreatment = async () => {
    try {
        await api.put(`/treatments/${editTreatmentData.value.id}`, editTreatmentData.value);
        closeEditForm();
        await loadAppointments();
    } catch (error) {
        alert('Failed to update treatment: ' + (error?.message || ''));
    }
};

const closeEditForm = () => {
    showEditForm.value = false;
    editTreatmentData.value = initialEditTreatment();
};

const completeAppointment = async (appointmentId) => {
    try {
        const response = await api.patch(`/appointments/${appointmentId}`, { status: 'completed' });
        alert(response.message);
        await loadAppointments();
    } catch (error) {
        alert('Failed to complete appointment: ' + (error?.message || ''));
    }
};

const cancelAppointment = async (appointmentId) => {
    if (!confirm(`Cancel appointment #${appointmentId}?`)) return;

    try {
        const response = await api.patch(`/appointments/${appointmentId}`, { status: 'cancelled' });
        await api.delete(`/treatments/${appointmentId}`);
        alert(response.message);
        await loadAppointments();
    } catch (error) {
        alert('Failed to cancel appointment: ' + (error?.message || ''));
    }
};

onMounted(async () => {
    await loadAppointments();
});
</script>