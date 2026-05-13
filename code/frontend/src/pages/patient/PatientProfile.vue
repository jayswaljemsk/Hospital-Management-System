<template>
	<div class="user-page">
		<div class="page-header">
			<h2 class="page-title">My Profile</h2>
			<button v-if="!isEditing" class="btn-add" @click="startEdit">Edit Profile</button>
		</div>

		<div v-if="loadingProfile" class="loading-text">Loading profile...</div>

		<form v-else @submit.prevent="saveProfile" >
			<div class="form-group">
				<label for="profile-name">Name</label>
				<input id="profile-name" v-model="profile.name" type="text" :disabled="!isEditing" required />
			</div>

			<div class="form-group">
				<label for="profile-email">Email</label>
				<input id="profile-email" v-model="profile.email" type="email" disabled />
			</div>

			<div class="form-group">
				<label for="profile-dob">Date of Birth</label>
				<input id="profile-dob" v-model="profile.date_of_birth" type="date" :disabled="!isEditing" />
			</div>

			<div class="form-group">
				<label for="profile-gender">Gender</label>
				<select id="profile-gender" v-model="profile.gender" :disabled="!isEditing">
					<option value="">Select Gender</option>
					<option value="Male">Male</option>
					<option value="Female">Female</option>
					<option value="Other">Other</option>
				</select>
			</div>

			<div class="form-group">
				<label for="profile-phone">Phone Number</label>
				<input id="profile-phone" v-model="profile.phone_number" type="text" :disabled="!isEditing" />
			</div>

			<div class="form-group">
				<label for="profile-address">Address</label>
				<input id="profile-address" v-model="profile.address" type="text" :disabled="!isEditing" />
			</div>

			<div v-if="isEditing" class="form-group">
				<label for="profile-password">New Password (optional)</label>
				<input id="profile-password" v-model="profile.password" type="password" placeholder="Leave blank to keep current password" />
			</div>

			<div v-if="isEditing" class="form-actions">
				<button type="submit" class="btn-primary" :disabled="savingProfile">
					{{ savingProfile ? 'Saving...' : 'Save' }}
				</button>
				<button type="button" class="btn-secondary" :disabled="savingProfile" @click="cancelEdit">Cancel</button>
			</div>
		</form>
	</div>
</template>

<script setup>
import { onMounted, ref } from 'vue';
import { useStore } from 'vuex';
import api from '@/utils/api';

const store = useStore();

const initialProfile = () => ({
	name: '',
	email: '',
	date_of_birth: '',
	gender: '',
	phone_number: '',
	address: '',
	password: '',
});

const loadingProfile = ref(false);
const savingProfile = ref(false);
const isEditing = ref(false);

const profile = ref(initialProfile());

const originalProfile = ref({});

const getUserId = () => store.state.userId || localStorage.getItem('user_id');

const loadProfile = async () => {
	const userId = getUserId();
	if (!userId) return;

	loadingProfile.value = true;
	try {
		const response = await api.get(`/patients/${userId}`);
		const data = response?.data || response || {};

		const loadedProfile = {
			name: data.name || '',
			email: data.email || '',
			date_of_birth: data.date_of_birth || '',
			gender: data.gender || '',
			phone_number: data.phone_number || '',
			address: data.address || '',
			password: '',
		};

		profile.value = { ...loadedProfile };
		originalProfile.value = { ...loadedProfile };
	} catch (error) {
		alert('Failed to load profile: ' + (error?.message || ''));
	} finally {
		loadingProfile.value = false;
	}
};

const startEdit = () => {
	isEditing.value = true;
};

const cancelEdit = () => {
	profile.value = { ...originalProfile.value, password: '' };
	isEditing.value = false;
};

const saveProfile = async () => {
	const userId = getUserId();
	if (!userId) return;

	const payload = {
		name: profile.value.name,
		email: profile.value.email,
		date_of_birth: profile.value.date_of_birth || null,
		gender: profile.value.gender,
		phone_number: profile.value.phone_number,
		address: profile.value.address,
	};

	if (profile.value.password && profile.value.password.trim()) {
		payload.password = profile.value.password;
	}

	savingProfile.value = true;
	try {
		await api.put(`/patients/${userId}`, payload);
		alert('Profile updated successfully.');
		await loadProfile();
		isEditing.value = false;
	} catch (error) {
		alert('Failed to update profile: ' + (error?.message || ''));
	} finally {
		savingProfile.value = false;
	}
};

onMounted(async () => {
	await loadProfile();
});
</script>
