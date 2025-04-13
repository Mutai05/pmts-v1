document.addEventListener('DOMContentLoaded', () => {
    // Sidebar toggle
    const toggleSidebarBtn = document.querySelector('.toggle-sidebar-btn');
    const sidebar = document.querySelector('.sidebar');
    const main = document.querySelector('#main');
    const footer = document.querySelector('#footer');
  
    toggleSidebarBtn.addEventListener('click', () => {
      sidebar.classList.toggle('toggle-sidebar');
      main.classList.toggle('toggle-sidebar');
      footer.classList.toggle('toggle-sidebar');
    });
  
    // Back to top button
    const backToTop = document.querySelector('.back-to-top');
    window.addEventListener('scroll', () => {
      if (window.scrollY > 100) {
        backToTop.classList.add('active');
      } else {
        backToTop.classList.remove('active');
      }
    });
  
    // Clear notifications
    const clearNotifications = document.querySelector('.dropdown-footer a');
    if (clearNotifications) {
      clearNotifications.addEventListener('click', (e) => {
        e.preventDefault();
        document.querySelector('.notifications').innerHTML = '<li class="dropdown-header">No notifications</li>';
        document.querySelector('.badge-number').remove();
      });
    }
  });