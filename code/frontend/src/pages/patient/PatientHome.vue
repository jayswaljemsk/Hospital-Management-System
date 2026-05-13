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
            <th>Doctor Name</th>
            <th>Department</th>
            <th>Date</th>
            <th>Slot</th>
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingAppointments"><td colspan="7" class="loading-text">Loading appointments...</td></tr>
          <template v-else>
            <tr v-if="appointments.length === 0">
              <td colspan="7" class="empty-state">No appointments found</td>
            </tr>
            <tr v-for="appointment in appointments" :key="appointment.id">
              <td>{{ appointment.id }}</td>
              <td>{{ appointment.doctor_name }}</td>
              <td>{{ appointment.department }}</td>
              <td>{{ appointment.date }}</td>
              <td>{{ appointment.slot }}</td>
              <td>
                <span :class="['status', appointmentStatusClass(appointment.status)]">
                  {{ appointment.status }}
                </span>
              </td>
              <td>
                <button v-if="appointment.status === 'booked'" class="action-btn action-delete" @click="cancelAppointment(appointment.id)">Cancel</button>
                <span v-else>-</span>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>
  </div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

const appointments = ref([]);
const loadingAppointments = ref(false);

const appointmentStatusClass = (status) => {
  if (status === 'booked') return 'booked';
  if (status === 'completed') return 'completed';
  if (status === 'cancelled') return 'cancelled';
  return 'unknown';
};

const loadAppointments = async () => {
  loadingAppointments.value = true;
  try {
    const response = await api.get('/appointments');
    appointments.value = (response?.data || []).sort((a, b) => new Date(a.date) - new Date(b.date));

  } catch (error) {
    alert('Failed to load appointments: ' + (error?.message || ''));
    appointments.value = [];
  } finally {
    loadingAppointments.value = false;
  }
};

const cancelAppointment = async (appointmentId) => {
    if (!confirm(`Cancel appointment #${appointmentId}?`)) return;

    try {
        const response = await api.patch(`/appointments/${appointmentId}`, { status: 'cancelled' });
      alert(response.message);
    } catch (error) {
      alert('Failed to cancel appointment: ' + (error?.message || ''));
    } finally {
      await loadAppointments();
    }
};

onMounted(async () => {
  await loadAppointments();
});
</script>
