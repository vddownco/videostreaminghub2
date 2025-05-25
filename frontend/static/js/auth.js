/**
 * Authentication utilities for VideoStreamingHub
 */

// Auth state
const AUTH = {
    // Check if user is logged in
    isLoggedIn: function() {
        return !!localStorage.getItem('token');
    },
    
    // Get the current auth token
    getToken: function() {
        return localStorage.getItem('token');
    },
    
    // Set auth token
    setToken: function(token) {
        localStorage.setItem('token', token);
    },
    
    // Clear auth token (logout)
    clearToken: function() {
        localStorage.removeItem('token');
    },
    
    // Get auth headers for API requests
    getHeaders: function() {
        const token = this.getToken();
        if (!token) return {};
        return {
            'Authorization': `Bearer ${token}`
        };
    },
    
    // Redirect to login if not authenticated
    requireAuth: function(redirectPath) {
        if (!this.isLoggedIn()) {
            const currentPath = window.location.pathname;
            window.location.href = `/login?redirect=${encodeURIComponent(redirectPath || currentPath)}`;
            return false;
        }
        return true;
    },
    
    // Get current user info
    getCurrentUser: async function() {
        if (!this.isLoggedIn()) return null;
        
        try {
            const response = await fetch('/users/me', {
                headers: this.getHeaders()
            });
            
            if (!response.ok) {
                if (response.status === 401) {
                    // Token expired or invalid
                    this.clearToken();
                    return null;
                }
                throw new Error(`Failed to get user info: ${response.status}`);
            }
            
            return await response.json();
        } catch (error) {
            console.error('Error getting user info:', error);
            return null;
        }
    },
    
    // Handle API response with auth check
    handleApiResponse: function(response) {
        if (response.status === 401) {
            // Unauthorized - token expired or invalid
            this.clearToken();
            window.location.href = `/login?redirect=${encodeURIComponent(window.location.pathname)}`;
            throw new Error('Session expired. Please log in again.');
        }
        return response;
    },
    
    // Logout the user
    logout: function() {
        this.clearToken();
        window.location.href = '/login';
    }
};

// Add auth status check on page load
document.addEventListener('DOMContentLoaded', function() {
    // Update navbar based on auth status
    updateAuthUI();
    
    // Add logout handler if logout button exists
    const logoutBtn = document.getElementById('logout-btn');
    if (logoutBtn) {
        logoutBtn.addEventListener('click', function(e) {
            e.preventDefault();
            AUTH.logout();
        });
    }
});

// Update UI based on authentication status
function updateAuthUI() {
    const isLoggedIn = AUTH.isLoggedIn();
    
    // Show/hide elements based on auth status
    document.querySelectorAll('.auth-only').forEach(el => {
        el.style.display = isLoggedIn ? '' : 'none';
    });
    
    document.querySelectorAll('.guest-only').forEach(el => {
        el.style.display = isLoggedIn ? 'none' : '';
    });
    
    // Fetch and display user info if logged in
    if (isLoggedIn) {
        AUTH.getCurrentUser().then(user => {
            if (user) {
                document.querySelectorAll('.user-name').forEach(el => {
                    el.textContent = user.username;
                });
                
                // Set profile picture if available
                const profilePicElements = document.querySelectorAll('.user-profile-pic');
                if (profilePicElements.length > 0 && user.profile_picture) {
                    profilePicElements.forEach(el => {
                        if (el.tagName === 'IMG') {
                            el.src = user.profile_picture || '/static/profile_pictures/default.jpg';
                        } else {
                            el.style.backgroundImage = `url(${user.profile_picture || '/static/profile_pictures/default.jpg'})`;
                        }
                    });
                }
            }
        }).catch(error => {
            console.error('Error fetching user data:', error);
        });
    }
} 