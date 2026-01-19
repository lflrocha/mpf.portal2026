const swiper = new Swiper(".mpf-swiper-aside", {
  slidesPerView: 1,
  spaceBetween: 16,
  loop: true,
  speed: 700,
  autoplay: {
    delay: 4500,
    disableOnInteraction: false,
  },
  a11y: { enabled: true },
  pagination: {
    el: ".mpf-swiper-aside-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".mpf-swiper-aside-next",
    prevEl: ".mpf-swiper-aside-prev",
  },
});

const swiperEl = document.querySelector(".mpf-swiper-aside");

// pausa com mouse
swiperEl.addEventListener("mouseenter", () => swiper.autoplay.stop());
swiperEl.addEventListener("mouseleave", () => swiper.autoplay.start());

// pausa com teclado (acessibilidade)
swiperEl.addEventListener("focusin", () => swiper.autoplay.stop());
swiperEl.addEventListener("focusout", () => swiper.autoplay.start());
