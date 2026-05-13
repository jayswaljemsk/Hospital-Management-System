<template>
  <div class="theme-gradient-bg full-page-center">
    <div class="auth-card login-box">
      <h2 class="auth-title">Login</h2>
      <p class="auth-subtitle">Welcome back to Hospital Management System</p>
      
      <div v-if="errorMsg" class="auth-error">{{ errorMsg }}</div>

      <form @submit.prevent="handleLogin">
        <div class="auth-form-group">
          <label for="email">Email or Username</label>
          <input
            class="auth-field"
            id="email"
            v-model="email"
            type="text"
            placeholder="Enter your email or username"
            required
            :disabled="loading"
          />
        </div>

        <div class="auth-form-group">
          <label for="password">Password</label>
          <input
            class="auth-field"
            id="password"
            v-model="password"
            type="password"
            placeholder="Enter your password"
            required
            :disabled="loading"
          />
        </div>

        <button type="submit" class="auth-submit" :disabled="loading">
          {{ loading ? 'Logging in...' : 'Login' }}
        </button>
      </form>

      <div class="auth-footer">
        <p>Don't have an account? <router-link to="/register">Register here</router-link></p>
      </div>
    </div>
  </div>
</template>

<script setup>
import { ref } from 'vue';
import { useStore } from 'vuex';
import { useRouter } from 'vue-router';

const router = useRouter();
const store = useStore();
const email = ref('');
const password = ref('');
const loading = ref(false);
const errorMsg = ref('');

const handleLogin = async () => {
  if (!email.value || !password.value) {
    errorMsg.value = 'Please fill in all fields';
    return;
  }

  loading.value = true;
  errorMsg.value = '';

  try {
    await store.dispatch('login', {
      email: email.value,
      password: password.value,
    });

    const role = store.state.role;
    if (role === 'admin') {
      router.push('/admin_dashboard');
    } else if (role === 'doctor') {
      router.push('/doctor_dashboard');
    } else if (role === 'patient') {
      router.push('/patient_dashboard');
    } else {
      router.push('/');
    }
  } catch (error) {
    errorMsg.value = error.message || 'Login failed. Please try again.';
  } finally {
    loading.value = false;
  }
};
</script>
