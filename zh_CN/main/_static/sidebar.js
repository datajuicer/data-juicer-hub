document.addEventListener('DOMContentLoaded', function() {
    // Check for the existence of the primary sidebar
    const sidebar = document.querySelector('.bd-sidebar-primary:not(.hide-on-wide)');
    
    if (!sidebar) {
        console.log('No primary sidebar found, skipping collapse feature');
        return;
    }
    
    // Locate the starting container of breadcrumb navigation
    const breadcrumbStart = document.querySelector('.header-article-items__start');
    
    if (!breadcrumbStart) {
        console.log('Breadcrumb container not found');
        return;
    }
    
    // Create the sidebar toggle button
    const toggleBtn = document.createElement('button');
    toggleBtn.className = 'sidebar-collapse-toggle';
    toggleBtn.setAttribute('aria-label', 'Collapse sidebar');
    toggleBtn.setAttribute('title', 'Collapse/expand sidebar (Ctrl+B)');
    
    // Use Font Awesome icon for visual indicator
    toggleBtn.innerHTML = '<i class="fa-solid fa-bars"></i>';
    
    // Insert the toggle button at the beginning of the breadcrumb container
    breadcrumbStart.insertBefore(toggleBtn, breadcrumbStart.firstChild);
    
    // Restore collapse state from localStorage
    const savedState = localStorage.getItem('sidebarCollapsed');
    if (savedState === 'true') {
        document.body.classList.add('sidebar-collapsed');
        toggleBtn.setAttribute('aria-label', 'Expand sidebar');
    }
    
    // Toggle sidebar collapse/expand state
    function toggleSidebar() {
        const isCollapsed = document.body.classList.toggle('sidebar-collapsed');
        
        if (isCollapsed) {
            toggleBtn.setAttribute('aria-label', 'Expand sidebar');
            localStorage.setItem('sidebarCollapsed', 'true');
        } else {
            toggleBtn.setAttribute('aria-label', 'Collapse sidebar');
            localStorage.setItem('sidebarCollapsed', 'false');
        }
        
        // Trigger resize event to notify components (e.g., charts, maps) of layout change
        window.dispatchEvent(new Event('resize'));
    }
    
    // Attach click event listener to toggle button
    toggleBtn.addEventListener('click', toggleSidebar);
    
    // Enable keyboard shortcut: Ctrl + B to toggle sidebar
    document.addEventListener('keydown', function(e) {
        if (e.ctrlKey && e.key === 'b') {
            e.preventDefault();
            toggleSidebar();
        }
    });
    
    console.log('Sidebar collapse feature initialized (in header)');
});
