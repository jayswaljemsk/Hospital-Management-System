<template>
	<div class="user-page">
		<div class="page-header">
			<h2 class="page-title">Departments Management</h2>
			<button @click="showForm = true" class="btn-add">+ Add Department</button>
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

		<div v-if="showForm" class="modal-overlay">
			<div class="modal-card">
				<div class="modal-top">
					<h3>Add New Department</h3>
					<button @click="showForm = false" class="close-btn">×</button>
				</div>

				<form @submit.prevent="addDepartment" class="form-stack">
					<div class="form-group">
						<label for="edit-name">Department Name</label>
						<input id="edit-name" v-model="newDepartment.name" type="text" placeholder="Department Name" required />
					</div>

					<div class="form-group">
						<label for="description">Description</label>
						<input
							id="description"
							v-model="newDepartment.description"
							rows="3"
							placeholder="Department Description"
						></input>
					</div>

					<div class="form-actions">
						<button type="submit" class="btn-primary">Create Department</button>
						<button type="button" @click="showForm = false" class="btn-secondary">Cancel</button>
					</div>
				</form>
			</div>
		</div>

		<div class="table-wrap">
			<table class="data-table">
				<thead>
					<tr>
						<th>ID</th>
						<th>Name</th>
						<th>Description</th>
						<th>Doctors Count</th>
						<th>Actions</th>
					</tr>
				</thead>
				<tbody>
					<tr v-if="loadingDepartments"><td colspan="5" class="loading-text">Loading departments...</td></tr>
					<tr v-else-if="departments.length === 0">
						<td colspan="5" class="empty-state">No departments found</td>
					</tr>
					<template v-else>
						<tr v-for="department in departments" :key="department.id">
							<td>
								<button class="link-btn" @click="openDoctorsModal(department.id)">
									{{ department.id }}
								</button>
							</td>
							<td>{{ department.name }}</td>
							<td>{{ department.description || '-' }}</td>
							<td>{{ Array.isArray(department.doctors) ? department.doctors.length : 0 }}</td>
							<td>
								<button @click="editDepartment(department)" class="action-btn action-edit">Edit</button>
								<button @click="deleteDepartment(department.id)" class="action-btn action-delete">Delete</button>
							</td>
						</tr>
					</template>
				</tbody>
			</table>
		</div>

		<div v-if="selectedDepartment" class="modal-overlay doctors-modal">
			<div class="modal-card modal-content">
				<div class="modal-top">
					<h3>
						Doctors in {{ selectedDepartment.name }} (ID: {{ selectedDepartment.id }})
					</h3>
					<button @click="closeDoctorsOverlay" class="close-btn">×</button>
				</div>

				<div v-if="loadingDoctors" class="loading-text">Loading doctors...</div>

				<table v-else class="data-table">
					<thead>
						<tr>
							<th>Doctor ID</th>
							<th>Doctor Name</th>
						</tr>
					</thead>
					<tbody>
						<tr v-if="selectedDoctors.length === 0">
							<td colspan="2" class="empty-state">No doctors in this department</td>
						</tr>
						<tr v-for="doc in selectedDoctors" :key="doc.id">
							<td>{{ doc.id }}</td>
							<td>{{ doc.name }}</td>
						</tr>
					</tbody>
				</table>
			</div>
		</div>

		<div v-if="showEditForm" class="modal-overlay">
			<div class="modal-card">
				<div class="modal-top">
					<h3>Edit Department</h3>
					<button @click="closeEditModal" class="close-btn">×</button>
				</div>
				<form @submit.prevent="updateDepartment" class="form-stack">
					<div class="form-group">
						<label for="name">Name</label>
						<input type="text" v-model="editDepartmentData.name" id="name" placeholder="Department Name" required />
					</div>
					<div class="form-group">
						<label for="description">Description</label>
						<input type="text" v-model="editDepartmentData.description" id="description" placeholder="Department Description" required />
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

const initialNewDepartment = () => ({
	name: '',
	description: '',
});

const initialEditDepartment = () => ({
	id: null,
	name: '',
	description: '',
});

const departments = ref([]);
const loadingDepartments = ref(false);
const showForm = ref(false);
const showEditForm = ref(false);
const loadingDoctors = ref(false);
const selectedDepartment = ref(null);
const selectedDoctors = ref([]);
const searchName = ref('');

const newDepartment = ref(initialNewDepartment());
const editDepartmentData = ref(initialEditDepartment());


const loadDepartments = async () => {
	loadingDepartments.value = true;
	try {
		const response = await api.get('/departments');
		departments.value = Array.isArray(response?.data) ? response.data : [];
	} catch (error) {
		alert('Failed to load departments: ' + (error?.message || ''));
		departments.value = [];
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
	closeDoctorsOverlay();
	searchName.value = '';
	await loadDepartments();
};
const openDoctorsModal = async (departmentId) => {
	loadingDoctors.value = true;
	try {
		const response = await api.get(`/departments/${departmentId}`);
		const dept = response?.data || null;
		selectedDepartment.value = dept;
		selectedDoctors.value = Array.isArray(dept?.doctors) ? dept.doctors : [];
	} catch (error) {
		selectedDepartment.value = null;
		selectedDoctors.value = [];
		alert('Failed to load doctors for this department: ' + (error?.message || ''));
	} finally {
		loadingDoctors.value = false;
	}
};

const closeDoctorsOverlay = () => {
	selectedDepartment.value = null;
	selectedDoctors.value = [];
};

const addDepartment = async () => {
	try {
		await api.post('/departments', newDepartment.value);
		showForm.value = false;
		newDepartment.value = initialNewDepartment();
		await loadDepartments();
	} catch (error) {
		alert('Failed to add department: ' + (error?.message || ''));
	}
};

const editDepartment = (department) => {
	showEditForm.value = true;
	editDepartmentData.value = {
		id: department.id,
		name: department.name || '',
		description: department.description || '',
	};
};

const closeEditModal = () => {
	showEditForm.value = false;
	editDepartmentData.value = initialEditDepartment();
};

const updateDepartment = async () => {
	try {
		await api.put(`/departments/${editDepartmentData.value.id}`, editDepartmentData.value);
		closeEditModal();
		await loadDepartments();
	} catch (error) {
		alert('Failed to update department: ' + (error?.message || ''));
	}
};

const deleteDepartment = async (departmentId) => {
	if (!confirm('Are you sure you want to delete this department?')) return;

	try {
		await api.delete(`/departments/${departmentId}`);
		await loadDepartments();
	} catch (error) {
		alert('Failed to delete department: ' + (error?.message || ''));
	}
};

onMounted(async () => {
	await loadDepartments();
});

</script>
