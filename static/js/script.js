let index = 0;
const slides = document.querySelectorAll('.slides img');
const dots = document.querySelectorAll('.dot');
const total = slides.length;
const prevBtn = document.querySelector('.prev');
const nextBtn = document.querySelector('.next');

function showSlide(i) {
  slides.forEach((slide, n) => {
    slide.classList.remove('active');
    dots[n].classList.remove('active');
    if (n === i) {
      slide.classList.add('active');
      dots[n].classList.add('active');
    }
  });
}

function nextSlide() {
  index = (index + 1) % total;
  showSlide(index);
}

function prevSlide() {
  index = (index - 1 + total) % total;
  showSlide(index);
}

// Clic en indicadores
dots.forEach((dot, i) => {
  dot.addEventListener('click', () => {
    index = i;
    showSlide(index);
  });
});

nextBtn.addEventListener('click', nextSlide);
prevBtn.addEventListener('click', prevSlide);

// Auto cambio cada 5 segundos
setInterval(nextSlide, 5000);

// Mostrar la primera imagen
showSlide(index);
