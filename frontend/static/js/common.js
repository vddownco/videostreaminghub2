// Auth token management
const TOKEN_KEY = 'videohub_token';
const USER_DATA_KEY = 'videohub_user';

// Check if user is logged in
function isLoggedIn() {
    return localStorage.getItem(TOKEN_KEY) !== null;
}

// Get auth token
function getToken() {
    return localStorage.getItem(TOKEN_KEY);
}

// Save auth token and user data
function setAuth(token, userData) {
    localStorage.setItem(TOKEN_KEY, token);
    localStorage.setItem(USER_DATA_KEY, JSON.stringify(userData));
    updateUI();
}

// Clear auth data (logout)
function clearAuth() {
    localStorage.removeItem(TOKEN_KEY);
    localStorage.removeItem(USER_DATA_KEY);
    updateUI();
}

// Get user data
function getUserData() {
    const userData = localStorage.getItem(USER_DATA_KEY);
    return userData ? JSON.parse(userData) : null;
}

// Update UI based on auth state
function updateUI() {
    const isAuth = isLoggedIn();
    const userDropdown = document.getElementById('user-dropdown');
    const loginButtons = document.getElementById('login-buttons');
    
    if (isAuth) {
        const userData = getUserData();
        
        if (userDropdown) {
            userDropdown.style.display = 'block';
            
            const usernameElement = document.getElementById('username');
            const userAvatar = document.getElementById('user-avatar');
            
            if (usernameElement) {
                usernameElement.textContent = userData.username;
            }
            
            if (userAvatar && userData.profile_picture) {
                userAvatar.src = `/static/profile_pictures/${userData.profile_picture}`;
            }
        }
        
        if (loginButtons) {
            loginButtons.style.display = 'none';
        }
    } else {
        if (userDropdown) {
            userDropdown.style.display = 'none';
        }
        
        if (loginButtons) {
            loginButtons.style.display = 'block';
        }
    }
}

// API request with auth token
async function apiRequest(url, options = {}) {
    const token = getToken();
    
    const headers = {
        'Content-Type': 'application/json',
        ...options.headers
    };
    
    if (token) {
        headers['Authorization'] = `Bearer ${token}`;
    }
    
    const response = await fetch(url, {
        ...options,
        headers
    });
    
    // If unauthorized, clear auth data
    if (response.status === 401) {
        clearAuth();
        window.location.href = '/login';
        return null;
    }
    
    return response;
}

// Format duration (seconds to MM:SS or HH:MM:SS)
function formatDuration(seconds) {
    const hours = Math.floor(seconds / 3600);
    const minutes = Math.floor((seconds % 3600) / 60);
    const secs = seconds % 60;
    
    if (hours > 0) {
        return `${hours}:${minutes.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
    } else {
        return `${minutes}:${secs.toString().padStart(2, '0')}`;
    }
}

// Format view count (e.g. 1.2K, 3.5M)
function formatViewCount(views) {
    if (views >= 1000000) {
        return `${(views / 1000000).toFixed(1)}M views`;
    } else if (views >= 1000) {
        return `${(views / 1000).toFixed(1)}K views`;
    } else {
        return `${views} views`;
    }
}

// Calculate time ago from date
function getTimeAgo(date) {
    const seconds = Math.floor((new Date() - new Date(date)) / 1000);
    
    let interval = seconds / 31536000;
    if (interval > 1) {
        return Math.floor(interval) + " years ago";
    }
    
    interval = seconds / 2592000;
    if (interval > 1) {
        return Math.floor(interval) + " months ago";
    }
    
    interval = seconds / 86400;
    if (interval > 1) {
        return Math.floor(interval) + " days ago";
    }
    
    interval = seconds / 3600;
    if (interval > 1) {
        return Math.floor(interval) + " hours ago";
    }
    
    interval = seconds / 60;
    if (interval > 1) {
        return Math.floor(interval) + " minutes ago";
    }
    
    return Math.floor(seconds) + " seconds ago";
}

// Register logout event handler
document.addEventListener('DOMContentLoaded', function() {
    // Update UI based on auth state
    updateUI();
    
    // Add logout event handler
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            clearAuth();
            window.location.href = '/';
        });
    }
}); 