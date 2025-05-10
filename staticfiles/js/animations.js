document.addEventListener("DOMContentLoaded", () => {
    // Initialize AOS with proper settings
    if (typeof AOS !== "undefined") {
      AOS.init({
        duration: 800,
        once: true,
        offset: 100,
        disable: window.innerWidth < 768 ? true : false,
      });
    }
  
    // Add classes to elements for animations
    const heroImage = document.querySelector(".hero-section img");
    if (heroImage) {
      heroImage.classList.add("hero-image");
    }
  
    // Add classes to floating coins
    const floatingCoins = document.querySelectorAll(".floating-coin");
    if (floatingCoins.length > 0) {
      floatingCoins.forEach((coin) => {
        coin.classList.add("animate-float");
      });
    }
  
    // Fix for staggered animations
    const staggerContainers = document.querySelectorAll(".stagger-reveal");
    staggerContainers.forEach((container) => {
      const items = container.querySelectorAll("*");
      items.forEach((item, index) => {
        // Make sure items are visible first
        item.style.opacity = "1";
        // Then add animation with delay
        item.style.animationDelay = `${index * 0.1}s`;
        item.classList.add("animate-fade-up");
      });
    });
  
    // Ensure all AOS elements are visible if animation fails
    setTimeout(() => {
      document.querySelectorAll("[data-aos]").forEach((el) => {
        if (window.getComputedStyle(el).opacity === "0") {
          el.style.opacity = "1";
          el.style.transform = "none";
        }
      });
    }, 2000);
  
    // Mobile Menu Toggle
    const mobileMenuBtn = document.getElementById("mobileMenuBtn");
    const mobileMenu = document.getElementById("mobileMenu");
  
    if (mobileMenuBtn && mobileMenu) {
      mobileMenuBtn.addEventListener("click", () => {
        mobileMenu.classList.toggle("hidden");
      });
    }
  
    // Dark Mode Toggle - Enhanced Version
    const darkModeToggle = document.querySelector(".dark-mode-toggle");
    const body = document.body;
  
    // Function to set theme
    const setTheme = (isDark) => {
      if (isDark) {
        body.classList.add("dark");
        localStorage.setItem("darkMode", "true");
      } else {
        body.classList.remove("dark");
        localStorage.setItem("darkMode", "false");
      }
    };
  
    // Check for saved theme preference or system preference
    const savedTheme = localStorage.getItem("darkMode");
    if (savedTheme === "true") {
      setTheme(true);
    } else if (savedTheme === "false") {
      setTheme(false);
    } else {
      // Check system preference if no saved preference
      const prefersDark = window.matchMedia("(prefers-color-scheme: dark)").matches;
      setTheme(prefersDark);
    }
  
    if (darkModeToggle) {
      darkModeToggle.addEventListener("click", () => {
        const isDark = body.classList.contains("dark");
        setTheme(!isDark);
      });
    }
  });
  