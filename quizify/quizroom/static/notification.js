function createNotification(message, type = 'info') {
  const containerId = 'notification-container';

  // Create container if not present
  let container = document.getElementById(containerId);
  if (!container) {
    container = document.createElement('div');
    container.id = containerId;
    container.style.position = 'fixed';
    container.style.bottom = '20px';
    container.style.right = '20px';
    container.style.zIndex = '9999';
    container.style.display = 'flex';
    container.style.flexDirection = 'column';
    container.style.gap = '6px';
    document.body.appendChild(container);

  }

  // Create notification
  const notification = document.createElement('div');
  const close_button=document.createElement("button");
  close_button.textContent="X";
  close_button.style.backgroundColor="red";
  close_button.style.position='absolute';
  close_button.style.top=0;
  close_button.style.right=0;
  close_button.style.height="100%";
  close_button.style.minWidth="30px";
  
  close_button.onclick=(event=>{
      notification.remove()
  })
  
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
  notification.appendChild(close_button);
  container.appendChild(notification);

  // Auto-remove after 4 seconds
  setTimeout(() => {
    notification.remove();
  }, 4000);
}

window.onload = function(){
const messages=document.querySelectorAll(".msn");
if(messages.length>0){
  console.log(messages)
  for(let m=0;m<messages.length;m++){
    setTimeout(createNotification(messages[m].textContent,messages[m].id),100)
  }
}

};