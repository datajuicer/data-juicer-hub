(function() {
    'use strict';
    
    function initSwitchers() {
        const dropdowns = document.querySelectorAll('.navbar-dropdown');
        
        if (dropdowns.length === 0) {
            console.log('No switcher dropdowns found');
            return;
        }
        
        // Detect if device supports hover
        const hasHover = window.matchMedia('(hover: hover) and (pointer: fine)').matches;
        const isDesktop = window.innerWidth >= 768;
        
        // For touch devices or mobile, use click
        if (!hasHover || !isDesktop) {
            dropdowns.forEach(dropdown => {
                const trigger = dropdown.querySelector('.navbar-dropdown-trigger');
                if (!trigger) return;
                
                // Toggle on click
                trigger.addEventListener('click', function(e) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Close other dropdowns
                    dropdowns.forEach(other => {
                        if (other !== dropdown) {
                            other.classList.remove('active');
                        }
                    });
                    
                    // Toggle current
                    dropdown.classList.toggle('active');
                });
            });
            
            // Close on outside click
            document.addEventListener('click', function(e) {
                if (!e.target.closest('.navbar-dropdown')) {
                    dropdowns.forEach(dropdown => {
                        dropdown.classList.remove('active');
                    });
                }
            });
            
            // Prevent panel clicks from closing
            dropdowns.forEach(dropdown => {
                const panel = dropdown.querySelector('.navbar-dropdown-panel');
                if (panel) {
                    panel.addEventListener('click', function(e) {
                        // Allow link clicks to proceed
                        if (e.target.classList.contains('dropdown-item')) {
                            return;
                        }
                        e.stopPropagation();
                    });
                }
            });
        }
        
        // Keyboard accessibility for all
        dropdowns.forEach(dropdown => {
            const trigger = dropdown.querySelector('.navbar-dropdown-trigger');
            if (!trigger) return;
            
            trigger.addEventListener('keydown', function(e) {
                if (e.key === 'Enter' || e.key === ' ') {
                    e.preventDefault();
                    dropdown.classList.toggle('active');
                } else if (e.key === 'Escape') {
                    dropdown.classList.remove('active');
                    trigger.blur();
                }
            });
        });
        
        console.log('Switcher interactions initialized (hasHover:', hasHover, ', isDesktop:', isDesktop, ')');
    }
    
    // Initialize when DOM is ready
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', initSwitchers);
    } else {
        initSwitchers();
    }
})();
