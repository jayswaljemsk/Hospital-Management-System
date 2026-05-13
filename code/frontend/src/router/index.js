import { createRouter, createWebHistory } from 'vue-router'
import store from "@/store/userStore";

const router = createRouter({
  history: createWebHistory(import.meta.env.BASE_URL),
  routes: [
    {
    path: "/",
    name: "home",
    component: () => import("@/pages/HomePage.vue"),
    meta: { title: "Home" },
  },
  {
    path: "/login",
    name: "login",
    component: () => import("@/pages/LoginPage.vue"),
    meta: { title: "Login Page"},
  },
  {
    path: "/register",
    name: "register",
    component: () => import("@/pages/RegisterPage.vue"),
    meta: { title: "Register Page"},
  },
  {
    path: "/admin_dashboard",
    name: "admin_dashboard",
    component: () => import("@/pages/admin/AdminDashboard.vue"),
    meta: { requiresAuth: true, roles: ["admin"] },
    redirect: "/admin_dashboard/home",
    children: [
      {
        path: "home",
        name: "admin_home",
        component: () => import("@/pages/admin/AdminHome.vue"),
        meta: { title: "Admin Home", requiresAuth: true, roles: ["admin"] },
      },
      {
        path: "doctors",
        name: "admin_doctors",
        component: () => import("@/pages/admin/AdminDoctor.vue"),
        meta: { title: "Manage Doctors", requiresAuth: true, roles: ["admin"] },
      },
      {
        path: "departments",
        name: "admin_departments",
        component: () => import("@/pages/admin/AdminDepartment.vue"),
        meta: { title: "Manage Departments", requiresAuth: true, roles: ["admin"] },
      },
      {
        path: "patients",
        name: "admin_patients",
        component: () => import("@/pages/admin/AdminPatient.vue"),
        meta: { title: "Manage Patients", requiresAuth: true, roles: ["admin"] },
      },
    ],
  },
  {
    path: "/doctor_dashboard",
    name: "doctor_dashboard",
    component: () => import("@/pages/doctor/DoctorDashboard.vue"),
    meta: { requiresAuth: true, roles: ["doctor"] },
    redirect: "/doctor_dashboard/home",
    children: [
      {
        path: "home",
        name: "doctor_home",
        component: () => import("@/pages/doctor/DoctorHome.vue"),
        meta: { title: "Doctor Home", requiresAuth: true, roles: ["doctor"] },
      },
      {
        path: "availability",
        name: "doctor_availability",
        component: () => import("@/pages/doctor/DoctorAvailability.vue"),
        meta: { title: "Manage Availability", requiresAuth: true, roles: ["doctor"] },
      },
      {
        path: "profile",
        name: "doctor_profile",
        component: () => import("@/pages/doctor/DoctorProfile.vue"),
        meta: { title: "My Profile", requiresAuth: true, roles: ["doctor"] },
      }
    ],
  },
  {
    path: "/patient_dashboard",
    name: "patient_dashboard",
    component: () => import("@/pages/patient/PatientDashboard.vue"),
    meta: { requiresAuth: true, roles: ["patient"] },
    redirect: "/patient_dashboard/home",
    children: [
      {
        path: "home",
        name: "patient_home",
        component: () => import("@/pages/patient/PatientHome.vue"),
        meta: { title: "Patient Home", requiresAuth: true, roles: ["patient"] },
      },
      {
        path: "departments",
        name: "patient_departments",
        component: () => import("@/pages/patient/PatientDepartment.vue"),
        meta: { title: "Departments", requiresAuth: true, roles: ["patient"] },
      },
      {
        path: "doctors",
        name: "patient_doctors",
        component: () => import("@/pages/patient/PatientDoctor.vue"),
        meta: { title: "Doctors", requiresAuth: true, roles: ["patient"] },
      },
      {
        path: "history",
        name: "patient_history",
        component: () => import("@/pages/patient/PatientHistory.vue"),
        meta: { title: "Medical History", requiresAuth: true, roles: ["patient"] },
      },
      {
        path: "profile",
        name: "patient_profile",
        component: () => import("@/pages/patient/PatientProfile.vue"),
        meta: { title: "My Profile", requiresAuth: true, roles: ["patient"] },
      },
      
    ],
  },

  ],
})

router.beforeEach((to) => {
  if (to.meta?.title) {
    document.title = to.meta.title;
  }

  if (to.path === "/login") {
    store.dispatch("logout");
    sessionStorage.clear();
  }

  const isAuthenticated = !!store.state.token;
  const role = store.state.role;
  const dashboardRoute = store.getters.dashboardRoute;

  if (to.meta?.requiresAuth && !isAuthenticated) {
    return "/login";
  }

  if (to.meta?.roles && !to.meta.roles.includes(role)) {
    return isAuthenticated ? (dashboardRoute || "/") : "/login";
  }

  return true;
});

export default router
