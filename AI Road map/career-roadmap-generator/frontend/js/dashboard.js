/**
 * Dashboard & App Logic
 */

document.addEventListener('DOMContentLoaded', async () => {
    // Only run on dashboard
    if (!window.location.pathname.includes('dashboard')) return;
    
    // Check auth
    await Auth.verifyToken();
    const user = Auth.getUser();
    
    if (user) {
        document.getElementById('welcomeMessage').textContent = `Welcome back, ${user.name}!`;
        document.getElementById('userNameDisplay').textContent = user.name;
    }

    // Sidebar & Mobile Menu Toggle
    const sidebar = document.getElementById('sidebar');
    const sidebarToggle = document.getElementById('sidebarToggle');
    const sidebarOverlay = document.getElementById('sidebarOverlay');

    if (sidebarToggle && sidebar && sidebarOverlay) {
        sidebarToggle.addEventListener('click', () => {
            sidebar.classList.add('active');
            sidebarOverlay.classList.add('active');
        });

        sidebarOverlay.addEventListener('click', () => {
            sidebar.classList.remove('active');
            sidebarOverlay.classList.remove('active');
        });
    }

    // Theme Toggle
    const themeToggleSidebar = document.getElementById('themeToggleSidebar');
    if (themeToggleSidebar) {
        themeToggleSidebar.addEventListener('click', (e) => {
            e.preventDefault();
            const html = document.documentElement;
            const currentTheme = html.getAttribute('data-theme');
            const newTheme = currentTheme === 'dark' ? 'light' : 'dark';
            html.setAttribute('data-theme', newTheme);
            localStorage.setItem('theme', newTheme);
            
            // Update chart theme if it exists
            if (window.skillsChart) {
                updateChartTheme(window.skillsChart, newTheme);
            }
        });
    }
    
    // Load saved theme
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme) {
        document.documentElement.setAttribute('data-theme', savedTheme);
    }

    // Initialize Chat Widget
    initChatWidget();
    
    // Load Dashboard Data
    loadDashboardData();
});

async function loadDashboardData() {
    UI.showLoading(true);
    
    // 1. Get Resume Analysis Data
    const resumeRes = await ApiService.request('/resume/analysis');
    if (resumeRes.success && resumeRes.data.resume.analysis) {
        const analysis = resumeRes.data.resume.analysis;
        
        // Update Stats
        const atsScore = analysis.ats_score || 0;
        document.getElementById('atsScoreDisplay').textContent = `${atsScore}/100`;
        
        // Count skills
        let skillCount = 0;
        if (analysis.skills) {
            skillCount += (analysis.skills.technical || []).length;
            skillCount += (analysis.skills.tools || []).length;
        }
        document.getElementById('skillsCountDisplay').textContent = skillCount;
        
        // Render Chart
        renderSkillsChart(analysis.skills);
    } else {
        document.getElementById('atsScoreDisplay').textContent = 'N/A';
        document.getElementById('skillsCountDisplay').textContent = '0';
        
        // Render empty chart
        renderSkillsChart(null);
    }
    
    // 2. Get Roadmap Data (for employability score)
    const roadmapRes = await ApiService.request('/roadmap/list');
    if (roadmapRes.success && roadmapRes.data.roadmaps.length > 0) {
        // Just mock a score based on roadmap existence for now
        document.getElementById('employabilityScoreDisplay').textContent = '75%';
    } else {
        document.getElementById('employabilityScoreDisplay').textContent = 'N/A';
    }
    
    UI.showLoading(false);
}

function renderSkillsChart(skillsData) {
    const ctx = document.getElementById('skillsRadarChart');
    if (!ctx) return;
    
    let labels = ['Frontend', 'Backend', 'Database', 'Cloud/DevOps', 'Soft Skills', 'Tools'];
    let data = [10, 10, 10, 10, 10, 10]; // Default empty state
    
    if (skillsData) {
        // Very basic mapping logic for demo purposes
        const techStr = (skillsData.technical || []).join(' ').toLowerCase();
        
        data = [
            (techStr.match(/html|css|react|angular|vue|javascript/g) || []).length * 20 + 20,
            (techStr.match(/node|python|java|php|spring|express/g) || []).length * 20 + 20,
            (techStr.match(/sql|mongo|redis|postgres|oracle/g) || []).length * 20 + 20,
            (techStr.match(/aws|azure|docker|kubernetes|ci\/cd/g) || []).length * 20 + 20,
            (skillsData.soft || []).length * 15 + 40,
            (skillsData.tools || []).length * 15 + 20
        ].map(val => Math.min(val, 100)); // Cap at 100
    }
    
    const theme = document.documentElement.getAttribute('data-theme');
    const textColor = theme === 'dark' ? '#F8FAFC' : '#0F172A';
    const gridColor = theme === 'dark' ? '#334155' : '#E2E8F0';

    if (window.skillsChart) {
        window.skillsChart.destroy();
    }

    window.skillsChart = new Chart(ctx, {
        type: 'radar',
        data: {
            labels: labels,
            datasets: [{
                label: 'Skill Proficiency',
                data: data,
                backgroundColor: 'rgba(37, 99, 235, 0.2)',
                borderColor: '#2563EB',
                pointBackgroundColor: '#38BDF8',
                pointBorderColor: '#fff',
                pointHoverBackgroundColor: '#fff',
                pointHoverBorderColor: '#38BDF8'
            }]
        },
        options: {
            scales: {
                r: {
                    angleLines: { color: gridColor },
                    grid: { color: gridColor },
                    pointLabels: { color: textColor, font: { family: 'Inter', size: 12 } },
                    ticks: { display: false, min: 0, max: 100 }
                }
            },
            plugins: {
                legend: { display: false }
            },
            maintainAspectRatio: false
        }
    });
}

function updateChartTheme(chart, theme) {
    const textColor = theme === 'dark' ? '#F8FAFC' : '#0F172A';
    const gridColor = theme === 'dark' ? '#334155' : '#E2E8F0';
    
    chart.options.scales.r.angleLines.color = gridColor;
    chart.options.scales.r.grid.color = gridColor;
    chart.options.scales.r.pointLabels.color = textColor;
    chart.update();
}

function initChatWidget() {
    const toggle = document.getElementById('chatToggleBtn');
    const panel = document.getElementById('chatPanel');
    const closeBtn = document.getElementById('chatCloseBtn');
    const input = document.getElementById('chatInput');
    const sendBtn = document.getElementById('chatSendBtn');
    const messagesContainer = document.getElementById('chatMessages');
    
    if (!toggle || !panel) return;
    
    toggle.addEventListener('click', () => {
        panel.classList.toggle('active');
        if (panel.classList.contains('active')) {
            input.focus();
        }
    });
    
    closeBtn.addEventListener('click', () => {
        panel.classList.remove('active');
    });
    
    const sendMessage = async () => {
        const text = input.value.trim();
        if (!text) return;
        
        // Add user message
        addMessage(text, 'user');
        input.value = '';
        input.disabled = true;
        sendBtn.disabled = true;
        
        // Add loading indicator
        const loadingId = 'msg-' + Date.now();
        addMessage('<i class="fa-solid fa-ellipsis fa-fade"></i>', 'ai', loadingId);
        
        // Call API
        const res = await ApiService.request('/skills/chat', 'POST', { message: text });
        
        // Remove loading
        document.getElementById(loadingId)?.remove();
        
        if (res.success) {
            // Basic markdown to HTML formatting for the response
            let formattedResponse = res.data.response
                .replace(/\*\*(.*?)\*\*/g, '<strong>$1</strong>')
                .replace(/\*(.*?)\*/g, '<em>$1</em>')
                .replace(/\n/g, '<br>');
            
            addMessage(formattedResponse, 'ai');
        } else {
            addMessage("Sorry, I'm having trouble connecting to the server right now.", 'ai');
        }
        
        input.disabled = false;
        sendBtn.disabled = false;
        input.focus();
    };
    
    sendBtn.addEventListener('click', sendMessage);
    input.addEventListener('keypress', (e) => {
        if (e.key === 'Enter') sendMessage();
    });
    
    function addMessage(text, sender, id = null) {
        const div = document.createElement('div');
        div.className = `message ${sender}`;
        if (id) div.id = id;
        div.innerHTML = text;
        messagesContainer.appendChild(div);
        messagesContainer.scrollTop = messagesContainer.scrollHeight;
    }
}
