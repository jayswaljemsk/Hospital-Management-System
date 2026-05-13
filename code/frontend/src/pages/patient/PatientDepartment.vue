<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Departments</h2>
    </div>

    <div class="toolbar">
      <div class="toolbar-fields">
        <input
          v-model="searchName"
          type="text"
          class="toolbar-input"
          placeholder="Search by department name"
          @keyup.enter="searchDepartments"
        />
      </div>
      <div class="toolbar-actions">
        <button @click="searchDepartments" class="btn-primary">Search</button>
        <button @click="resetDepartmentSearch" class="btn-secondary">Reset</button>
      </div>
    </div>

    <div class="table-wrap">
      <table class="data-table">
        <thead>
          <tr>
            <th>ID</th>
            <th>Name</th>
            <th>View</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingDepartments"><td colspan="3" class="loading-text">Loading departments...</td></tr>
          <tr v-else-if="departments.length === 0">
            <td colspan="3" class="empty-state">No departments found</td>
          </tr>
          <template v-else>
            <tr v-for="department in departments" :key="department.id">
              <td>{{ department.id }}</td>
              <td>{{ department.name }}</td>
              <td>
                <button class="action-btn action-view" @click="openDepartmentModal(department)">View</button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="showDepartmentModal" class="modal-overlay doctors-modal">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>Department of {{ selectedDepartment.name }}</h3>
          <button @click="closeDepartmentModal" class="close-btn">×</button>
        </div>

        <h4 class="section-title">Description:</h4>
        <p class="detail-text">{{ selectedDepartment.description || 'No department description available.' }}</p>

        <h4 class="section-title">Doctors List</h4>
        <table class="data-table">
          <thead>
            <tr>
              <th>ID</th>
              <th>Doctor</th>
              <th>Availability</th>
              <th>View</th>
            </tr>
          </thead>
          <tbody>
            <tr v-if="departmentDoctors.length === 0">
              <td colspan="4" class="empty-state">No doctors in this department</td>
            </tr>
            <tr v-for="doctor in departmentDoctors" :key="doctor.id">
              <td>{{ doctor.id }}</td>
              <td>{{ doctor.name }}</td>
              <td>
                <button class="action-btn action-unblock" @click="openAvailabilityModal(doctor)">Check Availability</button>
              </td>
              <td>
                <button class="action-btn action-view" @click="openDoctorProfileModal(doctor)">View</button>
              </td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showDoctorProfileModal" class="modal-overlay doctors-modal">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>Doctor Profile</h3>
          <button @click="closeDoctorProfileModal" class="close-btn">×</button>
        </div>

        <div v-if="selectedDoctorProfile" class="profile-grid">
          <p><strong>ID:</strong> {{ selectedDoctorProfile.id }}</p>
          <p><strong>Name:</strong> {{ selectedDoctorProfile.name }}</p>
          <p><strong>Email:</strong> {{ selectedDoctorProfile.email }}</p>
          <p><strong>Phone:</strong> {{ selectedDoctorProfile.phone_number || '-' }}</p>
          <p><strong>Specialization:</strong> {{ selectedDoctorProfile.specialty || '-' }}</p>
          <p><strong>Department:</strong> {{ selectedDoctorProfile.department || '-' }}</p>
        </div>

        <div class="availability-actions">
          <button class="btn-primary" @click="openAvailabilityFromProfile">Check Availability</button>
          <button class="btn-secondary" @click="closeDoctorProfileModal">Cancel</button>
        </div>
      </div>
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
import { computed, ref, onMounted } from 'vue';
import api from '@/utils/api';

const initialDepartment = () => ({ id: null, name: '', description: '' });
const initialDoctor = () => ({ id: null, name: '' });

const departments = ref([]);
const loadingDepartments = ref(false);
const showDepartmentModal = ref(false);
const showDoctorProfileModal = ref(false);
const showAvailabilityModal = ref(false);
const loadingAvailability = ref(false);
const booking = ref(false);

const selectedDepartment = ref(initialDepartment());
const departmentDoctors = ref([]);
const selectedDoctor = ref(initialDoctor());
const selectedDoctorProfile = ref(null);
const selectedAvailability = ref({});
const selectedSlot = ref(null);
const searchName = ref('');

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

const loadDepartments = async () => {
  loadingDepartments.value = true;
  try {
    const response = await api.get('/departments');
    departments.value = Array.isArray(response?.data) ? response.data : [];
  } catch (error) {
    departments.value = [];
    alert('Failed to load departments: ' + (error?.message || ''));
  } finally {
    loadingDepartments.value = false;
  }
};

const searchDepartments = async () => {
  const name = searchName.value.trim();
  if (!name) {
    await loadDepartments();
    return;
  }

  loadingDepartments.value = true;
  try {
    const response = await api.get(`/departments/search?name=${encodeURIComponent(name)}`);
    departments.value = Array.isArray(response?.data) ? response.data : [];
  } catch (error) {
    departments.value = [];
    alert('Failed to search departments: ' + (error?.message || ''));
  } finally {
    loadingDepartments.value = false;
  }
};

const resetDepartmentSearch = async () => {
  closeAvailabilityModal();
  closeDoctorProfileModal();
  closeDepartmentModal();
  searchName.value = '';
  await loadDepartments();
};

const openDepartmentModal = (department) => {
  selectedDepartment.value = {
    id: department.id,
    name: department.name || 'Department',
    description: department.description || '',
  };
  departmentDoctors.value = Array.isArray(department.doctors) ? department.doctors : [];
  showDepartmentModal.value = true;
};

const closeDepartmentModal = () => {
  showDepartmentModal.value = false;
  selectedDepartment.value = initialDepartment();
  departmentDoctors.value = [];
};

const openDoctorProfileModal = async (doctor) => {
  try {
    const response = await api.get(`/doctors/${doctor.id}`);
    selectedDoctorProfile.value = response?.data || null;
    selectedDoctor.value = { id: doctor.id, name: doctor.name || 'Doctor' };
    showDoctorProfileModal.value = true;
  } catch (error) {
    alert('Failed to load doctor details: ' + (error?.message || ''));
  }
};

const closeDoctorProfileModal = () => {
  showDoctorProfileModal.value = false;
  selectedDoctorProfile.value = null;
};

const openAvailabilityFromProfile = async () => {
  if (!selectedDoctor.value.id) return;
  await openAvailabilityModal(selectedDoctor.value);
  closeDoctorProfileModal();
};

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
  selectedDoctor.value = initialDoctor();
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

onMounted( async () => {
  await loadDepartments();
});

</script>
