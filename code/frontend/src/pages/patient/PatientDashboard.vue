<template>
  <div class="user-dashboard">
    <!-- Navbar -->
    <nav class="navbar">
      <div class="navbar-container">
        <div class="navbar-brand">Hospital Management</div>
        <div class="navbar-welcome">Welcome {{ store.state.name }} !!</div>
        <ul class="nav-links">
          <li><router-link to="/patient_dashboard/home" class="nav-link">Home</router-link></li>
          <li><router-link to="/patient_dashboard/departments" class="nav-link">Departments</router-link></li>
          <li><router-link to="/patient_dashboard/doctors" class="nav-link">Doctors</router-link></li>
          <li><router-link to="/patient_dashboard/history" class="nav-link">History</router-link></li>
          <li><router-link to="/patient_dashboard/profile" class="nav-link">Profile</router-link></li>
          <li><button @click="logout" class="nav-link logout-btn">Logout</button></li>
        </ul>
      </div>
    </nav>

    <!-- Main content -->
    <div class="user-content">
      <router-view />
    </div>
  </div>
</template>

<script setup>
import { useRouter } from 'vue-router';
import { useStore } from 'vuex';

const router = useRouter();
const store = useStore();

const logout = () => {
  store.dispatch('logout');
  router.push('/');
};
</script>
