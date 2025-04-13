/**
 * Main JavaScript File
 */
(function() {
  "use strict";

  /**
   * Mobile menu toggle icon animation
   */
  function setupMobileMenuToggle() {
    const navbarToggler = document.querySelector('.navbar-toggler');
    if (navbarToggler) {
      const navbarIcon = navbarToggler.querySelector('i');
      navbarToggler.addEventListener('click', function() {
        if (navbarIcon.classList.contains('bi-list')) {
          navbarIcon.classList.remove('bi-list');
          navbarIcon.classList.add('bi-x');
        } else {
          navbarIcon.classList.remove('bi-x');
          navbarIcon.classList.add('bi-list');
        }
      });
    }
  }

  /**
   * Initialize dropdown animations
   */
  function initDropdowns() {
    document.querySelectorAll('.dropdown').forEach(dropdown => {
      const dropdownMenu = dropdown.querySelector('.dropdown-menu');
      
      dropdown.addEventListener('show.bs.dropdown', function() {
        dropdownMenu.style.opacity = '0';
        dropdownMenu.style.transform = 'translateY(-10px)';
      });
      
      dropdown.addEventListener('shown.bs.dropdown', function() {
        dropdownMenu.style.opacity = '1';
        dropdownMenu.style.transform = 'translateY(0)';
        dropdownMenu.style.transition = 'all 0.2s ease-out';
      });
      
      dropdown.addEventListener('hide.bs.dropdown', function() {
        dropdownMenu.style.opacity = '0';
        dropdownMenu.style.transform = 'translateY(-10px)';
      });
    });
  }

  /**
   * Apply .scrolled class to the body as the page is scrolled down
   */
  function toggleScrolled() {
    const selectBody = document.querySelector('body');
    const selectHeader = document.querySelector('.navbar');
    if (!selectHeader.classList.contains('scroll-up-sticky') && 
        !selectHeader.classList.contains('sticky-top') && 
        !selectHeader.classList.contains('fixed-top')) return;
    window.scrollY > 100 ? selectBody.classList.add('scrolled') : selectBody.classList.remove('scrolled');
  }

  /**
   * Scroll top button
   */
  function setupScrollTop() {
    const scrollTop = document.querySelector('.scroll-top');
    if (!scrollTop) return;

    function toggleScrollTop() {
      window.scrollY > 100 ? scrollTop.classList.add('active') : scrollTop.classList.remove('active');
    }

    scrollTop.addEventListener('click', (e) => {
      e.preventDefault();
      window.scrollTo({
        top: 0,
        behavior: 'smooth'
      });
    });

    window.addEventListener('load', toggleScrollTop);
    document.addEventListener('scroll', toggleScrollTop);
  }

  /**
   * Preloader
   */
  function setupPreloader() {
    const preloader = document.querySelector('#preloader');
    if (preloader) {
      window.addEventListener('load', () => {
        setTimeout(() => {
          preloader.style.transition = 'opacity 0.5s ease';
          preloader.style.opacity = '0';
          setTimeout(() => preloader.remove(), 500);
        }, 500);
      });
    }
  }

  /**
   * Animation on scroll function and init
   */
  function initAOS() {
    if (typeof AOS !== 'undefined') {
      AOS.init({
        duration: 600,
        easing: 'ease-in-out',
        once: true,
        mirror: false
      });
    }
  }

  /**
   * Initialize all components when DOM is loaded
   */
  document.addEventListener('DOMContentLoaded', function() {
    setupMobileMenuToggle();
    initDropdowns();
    setupScrollTop();
    setupPreloader();
  });

  /**
   * Initialize AOS when window is fully loaded
   */
  window.addEventListener('load', function() {
    initAOS();
    
    // Initialize other components that need window load
    document.dispatchEvent(new Event('initSwiper'));
    document.dispatchEvent(new Event('initIsotope'));
  });

  /**
   * Initialize glightbox
   */
  if (typeof GLightbox !== 'undefined') {
    const glightbox = GLightbox({
      selector: '.glightbox'
    });
  }

  /**
   * Auto generate the carousel indicators
   */
  document.querySelectorAll('.carousel-indicators').forEach((carouselIndicator) => {
    const carousel = carouselIndicator.closest('.carousel');
    if (!carousel) return;
    
    carousel.querySelectorAll('.carousel-item').forEach((carouselItem, index) => {
      if (index === 0) {
        carouselIndicator.innerHTML += `<li data-bs-target="#${carousel.id}" data-bs-slide-to="${index}" class="active"></li>`;
      } else {
        carouselIndicator.innerHTML += `<li data-bs-target="#${carousel.id}" data-bs-slide-to="${index}"></li>`;
      }
    });
  });

  /**
   * Initialize isotope layout and filters
   */
  document.addEventListener('initIsotope', function() {
    document.querySelectorAll('.isotope-layout').forEach(function(isotopeItem) {
      let layout = isotopeItem.getAttribute('data-layout') ?? 'masonry';
      let filter = isotopeItem.getAttribute('data-default-filter') ?? '*';
      let sort = isotopeItem.getAttribute('data-sort') ?? 'original-order';

      let initIsotope;
      imagesLoaded(isotopeItem.querySelector('.isotope-container'), function() {
        initIsotope = new Isotope(isotopeItem.querySelector('.isotope-container'), {
          itemSelector: '.isotope-item',
          layoutMode: layout,
          filter: filter,
          sortBy: sort
        });
      });

      isotopeItem.querySelectorAll('.isotope-filters li').forEach(function(filters) {
        filters.addEventListener('click', function() {
          isotopeItem.querySelector('.isotope-filters .filter-active').classList.remove('filter-active');
          this.classList.add('filter-active');
          initIsotope.arrange({
            filter: this.getAttribute('data-filter')
          });
          if (typeof AOS !== 'undefined') {
            AOS.refresh();
          }
        }, false);
      });
    });
  });

  /**
   * Animate the skills items on reveal
   */
  document.querySelectorAll('.skills-animation').forEach((item) => {
    new Waypoint({
      element: item,
      offset: '80%',
      handler: function(direction) {
        let progress = item.querySelectorAll('.progress .progress-bar');
        progress.forEach(el => {
          el.style.width = el.getAttribute('aria-valuenow') + '%';
        });
      }
    });
  });

  /**
   * Initialize swiper sliders
   */
  document.addEventListener('initSwiper', function() {
    document.querySelectorAll(".init-swiper").forEach(function(swiperElement) {
      let config = JSON.parse(
        swiperElement.querySelector(".swiper-config").innerHTML.trim()
      );

      if (swiperElement.classList.contains("swiper-tab")) {
        initSwiperWithCustomPagination(swiperElement, config);
      } else {
        new Swiper(swiperElement, config);
      }
    });
  });

  function initSwiperWithCustomPagination(swiperElement, config) {
    // Custom swiper initialization logic if needed
    new Swiper(swiperElement, config);
  }

  // Initialize scroll event listeners
  document.addEventListener('scroll', toggleScrolled);
  window.addEventListener('load', toggleScrolled);
})();

document.addEventListener('DOMContentLoaded', function () {
  const toggler = document.querySelector('.navbar-toggler');
  const openIcon = toggler.querySelector('.toggler-icon-open');
  const closeIcon = toggler.querySelector('.toggler-icon-close');

  toggler.addEventListener('click', function () {
    openIcon.classList.toggle('d-none');
    closeIcon.classList.toggle('d-none');
  });
});