const swiper = new Swiper(".mpf-swiper", {
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
    el: ".mpf-swiper-pagination",
    clickable: true,
  },
  navigation: {
    nextEl: ".mpf-swiper-next",
    prevEl: ".mpf-swiper-prev",
  },
});

const swiperEl = document.querySelector(".mpf-swiper");

// pausa com mouse
swiperEl.addEventListener("mouseenter", () => swiper.autoplay.stop());
swiperEl.addEventListener("mouseleave", () => swiper.autoplay.start());

// pausa com teclado (acessibilidade)
swiperEl.addEventListener("focusin", () => swiper.autoplay.stop());
swiperEl.addEventListener("focusout", () => swiper.autoplay.start());
