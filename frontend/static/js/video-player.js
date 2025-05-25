/**
 * Video player functionality for VideoStreamingHub
 */

document.addEventListener('DOMContentLoaded', function() {
    // Video player elements
    const player = document.getElementById('video-player');
    const videoTitle = document.getElementById('video-title');
    const channelName = document.getElementById('channel-name');
    const videoViews = document.getElementById('video-views');
    const likeCount = document.getElementById('like-count');
    const dislikeCount = document.getElementById('dislike-count');
    const likeBtn = document.getElementById('like-btn');
    const dislikeBtn = document.getElementById('dislike-btn');
    const shareBtn = document.getElementById('share-btn');
    const saveBtn = document.getElementById('save-btn');
    const commentForm = document.getElementById('comment-form');
    const commentInput = document.getElementById('comment-input');
    const commentsList = document.getElementById('comments-list');
    
    // Get video ID from URL or data attribute
    const videoId = player ? player.getAttribute('data-video-id') : null;
    
    if (!videoId) {
        console.error('No video ID found');
        return;
    }
    
    // Init functions
    initPlayer();
    loadComments();
    setupActionHandlers();
    
    // Set up player
    function initPlayer() {
        if (!player) return;
        
        // Update view count when video starts playing
        player.addEventListener('playing', () => {
            updateViewCount();
        });
        
        // Log video progress for analytics and history
        player.addEventListener('timeupdate', () => {
            // Only log at certain intervals (e.g., every 15 seconds)
            if (Math.floor(player.currentTime) % 15 === 0 && player.currentTime > 0) {
                logVideoProgress(player.currentTime);
            }
        });
    }
    
    // Update view count
    async function updateViewCount() {
        try {
            if (!AUTH.isLoggedIn()) return;
            
            const response = await fetch(`/api/videos/${videoId}/view`, {
                method: 'POST',
                headers: AUTH.getHeaders()
            });
            
            if (response.ok) {
                const data = await response.json();
                if (videoViews) {
                    videoViews.textContent = `${data.views} views`;
                }
            }
        } catch (error) {
            console.error('Error updating view count:', error);
        }
    }
    
    // Log video progress
    async function logVideoProgress(currentTime) {
        if (!AUTH.isLoggedIn()) return;
        
        try {
            await fetch(`/api/videos/${videoId}/progress`, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                    ...AUTH.getHeaders()
                },
                body: JSON.stringify({
                    position: Math.floor(currentTime),
                    duration: Math.floor(player.duration)
                })
            });
        } catch (error) {
            console.error('Error logging video progress:', error);
        }
    }
    
    // Set up like, dislike, share, save buttons
    function setupActionHandlers() {
        // Like button
        if (likeBtn) {
            likeBtn.addEventListener('click', async () => {
                if (!AUTH.isLoggedIn()) {
                    window.location.href = `/login?redirect=/video/${videoId}`;
                    return;
                }
                
                try {
                    const response = await fetch(`/api/videos/${videoId}/like`, {
                        method: 'POST',
                        headers: AUTH.getHeaders()
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        
                        // Update UI
                        likeBtn.classList.toggle('active', data.liked);
                        if (dislikeBtn) dislikeBtn.classList.remove('active');
                        
                        if (likeCount) likeCount.textContent = data.likes;
                        if (dislikeCount) dislikeCount.textContent = data.dislikes;
                    }
                } catch (error) {
                    console.error('Error liking video:', error);
                }
            });
        }
        
        // Dislike button
        if (dislikeBtn) {
            dislikeBtn.addEventListener('click', async () => {
                if (!AUTH.isLoggedIn()) {
                    window.location.href = `/login?redirect=/video/${videoId}`;
                    return;
                }
                
                try {
                    const response = await fetch(`/api/videos/${videoId}/dislike`, {
                        method: 'POST',
                        headers: AUTH.getHeaders()
                    });
                    
                    if (response.ok) {
                        const data = await response.json();
                        
                        // Update UI
                        dislikeBtn.classList.toggle('active', data.disliked);
                        if (likeBtn) likeBtn.classList.remove('active');
                        
                        if (likeCount) likeCount.textContent = data.likes;
                        if (dislikeCount) dislikeCount.textContent = data.dislikes;
                    }
                } catch (error) {
                    console.error('Error disliking video:', error);
                }
            });
        }
        
        // Share button
        if (shareBtn) {
            shareBtn.addEventListener('click', () => {
                const videoUrl = window.location.href;
                
                // Use Web Share API if available
                if (navigator.share) {
                    navigator.share({
                        title: videoTitle ? videoTitle.textContent : 'Shared video',
                        url: videoUrl
                    }).catch(err => {
                        console.error('Error sharing:', err);
                    });
                } else {
                    // Fallback: copy to clipboard
                    navigator.clipboard.writeText(videoUrl).then(() => {
                        alert('Video URL copied to clipboard!');
                    }).catch(err => {
                        console.error('Error copying URL:', err);
                    });
                }
            });
        }
        
        // Save to playlist button
        if (saveBtn) {
            saveBtn.addEventListener('click', () => {
                if (!AUTH.isLoggedIn()) {
                    window.location.href = `/login?redirect=/video/${videoId}`;
                    return;
                }
                
                // Show playlist selection modal
                // This would be implemented elsewhere
                showPlaylistModal();
            });
        }
        
        // Comment form
        if (commentForm) {
            commentForm.addEventListener('submit', async (e) => {
                e.preventDefault();
                
                if (!AUTH.isLoggedIn()) {
                    window.location.href = `/login?redirect=/video/${videoId}`;
                    return;
                }
                
                const commentText = commentInput.value.trim();
                if (!commentText) return;
                
                try {
                    const response = await fetch(`/api/videos/${videoId}/comments`, {
                        method: 'POST',
                        headers: {
                            'Content-Type': 'application/json',
                            ...AUTH.getHeaders()
                        },
                        body: JSON.stringify({
                            content: commentText
                        })
                    });
                    
                    if (response.ok) {
                        // Clear input
                        commentInput.value = '';
                        
                        // Reload comments
                        await loadComments();
                    }
                } catch (error) {
                    console.error('Error posting comment:', error);
                }
            });
        }
    }
    
    // Load video comments
    async function loadComments() {
        if (!commentsList) return;
        
        try {
            const response = await fetch(`/api/videos/${videoId}/comments`);
            
            if (response.ok) {
                const comments = await response.json();
                
                // Clear existing comments
                commentsList.innerHTML = '';
                
                // Add comments
                if (comments.length === 0) {
                    commentsList.innerHTML = '<div class="text-center text-muted py-4">No comments yet. Be the first to comment!</div>';
                } else {
                    comments.forEach(comment => {
                        const commentEl = createCommentElement(comment);
                        commentsList.appendChild(commentEl);
                    });
                }
            }
        } catch (error) {
            console.error('Error loading comments:', error);
        }
    }
    
    // Create comment element
    function createCommentElement(comment) {
        const commentEl = document.createElement('div');
        commentEl.className = 'comment d-flex mb-3';
        
        const isLoggedIn = AUTH.isLoggedIn();
        const isOwnComment = isLoggedIn && comment.user_id === getUserId();
        
        commentEl.innerHTML = `
            <img src="${comment.profile_picture || '/static/profile_pictures/default.jpg'}" class="rounded-circle me-3" width="40" height="40" alt="${comment.username}">
            <div class="flex-grow-1">
                <div class="d-flex align-items-center mb-1">
                    <a href="/channel/${comment.username}" class="fw-bold text-decoration-none me-2">${comment.username}</a>
                    <small class="text-muted">${formatDate(comment.created_at)}</small>
                    ${isOwnComment ? `
                        <div class="dropdown ms-auto">
                            <button class="btn btn-sm text-muted" type="button" data-bs-toggle="dropdown">
                                <i class="fas fa-ellipsis-v"></i>
                            </button>
                            <ul class="dropdown-menu dropdown-menu-end">
                                <li><button class="dropdown-item edit-comment" data-comment-id="${comment.id}">Edit</button></li>
                                <li><button class="dropdown-item delete-comment" data-comment-id="${comment.id}">Delete</button></li>
                            </ul>
                        </div>
                    ` : ''}
                </div>
                <div class="comment-content">${comment.content}</div>
                <div class="mt-2">
                    <button class="btn btn-sm text-muted me-2 comment-like" data-comment-id="${comment.id}">
                        <i class="far fa-thumbs-up${comment.liked ? ' text-primary' : ''}"></i> ${comment.likes || ''}
                    </button>
                    <button class="btn btn-sm text-muted me-2 comment-dislike" data-comment-id="${comment.id}">
                        <i class="far fa-thumbs-down${comment.disliked ? ' text-danger' : ''}"></i> ${comment.dislikes || ''}
                    </button>
                    <button class="btn btn-sm text-muted comment-reply" data-comment-id="${comment.id}">Reply</button>
                </div>
                <div class="replies mt-3"></div>
            </div>
        `;
        
        // Add event listeners for comment actions
        setupCommentActions(commentEl, comment.id);
        
        return commentEl;
    }
    
    // Add event listeners to comment actions
    function setupCommentActions(commentEl, commentId) {
        // Like comment
        const likeBtn = commentEl.querySelector('.comment-like');
        if (likeBtn) {
            likeBtn.addEventListener('click', async () => {
                if (!AUTH.isLoggedIn()) {
                    window.location.href = `/login?redirect=/video/${videoId}`;
                    return;
                }
                
                try {
                    const response = await fetch(`/api/comments/${commentId}/like`, {
                        method: 'POST',
                        headers: AUTH.getHeaders()
                    });
                    
                    if (response.ok) {
                        // Reload comments to update UI
                        await loadComments();
                    }
                } catch (error) {
                    console.error('Error liking comment:', error);
                }
            });
        }
        
        // Dislike comment
        const dislikeBtn = commentEl.querySelector('.comment-dislike');
        if (dislikeBtn) {
            dislikeBtn.addEventListener('click', async () => {
                if (!AUTH.isLoggedIn()) {
                    window.location.href = `/login?redirect=/video/${videoId}`;
                    return;
                }
                
                try {
                    const response = await fetch(`/api/comments/${commentId}/dislike`, {
                        method: 'POST',
                        headers: AUTH.getHeaders()
                    });
                    
                    if (response.ok) {
                        // Reload comments to update UI
                        await loadComments();
                    }
                } catch (error) {
                    console.error('Error disliking comment:', error);
                }
            });
        }
        
        // Edit comment
        const editBtn = commentEl.querySelector('.edit-comment');
        if (editBtn) {
            editBtn.addEventListener('click', () => {
                const contentEl = commentEl.querySelector('.comment-content');
                const currentContent = contentEl.textContent;
                
                contentEl.innerHTML = `
                    <textarea class="form-control mb-2 edit-comment-textarea">${currentContent}</textarea>
                    <div class="d-flex">
                        <button class="btn btn-sm btn-primary me-2 save-edit">Save</button>
                        <button class="btn btn-sm btn-outline-secondary cancel-edit">Cancel</button>
                    </div>
                `;
                
                // Save edit
                contentEl.querySelector('.save-edit').addEventListener('click', async () => {
                    const newContent = contentEl.querySelector('.edit-comment-textarea').value.trim();
                    if (!newContent) return;
                    
                    try {
                        const response = await fetch(`/api/comments/${commentId}`, {
                            method: 'PUT',
                            headers: {
                                'Content-Type': 'application/json',
                                ...AUTH.getHeaders()
                            },
                            body: JSON.stringify({
                                content: newContent
                            })
                        });
                        
                        if (response.ok) {
                            // Reload comments
                            await loadComments();
                        }
                    } catch (error) {
                        console.error('Error updating comment:', error);
                    }
                });
                
                // Cancel edit
                contentEl.querySelector('.cancel-edit').addEventListener('click', () => {
                    contentEl.textContent = currentContent;
                });
            });
        }
        
        // Delete comment
        const deleteBtn = commentEl.querySelector('.delete-comment');
        if (deleteBtn) {
            deleteBtn.addEventListener('click', async () => {
                if (!confirm('Are you sure you want to delete this comment?')) return;
                
                try {
                    const response = await fetch(`/api/comments/${commentId}`, {
                        method: 'DELETE',
                        headers: AUTH.getHeaders()
                    });
                    
                    if (response.ok) {
                        // Reload comments
                        await loadComments();
                    }
                } catch (error) {
                    console.error('Error deleting comment:', error);
                }
            });
        }
        
        // Reply to comment
        const replyBtn = commentEl.querySelector('.comment-reply');
        if (replyBtn) {
            replyBtn.addEventListener('click', () => {
                if (!AUTH.isLoggedIn()) {
                    window.location.href = `/login?redirect=/video/${videoId}`;
                    return;
                }
                
                const repliesContainer = commentEl.querySelector('.replies');
                
                // Check if reply form already exists
                if (repliesContainer.querySelector('.reply-form')) {
                    return;
                }
                
                // Create reply form
                const replyForm = document.createElement('div');
                replyForm.className = 'reply-form d-flex mt-3';
                replyForm.innerHTML = `
                    <img src="/static/profile_pictures/default.jpg" class="rounded-circle me-2" width="32" height="32" alt="Your profile">
                    <div class="flex-grow-1">
                        <textarea class="form-control mb-2 reply-textarea" placeholder="Add a reply..."></textarea>
                        <div class="d-flex justify-content-end">
                            <button class="btn btn-sm btn-outline-secondary me-2 cancel-reply">Cancel</button>
                            <button class="btn btn-sm btn-primary post-reply">Reply</button>
                        </div>
                    </div>
                `;
                
                repliesContainer.prepend(replyForm);
                
                // Focus textarea
                replyForm.querySelector('.reply-textarea').focus();
                
                // Cancel reply
                replyForm.querySelector('.cancel-reply').addEventListener('click', () => {
                    replyForm.remove();
                });
                
                // Post reply
                replyForm.querySelector('.post-reply').addEventListener('click', async () => {
                    const replyText = replyForm.querySelector('.reply-textarea').value.trim();
                    if (!replyText) return;
                    
                    try {
                        const response = await fetch(`/api/comments/${commentId}/replies`, {
                            method: 'POST',
                            headers: {
                                'Content-Type': 'application/json',
                                ...AUTH.getHeaders()
                            },
                            body: JSON.stringify({
                                content: replyText
                            })
                        });
                        
                        if (response.ok) {
                            // Reload comments
                            await loadComments();
                        }
                    } catch (error) {
                        console.error('Error posting reply:', error);
                    }
                });
            });
        }
    }
    
    // Format date (e.g., "2 hours ago", "3 days ago")
    function formatDate(dateString) {
        const date = new Date(dateString);
        const now = new Date();
        const diff = Math.floor((now - date) / 1000); // Difference in seconds
        
        if (diff < 60) {
            return 'just now';
        } else if (diff < 3600) {
            const minutes = Math.floor(diff / 60);
            return `${minutes} minute${minutes > 1 ? 's' : ''} ago`;
        } else if (diff < 86400) {
            const hours = Math.floor(diff / 3600);
            return `${hours} hour${hours > 1 ? 's' : ''} ago`;
        } else if (diff < 2592000) {
            const days = Math.floor(diff / 86400);
            return `${days} day${days > 1 ? 's' : ''} ago`;
        } else if (diff < 31536000) {
            const months = Math.floor(diff / 2592000);
            return `${months} month${months > 1 ? 's' : ''} ago`;
        } else {
            const years = Math.floor(diff / 31536000);
            return `${years} year${years > 1 ? 's' : ''} ago`;
        }
    }
    
    // Get current user ID
    function getUserId() {
        // This would typically come from the auth system
        // For now, returning null or fetching from user data
        return null;
    }
    
    // Show playlist modal (placeholder)
    function showPlaylistModal() {
        // This would be implemented elsewhere
        alert('Save to playlist feature coming soon!');
    }
}); 