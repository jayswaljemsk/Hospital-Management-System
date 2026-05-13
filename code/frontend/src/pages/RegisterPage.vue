<template>
	<div class="theme-gradient-bg full-page-center">
		<div class="auth-card auth-card-wide">
			<h2 class="auth-title">Register</h2>
			<p class="auth-subtitle">Create your patient account</p>

			<div v-if="errorMsg" class="auth-error">{{ errorMsg }}</div>

			<form @submit.prevent="handleRegister">
				<div class="auth-form-group">
					<label for="name">Full Name</label>
					<input
						class="auth-field"
						id="name"
						v-model="form.name"
						type="text"
						placeholder="Enter your full name"
						required
						:disabled="loading"
					/>
				</div>

				<div class="auth-form-group">
					<label for="email">Email</label>
					<input
						class="auth-field"
						id="email"
						v-model="form.email"
						type="email"
						placeholder="Enter your email"
						required
						:disabled="loading"
					/>
				</div>

				<div class="auth-form-group">
					<label for="password">Password</label>
					<input
						class="auth-field"
						id="password"
						v-model="form.password"
						type="password"
						placeholder="Create a password"
						required
						:disabled="loading"
					/>
				</div>

				<div class="auth-form-group">
					<label for="date_of_birth">Date of Birth</label>
					<input
						class="auth-field"
						id="date_of_birth"
						v-model="form.date_of_birth"
						type="date"
						required
						:disabled="loading"
					/>
				</div>

				<div class="auth-form-group">
					<label for="gender">Gender</label>
					<select
						class="auth-field"
						id="gender"
						v-model="form.gender"
						required
						:disabled="loading"
					>
						<option value="" disabled>Select gender</option>
						<option value="Male">Male</option>
						<option value="Female">Female</option>
						<option value="Other">Other</option>
					</select>
				</div>

				<div class="auth-form-group">
					<label for="phone_number">Phone Number</label>
					<input
						class="auth-field"
						id="phone_number"
						v-model="form.phone_number"
						type="text"
						placeholder="Enter your phone number"
						required
						:disabled="loading"
					/>
				</div>

				<div class="auth-form-group">
					<label for="address">Address</label>
					<input
						class="auth-field"
						id="address"
						v-model="form.address"
						placeholder="Enter your address"
						rows="3"
						required
						:disabled="loading"
					/>
				</div>

				<button type="submit" class="auth-submit" :disabled="loading">
					{{ loading ? 'Creating account...' : 'Register' }}
				</button>
			</form>

			<div class="auth-footer">
				<p>Already have an account? <router-link to="/login">Login here</router-link></p>
			</div>
		</div>
	</div>
</template>

<script setup>
import { reactive, ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const store = useStore();
const router = useRouter();

const loading = ref(false);
const errorMsg = ref('');

const form = reactive({
	name: '',
	email: '',
	password: '',
	date_of_birth: '',
	gender: '',
	phone_number: '',
	address: '',
});

const handleRegister = async () => {
	if (
		!form.name ||
		!form.email ||
		!form.password ||
		!form.date_of_birth ||
		!form.gender ||
		!form.phone_number ||
		!form.address
	) {
		errorMsg.value = 'Please fill in all fields';
		return;
	}

	loading.value = true;
	errorMsg.value = '';

	try {
		await store.dispatch('register', {
			name: form.name,
			email: form.email,
			password: form.password,
			date_of_birth: form.date_of_birth,
			gender: form.gender,
			phone_number: form.phone_number,
			address: form.address,
		});

		router.push('/login');
	} catch (error) {
		errorMsg.value = error.message || 'Registration failed. Please try again.';
	} finally {
		loading.value = false;
	}
};
</script>
