<template>
  <div class="user-page">
		<div class="page-header">
			<h2 class="page-title">Medical History</h2>
			<div class="history-actions">
				<button class="btn-add" :disabled="exportingCsv" @click="triggerExportCsv">
					{{ exportingCsv ? 'Exporting...' : 'Export CSV' }}
				</button>
			</div>
		</div>

		<div class="table-wrap">
			<table class="data-table">
				<thead>
					<tr>
						<th>ID</th>
						<th>Date</th>
						<th>Doctor</th>
						<th>Tests Done</th>
						<th>Diagnosis</th>
						<th>Prescriptions</th>
						<th>Medicines</th>
					</tr>
				</thead>
				<tbody>
					<tr v-if="loadingHistory"><td colspan="7" class="loading-text">Loading history...</td></tr>
					<tr v-else-if="history.length === 0">
						<td colspan="7" class="empty-state">No history found</td>
					</tr>
					<template v-else>
						<tr v-for="entry in history" :key="entry.id">
							<td>{{ entry.id }}</td>
							<td>{{ entry.date || '-' }}</td>
							<td>{{ entry.doctor_name || '-' }}</td>
							<td>{{ entry.tests_done || '-' }}</td>
							<td>{{ entry.diagnosis || '-' }}</td>
							<td>{{ entry.prescription || '-' }}</td>
							<td>{{ entry.medicines || '-' }}</td>
						</tr>
					</template>
				</tbody>
			</table>
		</div>
	</div>
</template>

<script setup>
import { onMounted, onUnmounted, ref } from 'vue';
import { useStore } from 'vuex';
import api from '@/utils/api';

const store = useStore();
const history = ref([]);
const loadingHistory = ref(false);
const exportingCsv = ref(false);
const exportTaskId = ref('');

let exportPollTimer = null;

const loadHistory = async () => {
	loadingHistory.value = true;
	const userId = store.state.userId || localStorage.getItem('user_id');

	if (!userId) {
		history.value = [];
		loadingHistory.value = false;
		return;
	}

	try {
		const response = await api.get(`/patients/${userId}`);
		const patientData = response?.data || response;
		history.value = Array.isArray(patientData?.history) ? patientData.history : [];
	} catch (error) {
		alert('Failed to load patient history: ' + (error?.message || ''));
		history.value = [];
	} finally {
		loadingHistory.value = false;
	}
};

const triggerExportCsv = async () => {
	const userId = store.state.userId || localStorage.getItem('user_id');
	if (!userId) {
		alert('Unable to identify patient user. Please login again.');
		return;
	}

	exportingCsv.value = true;
	try {
		const response = await api.post(`/patients/${userId}/export-csv`, {});
		exportTaskId.value = response?.task_id || '';
		startExportStatusPolling();
	} catch (error) {
		exportingCsv.value = false;
		alert('Failed to start CSV export: ' + (error?.message || ''));
	}
};

const checkExportStatus = async () => {
	const userId = store.state.userId || localStorage.getItem('user_id');
	if (!userId || !exportTaskId.value) return;

	try {
		const response = await api.get(`/patients/${userId}/export-csv/${exportTaskId.value}`);
		const status = response?.data?.status || 'UNKNOWN';

		if (status === 'SUCCESS') {
			stopExportStatusPolling();
			alert('Export is ready! Starting download...');
			await downloadExportCsv();
			exportingCsv.value = false;
			return;
		}
		if (status === 'FAILURE') {
			stopExportStatusPolling();
			exportingCsv.value = false;
			alert('Export failed. Please retry.');
			return;
		}
	} catch (error) {
		stopExportStatusPolling();
		exportingCsv.value = false;
		alert('Failed to check export status: ' + (error?.message || ''));
	}
};

const startExportStatusPolling = () => {
	stopExportStatusPolling();
	exportPollTimer = setInterval(() => {
		checkExportStatus();
	}, 2000);
};

const stopExportStatusPolling = () => {
	if (exportPollTimer) {
		clearInterval(exportPollTimer);
		exportPollTimer = null;
	}
};

const downloadExportCsv = async () => {
	const userId = store.state.userId || localStorage.getItem('user_id');
	if (!userId || !exportTaskId.value) return;

	try {
		await api.download(
			`/patients/${userId}/export-csv/${exportTaskId.value}/download`,
			`treatments_user_${userId}.csv`
		);
	} catch (error) {
		alert('Failed to download CSV: ' + (error?.message || ''));
	}
};

onMounted(async () => {
	await loadHistory();
});

onUnmounted(() => {
	stopExportStatusPolling();
});
</script>
