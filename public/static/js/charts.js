/**
 * charts.js - Chart.js integrations for Student & Admin dashboards
 */

function initStudentCharts() {
  // 1. Radar Chart (Category Scores)
  const radarCtx = document.getElementById('radarChart');
  if (radarCtx && window.RADAR_DATA) {
    new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels: window.RADAR_DATA.labels,
        datasets: [{
          label: 'Current Score',
          data: window.RADAR_DATA.scores,
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderColor: '#6366f1',
          pointBackgroundColor: '#6366f1',
          pointBorderColor: '#fff',
          pointHoverBackgroundColor: '#fff',
          pointHoverBorderColor: '#6366f1',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            angleLines: { color: 'rgba(0, 0, 0, 0.08)' },
            grid: { color: 'rgba(0, 0, 0, 0.08)' },
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: { stepSize: 20, backdropColor: 'transparent' }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // 2. Progress / History Line Chart
  const progressCtx = document.getElementById('progressChart');
  if (progressCtx && window.HISTORY_DATA) {
    new Chart(progressCtx, {
      type: 'line',
      data: {
        labels: window.HISTORY_DATA.labels,
        datasets: [{
          label: 'Readiness Score',
          data: window.HISTORY_DATA.scores,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.35,
          pointRadius: 4,
          pointHoverRadius: 6,
          pointBackgroundColor: '#10b981'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            suggestedMin: 0,
            suggestedMax: 100,
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

function initAdminCharts() {
  // 1. Department Average Scores Bar Chart
  const deptCtx = document.getElementById('deptChart');
  if (deptCtx && window.ADMIN_DEPT_DATA) {
    new Chart(deptCtx, {
      type: 'bar',
      data: {
        labels: window.ADMIN_DEPT_DATA.labels,
        datasets: [{
          label: 'Avg Score (%)',
          data: window.ADMIN_DEPT_DATA.avg_scores,
          backgroundColor: '#6366f1',
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            suggestedMin: 0,
            suggestedMax: 100,
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // 2. Status Distribution Doughnut Chart
  const statusCtx = document.getElementById('statusChart');
  if (statusCtx && window.ADMIN_STATUS_DATA) {
    new Chart(statusCtx, {
      type: 'doughnut',
      data: {
        labels: window.ADMIN_STATUS_DATA.labels,
        datasets: [{
          data: window.ADMIN_STATUS_DATA.counts,
          backgroundColor: ['#10b981', '#3b82f6', '#f59e0b', '#ef4444'],
          borderWidth: 2,
          hoverOffset: 4
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        cutout: '65%',
        plugins: {
          legend: {
            position: 'bottom',
            labels: { boxWidth: 12, padding: 12 }
          }
        }
      }
    });
  }

  // 3. Skills Distribution Horizontal Bar Chart
  const skillsCtx = document.getElementById('skillsChart');
  if (skillsCtx && window.ADMIN_SKILLS_DATA) {
    new Chart(skillsCtx, {
      type: 'bar',
      data: {
        labels: window.ADMIN_SKILLS_DATA.labels,
        datasets: [{
          label: 'Student Count',
          data: window.ADMIN_SKILLS_DATA.counts,
          backgroundColor: '#06b6d4',
          borderRadius: 4
        }]
      },
      options: {
        indexAxis: 'y',
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          x: {
            beginAtZero: true,
            grid: { color: 'rgba(0, 0, 0, 0.05)' }
          },
          y: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}

function initAdminDetailCharts() {
  // 1. Radar Chart
  const radarCtx = document.getElementById('radarChartAdmin');
  if (radarCtx && window.RADAR_DATA) {
    new Chart(radarCtx, {
      type: 'radar',
      data: {
        labels: window.RADAR_DATA.labels,
        datasets: [{
          label: 'Student Readiness',
          data: window.RADAR_DATA.scores,
          backgroundColor: 'rgba(99, 102, 241, 0.2)',
          borderColor: '#6366f1',
          pointBackgroundColor: '#6366f1',
          borderWidth: 2
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          r: {
            suggestedMin: 0,
            suggestedMax: 100,
            ticks: { stepSize: 20, backdropColor: 'transparent' }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  // 2. History Line Chart
  const historyCtx = document.getElementById('historyChartAdmin');
  if (historyCtx && window.HISTORY_DATA) {
    new Chart(historyCtx, {
      type: 'line',
      data: {
        labels: window.HISTORY_DATA.labels,
        datasets: [{
          label: 'Score History',
          data: window.HISTORY_DATA.scores,
          borderColor: '#10b981',
          backgroundColor: 'rgba(16, 185, 129, 0.1)',
          fill: true,
          tension: 0.35,
          pointRadius: 4,
          pointBackgroundColor: '#10b981'
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        scales: {
          y: {
            suggestedMin: 0,
            suggestedMax: 100
          },
          x: {
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }
}
