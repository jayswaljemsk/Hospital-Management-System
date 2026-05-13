<template>
  <div class="user-page">
    <div v-if="!showEditAvailability">
        <div class="page-header">
            <h2 class="page-title">Doctor Availability</h2>
            <button class="action-btn action-edit" @click="openEditAvailability" :disabled="loadingAvailability">Edit Availability</button>
        </div>

        <div class="table-wrap">    
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
                <tr v-if="loadingAvailability"><td colspan="5" class="loading-text">Loading availability...</td></tr>
                <tr v-else-if="availabilityRows.length === 0">
                    <td colspan="5" class="empty-state">No availability found</td>
                </tr>
                <template v-else>
                    <tr v-for="row in availabilityRows" :key="row.day">
                    <td>{{ row.date }}</td>
                    <td>{{ row.day }}</td>
                    <td><span :class="['slot-badge', row.morning ? 'slot-on' : 'slot-off']">{{ row.morning ? 'Available' : 'Unavailable' }}</span></td>
                    <td><span :class="['slot-badge', row.afternoon ? 'slot-on' : 'slot-off']">{{ row.afternoon ? 'Available' : 'Unavailable' }}</span></td>
                    <td><span :class="['slot-badge', row.evening ? 'slot-on' : 'slot-off']">{{ row.evening ? 'Available' : 'Unavailable' }}</span></td>
                    </tr>
                </template>
                </tbody>
            </table>
        </div>
    </div>
    <div v-else>
      <!-- <div class="modal-card modal-content"> -->
        <div class="modal-top">
          <h2 class="page-title">Edit Availability: </h2>
        </div>
        <div class="table-wrap">
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
          <button type="button" class="btn-secondary" @click="closeEditAvailability" :disabled="updatingAvailability">
            Cancel
          </button>
        </div>
      </div>
      </div>
    </div>
  <!-- </div> -->
</template>

<script setup>
import { computed, onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import api from '@/utils/api';

const store = useStore();
const doctorId = store.state.userId || localStorage.getItem('user_id');

const cloneAvailability = (value = {}) => JSON.parse(JSON.stringify(value));

const selectedAvailability = ref({});
const editableAvailability = ref({});

const loadingAvailability = ref(false);
const showEditAvailability = ref(false);
const updatingAvailability = ref(false);

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

const loadAvailability = async () => {
  if (!doctorId) return;

  loadingAvailability.value = true;
  try {
    const response = await api.get(`/doctors/${doctorId}/availability`);
    const availability = response?.data?.availability && typeof response.data.availability === 'object'
      ? response.data.availability
      : {};

    selectedAvailability.value = availability;
  } catch (error) {
    alert('Failed to load availability: ' + (error?.message || ''));
    selectedAvailability.value = {};
  } finally {
    loadingAvailability.value = false;
  }
};

const openEditAvailability = () => {
  editableAvailability.value = cloneAvailability(selectedAvailability.value || {});
  showEditAvailability.value = true;
};

const closeEditAvailability = () => {
  showEditAvailability.value = false;
  editableAvailability.value = {};
};

const toggleAvailabilitySlot = (day, slot) => {
  if (!editableAvailability.value[day]) {
    editableAvailability.value[day] = { morning: false, afternoon: false, evening: false };
  }
  editableAvailability.value[day][slot] = !editableAvailability.value[day][slot];
};

const updateAvailability = async () => {
  if (!doctorId) return;

  updatingAvailability.value = true;
  try {
    await api.put(`/doctors/${doctorId}/availability`, editableAvailability.value);
    selectedAvailability.value = cloneAvailability(editableAvailability.value);
    closeEditAvailability();
  } catch (error) {
    alert('Failed to update availability: ' + (error?.message || ''));
  } finally {
    updatingAvailability.value = false;
  }
};

onMounted(async () => {
  await loadAvailability();
});
</script>