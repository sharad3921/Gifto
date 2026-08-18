// to get current year
function getYear() {
    var currentDate = new Date();
    var currentYear = currentDate.getFullYear();
    document.querySelector("#displayYear").innerHTML = currentYear;
}

getYear();

// owl carousel 

$('.owl-carousel').owlCarousel({
    loop: true,
    margin: 10,
    nav: true,
    autoplay: true,
    autoplayHoverPause: true,
    responsive: {
        0: {
            items: 1
        },
        600: {
            items: 3
        },
        1000: {
            items: 6
        }
    }
})

// Navbar: add class on scroll to reduce visual clutter
function handleNavbarScroll() {
    var nav = document.querySelector('.custom_nav-container');
    if(!nav) return;
    if(window.scrollY > 60) {
        nav.classList.add('navbar-scrolled');
    } else {
        nav.classList.remove('navbar-scrolled');
    }
}
window.addEventListener('load', handleNavbarScroll);
window.addEventListener('scroll', handleNavbarScroll);

// Enhance quantity change UX globally: animate inputs when value changes
function animateQtyInputById(id) {
    try {
        var el = document.getElementById(id);
        if(!el) return;
        el.classList.remove('qty-anim');
        // force reflow
        void el.offsetWidth;
        el.classList.add('qty-anim');
        setTimeout(function(){ el.classList.remove('qty-anim'); }, 300);
    } catch(e){}
}

// Expose helper for existing inline handlers
window.animateQtyInputById = animateQtyInputById;