<template>
  <div class="user-page">
    <div class="page-header">
      <h2 class="page-title">Doctors Management</h2>
      <button @click="showAddForm = true" class="btn-add">+ Add Doctor</button>
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

    <div v-if="showEditForm" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-top">
          <h3>Edit Doctor</h3>
          <button @click="closeEditModal" class="close-btn">×</button>
        </div>

        <form @submit.prevent="updateDoctor" class="form-stack">
          <div class="form-group">
            <label for="edit-name">Name</label>
            <input id="edit-name" v-model="editDoctorData.name" type="text" placeholder="Doctor Name" required />
          </div>

          <div class="form-group">
            <label for="edit-email">Email</label>
            <input id="edit-email" v-model="editDoctorData.email" type="email" placeholder="Email" disabled required />
          </div>

          <div class="form-group">
            <label for="edit-password">Password (optional)</label>
            <input id="edit-password" v-model="editDoctorData.password" type="password" placeholder="Leave blank to keep current password" />
          </div>

          <div class="form-group">
            <label for="edit-phone">Phone</label>
            <input id="edit-phone" v-model="editDoctorData.phone_number" type="tel" placeholder="Phone Number" required />
          </div>

          <div class="form-group">
            <label for="edit-specialization">Specialization</label>
            <input id="edit-specialization" v-model="editDoctorData.specialty" type="text" placeholder="Specialization" required />
          </div>

          <div class="form-group">
            <label for="edit-department">Department</label>
            <select id="edit-department" v-model="editDoctorData.department_id" required>
              <option value="">Select Department</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary">Update Doctor</button>
            <button type="button" @click="closeEditModal" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Add Doctor Form Modal -->
    <div v-if="showAddForm" class="modal-overlay">
      <div class="modal-card">
        <div class="modal-top">
          <h3>Add New Doctor</h3>
          <button @click="showAddForm = false" class="close-btn">×</button>
        </div>
        
        <form @submit.prevent="addDoctor" class="form-stack">
          <div class="form-group">
            <label for="name">Name</label>
            <input id="name" v-model="newDoctor.name" type="text" placeholder="Doctor Name" required />
          </div>

          <div class="form-group">
            <label for="email">Email</label>
            <input id="email" v-model="newDoctor.email" type="email" placeholder="Email" required />
          </div>

          <div class="form-group">
            <label for="password">Password</label>
            <input id="password" v-model="newDoctor.password" type="password" placeholder="Password" required />
          </div>

          <div class="form-group">
            <label for="phone">Phone</label>
            <input id="phone" v-model="newDoctor.phone_number" type="tel" placeholder="Phone Number" required />
          </div>

          <div class="form-group">
            <label for="specialization">Specialization</label>
            <input id="specialization" v-model="newDoctor.specialty" type="text" placeholder="Specialization" required />
          </div>

          <div class="form-group">
            <label for="department">Department</label>
            <select id="department" v-model="newDoctor.department_id" required>
              <option value="">Select Department</option>
              <option v-for="dept in departments" :key="dept.id" :value="dept.id">
                {{ dept.name }}
              </option>
            </select>
          </div>

          <div class="form-actions">
            <button type="submit" class="btn-primary">Add Doctor</button>
            <button type="button" @click="showAddForm = false" class="btn-secondary">Cancel</button>
          </div>
        </form>
      </div>
    </div>

    <!-- Doctors Table -->
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
            <th>Status</th>
            <th>Actions</th>
          </tr>
        </thead>
        <tbody>
          <tr v-if="loadingDoctors"><td colspan="9" class="loading-text">Loading doctors...</td></tr>
          <template v-else>
            <tr v-if="doctors.length === 0">
              <td colspan="9" class="empty-state">No doctors found</td>
            </tr>
            <tr v-for="doctor in doctors" :key="doctor.id">
              <td>{{ doctor.id }}</td>
              <td>{{ doctor.name }}</td>
              <td>{{ doctor.email }}</td>
              <td>{{ doctor.phone_number }}</td>
              <td>{{ doctor.specialty }}</td>
              <td>{{ doctor.department }}</td>
              <td>
                <button @click="viewDoctorAvailability(doctor)" class="action-btn action-view">View</button>
              </td>
              <td>
                <span class="status" :class="statusClass(doctor)">{{ statusLabel(doctor) }}</span>
              </td>
              <td>
                <button @click="editDoctor(doctor)" class="action-btn action-edit">Edit</button>
                <button
                  @click="toggleDoctorStatus(doctor)"
                  class="action-btn"
                  :class="doctor.active ? 'action-block' : 'action-unblock'"
                >
                  {{ doctor.active ? 'Block' : 'Unblock' }}
                </button>
                <button @click="deleteDoctor(doctor.id)" class="action-btn action-delete">Delete</button>
              </td>
            </tr>
          </template>
        </tbody>
      </table>
    </div>

    <div v-if="showAvailabilityModal" class="modal-overlay doctors-modal">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>Availability - {{ selectedDoctorName }}</h3>
          <div class="modal-actions">
            <button @click="openEditAvailabilityModal" class="action-btn action-edit" :disabled="loadingAvailability">Edit</button>
            <button @click="closeAvailabilityModal" class="close-btn">×</button>
          </div>
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
            <tr v-if="availabilityRows.length === 0">
              <td colspan="5" class="empty-state">No availability found</td>
            </tr>
            <tr v-for="row in availabilityRows" :key="row.day">
              <td>{{ row.date }}</td>
              <td>{{ row.day }}</td>
              <td><span :class="['slot-badge', row.morning ? 'slot-on' : 'slot-off']">{{ row.morning ? 'Available' : 'Unavailable' }}</span></td>
              <td><span :class="['slot-badge', row.afternoon ? 'slot-on' : 'slot-off']">{{ row.afternoon ? 'Available' : 'Unavailable' }}</span></td>
              <td><span :class="['slot-badge', row.evening ? 'slot-on' : 'slot-off']">{{ row.evening ? 'Available' : 'Unavailable' }}</span></td>
            </tr>
          </tbody>
        </table>
      </div>
    </div>

    <div v-if="showEditAvailabilityModal" class="modal-overlay doctors-modal">
      <div class="modal-card modal-content">
        <div class="modal-top">
          <h3>Edit Availability - {{ selectedDoctorName }}</h3>
        </div>

        <table class="data-table">
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
            <tr v-for="row in editableAvailabilityRows" :key="`edit-${row.date}-${row.day}`">
              <td>{{ row.date }}</td>
              <td>{{ row.day }}</td>
              <td>
                <button
                  type="button"
                  class="slot-toggle-btn"
                  :class="editableAvailability[row.day]?.morning ? 'slot-toggle-on' : 'slot-toggle-off'"
                  @click="toggleAvailabilitySlot(row.day, 'morning')"
                >
                  {{ editableAvailability[row.day]?.morning ? 'Available' : 'Unavailable' }}
                </button>
              </td>
              <td>
                <button
                  type="button"
                  class="slot-toggle-btn"
                  :class="editableAvailability[row.day]?.afternoon ? 'slot-toggle-on' : 'slot-toggle-off'"
                  @click="toggleAvailabilitySlot(row.day, 'afternoon')"
                >
                  {{ editableAvailability[row.day]?.afternoon ? 'Available' : 'Unavailable' }}
                </button>
              </td>
              <td>
                <button
                  type="button"
                  class="slot-toggle-btn"
                  :class="editableAvailability[row.day]?.evening ? 'slot-toggle-on' : 'slot-toggle-off'"
                  @click="toggleAvailabilitySlot(row.day, 'evening')"
                >
                  {{ editableAvailability[row.day]?.evening ? 'Available' : 'Unavailable' }}
                </button>
              </td>
            </tr>
          </tbody>
        </table>

        <div class="availability-actions">
          <button type="button" class="btn-primary" @click="updateAvailability" :disabled="updatingAvailability">
            {{ updatingAvailability ? 'Updating...' : 'Update' }}
          </button>
          <button type="button" class="btn-secondary" @click="closeEditAvailabilityModal" :disabled="updatingAvailability">
            Cancel
          </button>
        </div>
      </div>
    </div>
  </div>
</template>

<script setup>
import { computed, ref, onMounted } from 'vue';
import api from '@/utils/api';

const initialSearchFilters = () => ({
  name: '',
  department: '',
});

const initialNewDoctor = () => ({
  name: '',
  email: '',
  phone_number: '',
  specialty: '',
  department_id: '',
  password: '',
});

const initialEditDoctor = () => ({
  id: null,
  name: '',
  email: '',
  phone_number: '',
  specialty: '',
  department_id: '',
  password: '',
});

const doctors = ref([]);
const departments = ref([]);
const showAddForm = ref(false);
const showEditForm = ref(false);
const showAvailabilityModal = ref(false);
const showEditAvailabilityModal = ref(false);
const loadingDoctors = ref(false);
const loadingAvailability = ref(false);
const updatingAvailability = ref(false);
const selectedDoctorId = ref(null);
const selectedDoctorName = ref('');
const selectedAvailability = ref({});
const editableAvailability = ref({});
const searchFilters = ref(initialSearchFilters());
const newDoctor = ref(initialNewDoctor());
const editDoctorData = ref(initialEditDoctor());

const getRollingWeek = () => {
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
      day: dateObj.toLocaleDateString('en-US', { weekday: 'long' }),
    });
  }

  return rows;
};

const rollingWeek = computed(() => getRollingWeek());

const availabilityRows = computed(() => {
  const availability = selectedAvailability.value || {};

  return rollingWeek.value.map((entry) => ({
    date: entry.date,
    day: entry.day,
    morning: Boolean(availability[entry.day]?.morning),
    afternoon: Boolean(availability[entry.day]?.afternoon),
    evening: Boolean(availability[entry.day]?.evening),
  }));
});

const editableAvailabilityRows = computed(() => {
  const availability = editableAvailability.value || {};

  return rollingWeek.value.map((entry) => ({
    date: entry.date,
    day: entry.day,
    morning: Boolean(availability[entry.day]?.morning),
    afternoon: Boolean(availability[entry.day]?.afternoon),
    evening: Boolean(availability[entry.day]?.evening),
  }));
});


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
    alert('Failed to load departments: ' + (error?.message || ''));
    departments.value = [];
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

  try {
    const response = await api.get(`/doctors/search?${params.toString()}`);
    doctors.value = Array.isArray(response?.data) ? response.data : [];
  } catch (error) {
    doctors.value = [];
    alert('Failed to search doctors: ' + (error?.message || ''));
  }
};

const resetSearch = async () => {
  searchFilters.value = initialSearchFilters();
  await loadDoctors();
};

const addDoctor = async () => {
  try {
    await api.post('/doctors', newDoctor.value);
    await searchDoctors();
    showAddForm.value = false;
    newDoctor.value = initialNewDoctor();
  } catch (error) {
    alert('Failed to add doctor: ' + (error?.message || ''));
  }
};

const editDoctor = (doctor) => {
  const selectedDepartment = departments.value.find((dept) => dept.name === doctor.department);
  
  editDoctorData.value = {
    id: doctor.id,
    name: doctor.name || '',
    email: doctor.email || '',
    phone_number: doctor.phone_number || '',
    specialty: doctor.specialty || '',
    department_id: selectedDepartment ? selectedDepartment.id : '',
    password: '',
  };

  showEditForm.value = true;
};

const closeEditModal = () => {
  showEditForm.value = false;
  editDoctorData.value = initialEditDoctor();
};

const updateDoctor = async () => {
  const payload = {
    name: editDoctorData.value.name,
    email: editDoctorData.value.email,
    phone_number: editDoctorData.value.phone_number,
    specialty: editDoctorData.value.specialty,
    department_id: editDoctorData.value.department_id,
  };

  if (editDoctorData.value.password && editDoctorData.value.password.trim()) {
    payload.password = editDoctorData.value.password;
  }

  try {
    await api.put(`/doctors/${editDoctorData.value.id}`, payload);
    closeEditModal();
    await searchDoctors();
  } catch (error) {
    alert('Failed to update doctor: ' + (error?.message || ''));
  }
};

const deleteDoctor = async (doctorId) => {
  if (confirm('Are you sure you want to delete this doctor?')) {
    try {
      await api.delete(`/doctors/${doctorId}`);
      await searchDoctors();
    } catch (error) {
      alert('Failed to delete doctor: ' + (error?.message || ''));
    }
  }
};

const viewDoctorAvailability = async (doctor) => {
  loadingAvailability.value = true;
  selectedDoctorId.value = doctor.id;
  selectedDoctorName.value = doctor.name || 'Doctor';
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

const openEditAvailabilityModal = () => {
  editableAvailability.value = JSON.parse(JSON.stringify(selectedAvailability.value || {}));
  showEditAvailabilityModal.value = true;
};

const closeEditAvailabilityModal = () => {
  showEditAvailabilityModal.value = false;
  editableAvailability.value = {};
};

const toggleAvailabilitySlot = (day, slot) => {
  if (!editableAvailability.value[day]) {
    editableAvailability.value[day] = { morning: false, afternoon: false, evening: false };
  }
  editableAvailability.value[day][slot] = !editableAvailability.value[day][slot];
};

const updateAvailability = async () => {
  updatingAvailability.value = true;
  try {
    await api.put(`/doctors/${selectedDoctorId.value}/availability`, editableAvailability.value);
    selectedAvailability.value = JSON.parse(JSON.stringify(editableAvailability.value));
    closeEditAvailabilityModal();
  } catch (error) {
    alert('Failed to update availability: ' + (error?.message || ''));
  } finally {
    updatingAvailability.value = false;
  }
};

const closeAvailabilityModal = () => {
  showAvailabilityModal.value = false;
  showEditAvailabilityModal.value = false;
  selectedDoctorId.value = null;
  selectedDoctorName.value = '';
  selectedAvailability.value = {};
  editableAvailability.value = {};
};

const toggleDoctorStatus = async (doctor) => {
  const nextActive = !doctor.active;
  const actionLabel = nextActive ? 'unblock' : 'block';

  if (!confirm(`Are you sure you want to ${actionLabel} ${doctor.name}?`)) return;

  try {
    await api.patch(`/doctors/${doctor.id}`, {
      active: nextActive,
    });
    await searchDoctors();
  } catch (error) {
    alert(`Failed to ${actionLabel} doctor: ` + (error?.message || ''));
  }
};

const statusLabel = (doctor) => {
  if (doctor.active === true) return 'Active';
  if (doctor.active === false) return 'Blocked';
  return 'Unknown';
};

const statusClass = (doctor) => {
  if (doctor.active === true) return 'active';
  if (doctor.active === false) return 'blocked';
  return 'unknown';
};

onMounted(async () => {
  await loadDoctors();
  await loadDepartments();
});
</script>
