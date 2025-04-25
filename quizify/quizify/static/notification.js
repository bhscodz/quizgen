function createNotification(message, type = 'info') {
    const containerId = 'notification-container';
  
    // Create container if not present
    let container = document.getElementById(containerId);
    if (!container) {
      container = document.createElement('div');
      container.id = containerId;
      container.style.position = 'fixed';
      container.style.top = '20px';
      container.style.right = '20px';
      container.style.zIndex = '9999';
      container.style.display = 'flex';
      container.style.flexDirection = 'column';
      container.style.gap = '10px';
      document.body.appendChild(container);
    }
  
    // Create notification
    const notification = document.createElement('div');
    notification.className = `notification ${type}`;
    notification.style.padding = '10px 15px';
    notification.style.backgroundColor = type === 'success' ? '#4caf50' :
                                         type === 'error' ? '#f44336' :
                                         type === 'warning' ? '#ff9800' : '#2196f3';
    notification.style.color = 'white';
    notification.style.borderRadius = '5px';
    notification.style.boxShadow = '0 2px 8px rgba(0, 0, 0, 0.2)';
    notification.style.minWidth = '200px';
    notification.textContent = message;
  
    container.appendChild(notification);
  
    // Auto-remove after 4 seconds
    setTimeout(() => {
      notification.remove();
    }, 4000);
  }