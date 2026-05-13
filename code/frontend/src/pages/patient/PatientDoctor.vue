<template>
  <div class="user-page">
      <div class="page-header">
          <h2 class="page-title">Doctors</h2>
      </div>

      <div class="toolbar">
        <div class="toolbar-fields">
          <input
            v-model="searchFilters.name"
            type="text"
            class="toolbar-input"
            placeholder="Search by doctor name"
            @keyup.enter="searchDoctors"
          />
          <select v-model="searchFilters.department" class="toolbar-select">
            <option value="">All Departments</option>
            <option v-for="dept in departments" :key="dept.id" :value="dept.name">
              {{ dept.name }}
            </option>
          </select>
        </div>
        <div class="toolbar-actions">
          <button @click="searchDoctors" class="btn-primary">Search</button>
          <button @click="resetSearch" class="btn-secondary">Reset</button>
        </div>
      </div>

      <div class="table-wrap">
          <table class="data-table">
              <thead>
                  <tr>
                      <th>ID</th>
                      <th>Name</th>
                      <th>Email</th>
                      <th>Phone</th>
                      <th>Specialization</th>
                      <th>Department</th>
                      <th>Availability</th>
                  </tr>
              </thead>
              <tbody>
                  <tr v-if="loadingDoctors"><td colspan="7" class="loading-text">Loading doctors...</td></tr>
                  <tr v-else-if="doctors.length === 0">
                      <td colspan="7" class="empty-state">No doctors found</td>
                  </tr>
                  <template v-else>
                      <tr v-for="doctor in doctors" :key="doctor.id">
                          <td>{{ doctor.id }}</td>
                          <td>{{ doctor.name }}</td>
                          <td>{{ doctor.email }}</td>
                          <td>{{ doctor.phone_number }}</td>
                          <td>{{ doctor.specialty }}</td>
                            <td>{{ doctor.department }}</td>
                          <td>
                              <button class="action-btn action-unblock" @click="openAvailabilityModal(doctor)">Check Availability</button>
                          </td>
                      </tr>
                  </template>
              </tbody>
          </table>
      </div>

      <div v-if="showAvailabilityModal" class="modal-overlay doctors-modal">
      <div class="modal-card modal-content">
          <div class="modal-top">
          <h3>Doctor Availability - {{ selectedDoctor.name }}</h3>
          <button @click="closeAvailabilityModal" class="close-btn">×</button>
          </div>

          <div v-if="loadingAvailability" class="loading-text">Loading availability...</div>

          <table v-else class="data-table">
          <thead>
              <tr>
              <th>Date</th>
              <th>Day</th>
              <th>Morning</th>
              <th>Afternoon</th>
              <th>Evening</th>
              </tr>
          </thead>
          <tbody>
              <tr v-for="row in availabilityRows" :key="`${row.date}-${row.day}`">
              <td>{{ row.date }}</td>
              <td>{{ row.day }}</td>
              <td>
                  <button
                  type="button"
                  class="slot-toggle-btn"
                  :class="slotButtonClass(row.day, 'morning', row.morning)"
                  :disabled="!row.morning"
                  @click="selectSlot(row.date, row.isoDate, row.day, 'morning', row.morning)"
                  >
                  {{ row.morning ? 'Available' : 'Unavailable' }}
                  </button>
              </td>
              <td>
                  <button
                  type="button"
                  class="slot-toggle-btn"
                  :class="slotButtonClass(row.day, 'afternoon', row.afternoon)"
                  :disabled="!row.afternoon"
                  @click="selectSlot(row.date, row.isoDate, row.day, 'afternoon', row.afternoon)"
                  >
                  {{ row.afternoon ? 'Available' : 'Unavailable' }}
                  </button>
              </td>
              <td>
                  <button
                  type="button"
                  class="slot-toggle-btn"
                  :class="slotButtonClass(row.day, 'evening', row.evening)"
                  :disabled="!row.evening"
                  @click="selectSlot(row.date, row.isoDate, row.day, 'evening', row.evening)"
                  >
                  {{ row.evening ? 'Available' : 'Unavailable' }}
                  </button>
              </td>
              </tr>
          </tbody>
          </table>

          <p class="detail-text" v-if="selectedSlot">
          Selected: {{ selectedSlot.date }} ({{ selectedSlot.day }}) - {{ selectedSlot.slot }}
          </p>

          <div class="availability-actions">
          <button class="btn-primary" :disabled="!selectedSlot || booking" @click="bookSelectedSlot">
              {{ booking ? 'Booking...' : 'Book' }}
          </button>
          <button class="btn-secondary" :disabled="booking" @click="closeAvailabilityModal">Cancel</button>
          </div>
      </div>
      </div>
  </div>
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import api from '@/utils/api';

const initialSelectedDoctor = () => ({ id: null, name: '' });
const initialSearchFilters = () => ({ name: '', department: '' });

const doctors = ref([]);
const departments = ref([]);
const loadingDoctors = ref(false);
const showAvailabilityModal = ref(false);
const selectedDoctor = ref(initialSelectedDoctor());
const selectedAvailability = ref({});
const selectedSlot = ref(null);
const loadingAvailability = ref(false);
const booking = ref(false);
const searchFilters = ref(initialSearchFilters());

const rollingWeek = computed(() => {
  const today = new Date();
  const rows = [];

  for (let offset = 0; offset < 7; offset += 1) {
    const dateObj = new Date(today);
    dateObj.setDate(today.getDate() + offset);

    rows.push({
      date: dateObj.toLocaleDateString('en-GB', {
        day: '2-digit',
        month: 'short',
        year: 'numeric',
      }),
      isoDate: dateObj.toISOString().slice(0, 10),
      day: dateObj.toLocaleDateString('en-US', { weekday: 'long' }),
    });
  }

  return rows;
});

const availabilityRows = computed(() => {
  const availability = selectedAvailability.value || {};

  return rollingWeek.value.map((entry) => ({
    date: entry.date,
    isoDate: entry.isoDate,
    day: entry.day,
    morning: Boolean(availability[entry.day]?.morning),
    afternoon: Boolean(availability[entry.day]?.afternoon),
    evening: Boolean(availability[entry.day]?.evening),
  }));
});

const openAvailabilityModal = async (doctor) => {
  loadingAvailability.value = true;
  selectedDoctor.value = { id: doctor.id, name: doctor.name || 'Doctor' };
  selectedSlot.value = null;
  showAvailabilityModal.value = true;

  try {
    const response = await api.get(`/doctors/${doctor.id}/availability`);
    const availability = response?.data?.availability && typeof response.data.availability === 'object'
      ? response.data.availability
      : {};
    selectedAvailability.value = availability;
  } catch (error) {
    selectedAvailability.value = {};
    alert('Failed to load availability: ' + (error?.message || ''));
  } finally {
    loadingAvailability.value = false;
  }
};

const closeAvailabilityModal = () => {
  showAvailabilityModal.value = false;
  selectedDoctor.value = initialSelectedDoctor();
  selectedSlot.value = null;
  selectedAvailability.value = {};
};

const selectSlot = (date, isoDate, day, slot, isAvailable) => {
  if (!isAvailable) return;
  selectedSlot.value = { date, isoDate, day, slot };
};

const slotButtonClass = (day, slot, isAvailable) => {
  if (!isAvailable) return 'slot-toggle-off';

  const isSelected =
    selectedSlot.value &&
    selectedSlot.value.day === day &&
    selectedSlot.value.slot === slot;

  return isSelected ? 'slot-selected' : 'slot-toggle-on';
};

const bookSelectedSlot = async () => {
  if (!selectedSlot.value || !selectedDoctor.value.id) return;

  booking.value = true;
  try {
    const response = await api.post('/appointments', {
      doctor_id: selectedDoctor.value.id,
      date: selectedSlot.value.isoDate,
      slot: selectedSlot.value.slot,
    });
    alert(response.message);
    closeAvailabilityModal();
    window.location.href = '/patient_dashboard/home';
  } catch (error) {
    alert('Failed to book appointment: ' + (error?.message || ''));
  } finally {
    booking.value = false;
  }
};

const loadDoctors = async () => {
  loadingDoctors.value = true;
  try {
    const response = await api.get('/doctors');
    doctors.value = Array.isArray(response?.data) ? response.data : [];
  } catch (error) {
    alert('Failed to load doctors: ' + (error?.message || ''));
    doctors.value = [];
  } finally {
    loadingDoctors.value = false;
  }
};

const loadDepartments = async () => {
  try {
    const response = await api.get('/departments');
    departments.value = Array.isArray(response?.data) ? response.data : [];
  } catch (error) {
    departments.value = [];
    alert('Failed to load departments: ' + (error?.message || ''));
  }
};

const searchDoctors = async () => {
  const name = searchFilters.value.name.trim();
  const department = searchFilters.value.department.trim();

  if (!name && !department) {
    await loadDoctors();
    return;
  }

  const params = new URLSearchParams();
  if (name) params.append('name', name);
  if (department) params.append('department', department);

  loadingDoctors.value = true;
  try {
    const response = await api.get(`/doctors/search?${params.toString()}`);
    doctors.value = Array.isArray(response?.data) ? response.data : [];
  } catch (error) {
    doctors.value = [];
    alert('Failed to search doctors: ' + (error?.message || ''));
  } finally {
    loadingDoctors.value = false;
  }
};

const resetSearch = async () => {
  searchFilters.value = initialSearchFilters();
  await loadDoctors();
};

onMounted(async () => {
    await loadDoctors();
    await loadDepartments();
});

</script>