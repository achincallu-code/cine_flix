document.addEventListener("DOMContentLoaded", () => {
    document.querySelectorAll(".delete-form").forEach((form) => {
        form.addEventListener("submit", (event) => {
            const message = form.dataset.confirm || "¿Deseas continuar?";
            if (!window.confirm(message)) event.preventDefault();
        });
    });

    const dateInput = document.querySelector("#fecha");
    if (dateInput && !dateInput.value) {
        dateInput.min = new Date().toISOString().slice(0, 10);
    }

    const movieSelect = document.querySelector("#pelicula");
    const movieCards = document.querySelectorAll(".movie-card");
    const syncMovieCards = () => {
        movieCards.forEach((card) => {
            card.setAttribute("aria-pressed", String(card.dataset.movie === movieSelect.value));
        });
    };

    if (movieSelect && movieCards.length) {
        movieCards.forEach((card) => {
            card.addEventListener("click", () => {
                movieSelect.value = card.dataset.movie;
                syncMovieCards();
            });
        });
        movieSelect.addEventListener("change", syncMovieCards);
        syncMovieCards();
    }

    const movieShelf = document.querySelector(".movie-shelf");
    const carouselButtons = document.querySelectorAll("[data-carousel-direction]");
    if (movieShelf && carouselButtons.length) {
        const updateCarouselButtons = () => {
            const maxScroll = movieShelf.scrollWidth - movieShelf.clientWidth;
            carouselButtons.forEach((button) => {
                const direction = Number(button.dataset.carouselDirection);
                button.disabled = direction < 0
                    ? movieShelf.scrollLeft <= 4
                    : movieShelf.scrollLeft >= maxScroll - 4;
            });
        };

        carouselButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const card = movieShelf.querySelector(".movie-card");
                const gap = Number.parseFloat(getComputedStyle(movieShelf).gap) || 0;
                const step = card ? card.getBoundingClientRect().width + gap : movieShelf.clientWidth;
                movieShelf.scrollBy({
                    left: step * Number(button.dataset.carouselDirection),
                    behavior: "smooth",
                });
            });
        });
        movieShelf.addEventListener("scroll", updateCarouselButtons, { passive: true });
        window.addEventListener("resize", updateCarouselButtons);
        updateCarouselButtons();
    }
});
