<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Upcoming Appointments</h2>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>#</th>
            <th>Patient Name</th>
            <th>Doctor Name</th>
            <th>Department</th>
            <th>Date</th>
            <th>Slot</th>
            <th>Status</th>
            <th>History</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingAppointments"><td colspan="8" class="loading-text">Loading appointments...</td></tr>
          <tr v-else-if="appointments.length === 0">
            <td colspan="8" class="empty-state">No appointments found</td>
          </tr>
          <template v-else>
            <tr v-for="(appointment, index) in appointments" :key="appointment.id">

              <td>{{ index + 1 }}</td>
              <td>{{ appointment.patient_name }}</td>
              <td>{{ appointment.doctor_name }}</td>
              <td>{{ appointment.department }}</td>
              <td>{{ appointment.date }}</td>
              <td>{{ appointment.slot }}</td>
              <td>
                <span :class="['status', appointment.status]">
                  {{ appointment.status }}
                </span>
              </td>
              <td>
                <button class="action-btn action-view" @click="openHistoryModal(appointment)">View</button>
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
						<th>Prescriptions</th>
						<th>Medicines</th>
					</tr>
				</thead>
        <tbody>
          <tr v-if="selectedPatientHistory.length === 0">
            <td colspan="8" class="empty-state">No history found</td>
          </tr>
          <tr v-for="entry in selectedPatientHistory" :key="entry.id">
            <td>{{ entry.id }}</td>
            <td>{{ entry.date || '-' }}</td>
            <td>{{ entry.doctor_name || '-' }}</td>
            <td>{{ entry.department || '-' }}</td>
            <td>{{ entry.tests_done || '-' }}</td>
            <td>{{ entry.diagnosis || '-' }}</td>
            <td>{{ entry.prescription || '-' }}</td>
            <td>{{ entry.medicines || '-' }}</td>
          </tr>
        </tbody>
        </table>
      </div>
      
    </div>

  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

const appointments = ref([]);
const loadingAppointments = ref(false);
const showHistoryModal = ref(false);
const selectedPatientName = ref('');
const selectedPatientHistory = ref([]);

const loadAppointments = async () => {
  loadingAppointments.value = true;
  try {
    const response = await api.get('/appointments');
    appointments.value = (response.data || []).sort((a, b) => new Date(a.date) - new Date(b.date));
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

onMounted(async () => {
  await loadAppointments();
});
</script>
