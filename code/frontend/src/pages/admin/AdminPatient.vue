<template>
	<div class="user-page">
		<div class="page-header">
			<h2 class="page-title">Patients Management</h2>
		</div>
		<div class="toolbar">
			<div class="toolbar-fields">
				<input
					v-model="searchFilters.id"
					type="text"
					inputmode="numeric"
					class="toolbar-input"
					placeholder="Search by patient ID"
					@keyup.enter="searchPatients"
				/>
			</div>
			<div class="toolbar-fields">
				<input
					v-model="searchFilters.name"
					type="text"
					class="toolbar-input"
					placeholder="Search by patient name"
					@keyup.enter="searchPatients"
				/>
			</div>
			<div class="toolbar-actions">
				<button @click="searchPatients" class="btn-primary">Search</button>
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
						<th>Gender</th>
						<th>Phone</th>
                        <th>Address</th>
                        <th>History</th>
                        <th>Status</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					<tr v-if="loadingPatients"><td colspan="9" class="loading-text">Loading patients...</td></tr>
					<tr v-else-if="patients.length === 0">
						<td colspan="9" class="empty-state">No patients found</td>
					</tr>
					<template v-else>
						<tr v-for="patient in patients" :key="patient.user_id">
							<td>{{ patient.user_id }}</td>
							<td>{{ patient.name }}</td>
							<td>{{ patient.email }}</td>
							<td>{{ patient.gender || '-' }}</td>
							<td>{{ patient.phone_number || '-' }}</td>
                        <td>{{ patient.address || '-' }}</td>
                        <td>
                            <button @click="openHistoryModal(patient)" class="action-btn action-view">View</button>
                        </td>
                        <td>
                            <span class="status" :class="statusClass(patient)">{{ statusLabel(patient) }}</span>
                        </td>
							<td>
								<button @click="openEditModal(patient)" class="action-btn action-edit">Edit</button>
								<button
									@click="togglePatientStatus(patient)"
									class="action-btn"
									:class="patient.active ? 'action-block' : 'action-unblock'"
								>
									{{ patient.active ? 'Block' : 'Unblock' }}
								</button>
								<button @click="deletePatient(patient.user_id)" class="action-btn action-delete">Delete</button>
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
							<td colspan="8" class="empty-state">No treatment history found</td>
						</tr>
						<tr v-for="(entry, index) in selectedPatientHistory" :key="`history-${index}`">
							<td>{{ entry.id || '-' }}</td>
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

		<div v-if="showEditForm" class="modal-overlay">
			<div class="modal-card">
				<div class="modal-top">
					<h3>Edit Patient</h3>
					<button @click="closeEditModal" class="close-btn">×</button>
				</div>

				<form @submit.prevent="updatePatient" class="form-stack">
					<div class="form-group">
						<label for="patient-name">Name</label>
						<input id="patient-name" v-model="editPatient.name" type="text" required />
					</div>

					<div class="form-group">
						<label for="patient-email">Email</label>
						<input id="patient-email" v-model="editPatient.email" type="email" required />
					</div>

                    <div class="form-group">
                        <label for="patient-password">Password</label>
                        <input id="patient-password" v-model="editPatient.password" type="password" />
                    </div>

					<div class="form-group">
						<label for="patient-gender">Gender</label>
						<select id="patient-gender" v-model="editPatient.gender">
							<option value="">Select Gender</option>
							<option value="Male">Male</option>
							<option value="Female">Female</option>
							<option value="Other">Other</option>
						</select>
					</div>

					<div class="form-group">
						<label for="patient-phone">Phone Number</label>
						<input id="patient-phone" v-model="editPatient.phone_number" type="text" />
					</div>

					<div class="form-group">
						<label for="patient-address">Address</label>
						<input id="patient-address" v-model="editPatient.address" type="text" />
					</div>

					<div class="form-actions">
						<button type="submit" class="btn-primary">Update</button>
						<button type="button" @click="closeEditModal" class="btn-secondary">Cancel</button>
					</div>
				</form>
			</div>
		</div>
	</div>
</template>

<script setup>
import { ref, onMounted } from 'vue';
import api from '@/utils/api';

const initialSearchFilters = () => ({
	id: '',
	name: '',
});

const initialEditPatient = () => ({
	user_id: null,
	name: '',
	email: '',
	gender: '',
	phone_number: '',
	address: '',
	password: '',
});

const patients = ref([]);
const loadingPatients = ref(false);
const showEditForm = ref(false);
const showHistoryModal = ref(false);
const selectedPatientName = ref('');
const selectedPatientHistory = ref([]);

const searchFilters = ref(initialSearchFilters());
const editPatient = ref(initialEditPatient());

const loadPatients = async () => {
	loadingPatients.value = true;
	try {
		const response = await api.get('/patients');
		patients.value = Array.isArray(response?.data) ? response.data : [];
	} catch (error) {
		alert('Failed to load patients: ' + (error?.message || ''));
		patients.value = [];
	} finally {
		loadingPatients.value = false;
	}
};


const searchPatients = async () => {
	const id = searchFilters.value.id.trim();
	const name = searchFilters.value.name.trim();

	if (!id && !name) {
		await loadPatients();
		return;
	}

	const params = new URLSearchParams();
	if (id) params.append('id', id);
	if (name) params.append('name', name);

	loadingPatients.value = true;
	try {
		const response = await api.get(`/patients/search?${params.toString()}`);
		patients.value = Array.isArray(response?.data) ? response.data : [];
	} catch (error) {
		alert('Failed to search patients: ' + (error?.message || ''));
		patients.value = [];
	} finally {
		loadingPatients.value = false;
	}
};

const resetSearch = async () => {
	searchFilters.value = initialSearchFilters();
	await loadPatients();
};

const openEditModal = (patient) => {
	editPatient.value = {
		user_id: patient.user_id,
		name: patient.name || '',
		email: patient.email || '',
		gender: patient.gender || '',
		phone_number: patient.phone_number || '',
		address: patient.address || '',
		password: '',
	};
	showEditForm.value = true;
};

const openHistoryModal = (patient) => {
	selectedPatientName.value = patient.name || 'Patient';
	selectedPatientHistory.value = patient.history || [];
	showHistoryModal.value = true;
};

const closeHistoryModal = () => {
	showHistoryModal.value = false;
	selectedPatientName.value = '';
	selectedPatientHistory.value = [];
};

const closeEditModal = () => {
	showEditForm.value = false;
	editPatient.value = initialEditPatient();
};

const updatePatient = async () => {
	const payload = {
		name: editPatient.value.name,
		email: editPatient.value.email,
		gender: editPatient.value.gender,
		phone_number: editPatient.value.phone_number,
		address: editPatient.value.address,
	};

	if (editPatient.value.password && editPatient.value.password.trim()) {
		payload.password = editPatient.value.password;
	}

	try {
		await api.put(`/patients/${editPatient.value.user_id}`, payload);
		closeEditModal();
		await loadPatients();
	} catch (error) {
		alert('Failed to update patient: ' + (error?.message || ''));
	}
};

const deletePatient = async (userId) => {
	if (!confirm('Are you sure you want to delete this patient?')) return;

	try {
		await api.delete(`/patients/${userId}`);
		await loadPatients();
	} catch (error) {
		alert('Failed to delete patient: ' + (error?.message || ''));
	}
};

const togglePatientStatus = async (patient) => {
	const nextActive = !patient.active;
	const actionLabel = nextActive ? 'unblock' : 'block';

	if (!confirm(`Are you sure you want to ${actionLabel} ${patient.name}?`)) return;

	try {
		await api.put(`/patients/${patient.user_id}`, {
			active: nextActive,
		});
		await loadPatients();
	} catch (error) {
		alert(`Failed to ${actionLabel} patient: ` + (error?.message || ''));
	}
};

const statusLabel = (patient) => {
    if (patient.active === true) return 'Active';
    if (patient.active === false) return 'Blocked';
    return 'Unknown';
};

const statusClass = (patient) => {
    if (patient.active === true) return 'active';
    if (patient.active === false) return 'blocked';
    return 'unknown';
}

onMounted(async () => {
	await loadPatients();
});
</script>
