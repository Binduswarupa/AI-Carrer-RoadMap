/**
 * API Service for handling all backend requests
 */
const API_URL = 'http://localhost:5000/api';

class ApiService {
    static getHeaders() {
        const headers = {
            'Content-Type': 'application/json'
        };
        const token = localStorage.getItem('token');
        if (token) {
            headers['Authorization'] = `Bearer ${token}`;
        }
        return headers;
    }

    static async request(endpoint, method = 'GET', body = null, isFormData = false) {
        try {
            const options = {
                method,
                headers: isFormData ? { 'Authorization': `Bearer ${localStorage.getItem('token')}` } : this.getHeaders()
            };

            if (body && !isFormData) {
                options.body = JSON.stringify(body);
            } else if (body && isFormData) {
                options.body = body;
            }

            const response = await fetch(`${API_URL}${endpoint}`, options);
            const data = await response.json();

            if (!response.ok) {
                throw new Error(data.error || 'API Request Failed');
            }

            return { success: true, data };
        } catch (error) {
            console.error('API Error:', error);
            if (error.message.includes('Token') || error.message.includes('token')) {
                Auth.logout();
            }
            return { success: false, error: error.message };
        }
    }
}

/**
 * Authentication Module
 */
class Auth {
    static async login(email, password) {
        const response = await ApiService.request('/auth/login', 'POST', { email, password });
        if (response.success) {
            this.setSession(response.data.token, response.data.user);
            window.location.href = 'dashboard.html';
            return true;
        } else {
            UI.showToast(response.error, 'error');
            return false;
        }
    }

    static async register(name, email, password, career_goal) {
        const response = await ApiService.request('/auth/register', 'POST', { name, email, password, career_goal });
        if (response.success) {
            this.setSession(response.data.token, response.data.user);
            window.location.href = 'dashboard.html';
            return true;
        } else {
            UI.showToast(response.error, 'error');
            return false;
        }
    }

    static logout() {
        localStorage.removeItem('token');
        localStorage.removeItem('user');
        window.location.href = 'login.html';
    }

    static setSession(token, user) {
        localStorage.setItem('token', token);
        localStorage.setItem('user', JSON.stringify(user));
    }

    static getUser() {
        const user = localStorage.getItem('user');
        return user ? JSON.parse(user) : null;
    }

    static isAuthenticated() {
        return !!localStorage.getItem('token');
    }
    
    static async verifyToken() {
        if (!this.isAuthenticated()) return false;
        const res = await ApiService.request('/auth/verify');
        if (!res.success) this.logout();
        return res.success;
    }
}

/**
 * UI Utilities
 */
class UI {
    static showToast(message, type = 'info') {
        const container = document.getElementById('toastContainer');
        if (!container) return;

        const toast = document.createElement('div');
        toast.className = `toast toast-${type}`;
        
        const icon = type === 'success' ? 'fa-check-circle' : type === 'error' ? 'fa-circle-exclamation' : 'fa-info-circle';
        
        toast.innerHTML = `
            <i class="fa-solid ${icon}"></i>
            <span>${message}</span>
        `;
        
        container.appendChild(toast);
        
        setTimeout(() => {
            toast.style.opacity = '0';
            toast.style.transform = 'translateY(-20px)';
            setTimeout(() => toast.remove(), 300);
        }, 3000);
    }
    
    static showLoading(show = true) {
        if (show) {
            if (!document.getElementById('loadingOverlay')) {
                const overlay = document.createElement('div');
                overlay.id = 'loadingOverlay';
                overlay.className = 'loading-overlay';
                overlay.innerHTML = '<div class="spinner"></div>';
                document.body.appendChild(overlay);
            }
        } else {
            const overlay = document.getElementById('loadingOverlay');
            if (overlay) overlay.remove();
        }
    }
}

// Check auth on protected pages
document.addEventListener('DOMContentLoaded', () => {
    const isAuthPage = window.location.pathname.includes('login') || 
                       window.location.pathname.includes('register') || 
                       window.location.pathname === '/' || 
                       window.location.pathname.includes('index');
                       
    if (!isAuthPage && !Auth.isAuthenticated()) {
        window.location.href = 'login.html';
    }
});
