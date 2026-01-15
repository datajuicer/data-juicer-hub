(function() {
    'use strict';
    
    // Check if on desktop
    function isDesktop() {
        return window.innerWidth >= 960;
    }
    
    // Check if sidebar exists
    function hasSidebar() {
        const sidebar = document.querySelector('.bd-sidebar-primary:not(.hide-on-wide)');
        return sidebar !== null;
    }
    
    function initSidebarCollapse() {
        if (!hasSidebar()) {
            console.log('No collapsible sidebar found');
            return;
        }
        
        const breadcrumbStart = document.querySelector('.header-article-items__start');
        if (!breadcrumbStart) {
            console.warn('Breadcrumb container not found');
            return;
        }
        
        // Create toggle button
        const toggleBtn = document.createElement('button');
        toggleBtn.className = 'sidebar-collapse-toggle';
        toggleBtn.setAttribute('aria-label', 'Collapse sidebar');
        toggleBtn.setAttribute('title', 'Collapse/expand sidebar (Ctrl+B)');
        
        // Use Font Awesome icon for visual indicator
        toggleBtn.innerHTML = '<i class="fas fa-bars"></i>';
        
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
        
        // Click handler
        toggleBtn.addEventListener('click', toggleSidebar);
        
        // Keyboard shortcut: Ctrl+B
        document.addEventListener('keydown', function(e) {
            if (e.ctrlKey && e.key === 'b') {
                e.preventDefault();
                toggleSidebar();
            }
        });
        
        // Handle window resize
        let resizeTimer;
        window.addEventListener('resize', function() {
            clearTimeout(resizeTimer);
            resizeTimer = setTimeout(function() {
                if (!isDesktop()) {
                    // Remove collapse state on mobile
                    document.body.classList.remove('sidebar-collapsed');
                } else {
                    // Restore saved state on desktop
                    const saved = localStorage.getItem('sidebarCollapsed');
                    if (saved === 'true') {
                        document.body.classList.add('sidebar-collapsed');
                    }
                }
            }, 250);
        });
        
        console.log('Sidebar collapse initialized');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSidebarCollapse);
    } else {
        initSidebarCollapse();
    }
})();
