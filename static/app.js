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
    const movieCards = [...document.querySelectorAll("[data-movie-card]")];
    const movieShelf = document.querySelector(".movie-shelf");
    const movieSearch = document.querySelector("#movie-search");
    const favoritesFilter = document.querySelector("#favorites-filter");
    const favoritesCount = document.querySelector("#favorites-count");
    const movieResults = document.querySelector("#movie-results");
    const noMovies = document.querySelector("#no-movies");
    const carouselButtons = document.querySelectorAll("[data-carousel-direction]");
    const favoriteStorageKey = "cineflix-favorites-v1";
    let favorites = [];

    try {
        const savedFavorites = JSON.parse(localStorage.getItem(favoriteStorageKey) || "[]");
        if (Array.isArray(savedFavorites) && savedFavorites.every((title) => typeof title === "string")) {
            favorites = savedFavorites;
        }
    } catch (error) {
        console.error("No se pudieron cargar las películas favoritas.", error);
    }

    const updateFavoriteButtons = () => {
        movieCards.forEach((card) => {
            const button = card.querySelector("[data-favorite]");
            const isFavorite = favorites.includes(button.dataset.favorite);
            button.setAttribute("aria-pressed", String(isFavorite));
            button.textContent = isFavorite ? "Guardada" : "Guardar";
            button.setAttribute(
                "aria-label",
                `${isFavorite ? "Quitar" : "Guardar"} ${button.dataset.favorite} ${isFavorite ? "de" : "en"} favoritas`,
            );
        });
        if (favoritesCount) favoritesCount.textContent = String(favorites.length);
    };

    const filterMovies = () => {
        const query = movieSearch?.value.trim().toLocaleLowerCase("es") || "";
        const favoritesOnly = favoritesFilter?.getAttribute("aria-pressed") === "true";
        let visibleCount = 0;
        movieCards.forEach((card) => {
            const title = card.dataset.title.toLocaleLowerCase("es");
            const genre = card.dataset.genre.toLocaleLowerCase("es");
            const isFavorite = favorites.includes(card.dataset.title);
            const matches = (!query || title.includes(query) || genre.includes(query))
                && (!favoritesOnly || isFavorite);
            card.hidden = !matches;
            if (matches) visibleCount += 1;
        });
        if (noMovies) noMovies.hidden = visibleCount > 0;
        if (movieResults) {
            movieResults.textContent = `${visibleCount} ${visibleCount === 1 ? "película" : "películas"}`;
        }
        updateCarouselButtons();
    };

    const syncMovieSelection = () => {
        if (!movieSelect) return;
        movieCards.forEach((card) => {
            const selected = card.dataset.title === movieSelect.value;
            card.querySelector(".movie-select").setAttribute("aria-pressed", String(selected));
            card.classList.toggle("is-selected", selected);
        });
    };

    movieCards.forEach((card) => {
        const selectButton = card.querySelector(".movie-select");
        selectButton.addEventListener("click", () => {
            movieSelect.value = card.dataset.title;
            movieSelect.dispatchEvent(new Event("change", { bubbles: true }));
            document.querySelector("#booking-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
        });
        card.querySelector("[data-favorite]").addEventListener("click", (event) => {
            const title = event.currentTarget.dataset.favorite;
            favorites = favorites.includes(title)
                ? favorites.filter((favorite) => favorite !== title)
                : [...favorites, title];
            try {
                localStorage.setItem(favoriteStorageKey, JSON.stringify(favorites));
            } catch (error) {
                console.error("No se pudieron guardar las películas favoritas.", error);
            }
            updateFavoriteButtons();
            filterMovies();
        });
        card.querySelector("[data-show-details]").addEventListener("click", () => {
            const dialog = document.querySelector("#movie-dialog");
            document.querySelector("#dialog-title").textContent = card.dataset.title;
            document.querySelector("#dialog-genre").textContent = card.dataset.genre;
            document.querySelector("#dialog-synopsis").textContent = card.dataset.synopsis;
            const poster = document.querySelector("#dialog-poster");
            poster.src = card.dataset.poster;
            poster.alt = `Póster de ${card.dataset.title}`;
            const trailer = document.querySelector("#dialog-trailer");
            trailer.href = `https://www.youtube.com/results?search_query=${card.dataset.trailerQuery}`;
            const dialogSelect = document.querySelector("#dialog-select");
            dialogSelect.onclick = () => {
                movieSelect.value = card.dataset.title;
                movieSelect.dispatchEvent(new Event("change", { bubbles: true }));
                dialog.close();
                document.querySelector("#booking-form")?.scrollIntoView({ behavior: "smooth", block: "start" });
            };
            dialog.showModal();
        });
    });

    document.querySelector("[data-close-dialog]")?.addEventListener("click", () => {
        document.querySelector("#movie-dialog").close();
    });
    document.querySelector("#movie-dialog")?.addEventListener("click", (event) => {
        if (event.target === event.currentTarget) event.currentTarget.close();
    });

    movieSelect?.addEventListener("change", () => {
        syncMovieSelection();
    });
    movieSearch?.addEventListener("input", filterMovies);
    favoritesFilter?.addEventListener("click", () => {
        const isPressed = favoritesFilter.getAttribute("aria-pressed") === "true";
        favoritesFilter.setAttribute("aria-pressed", String(!isPressed));
        document.querySelector("#favorites-label").textContent = isPressed ? "Ver favoritas" : "Ver todas";
        filterMovies();
    });
    updateFavoriteButtons();
    filterMovies();
    syncMovieSelection();

    function updateCarouselButtons() {
        if (!movieShelf) return;
        const visibleCards = movieCards.filter((card) => !card.hidden);
        const maxScroll = movieShelf.scrollWidth - movieShelf.clientWidth;
        carouselButtons.forEach((button) => {
            const direction = Number(button.dataset.carouselDirection);
            button.disabled = visibleCards.length === 0
                || (direction < 0 ? movieShelf.scrollLeft <= 4 : movieShelf.scrollLeft >= maxScroll - 4);
        });
    }

    if (movieShelf && carouselButtons.length) {
        carouselButtons.forEach((button) => {
            button.addEventListener("click", () => {
                const card = movieCards.find((candidate) => !candidate.hidden);
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

    const bookingForm = document.querySelector("#booking-form");
    const seatSelector = document.querySelector("#seat-selector");
    const seatGrid = document.querySelector("#seat-grid");
    const seatCount = document.querySelector("#seat-count");
    const seatMessage = document.querySelector("#seat-message");
    const ticketInput = document.querySelector("#boletos");
    if (bookingForm && seatSelector && seatGrid && seatCount && seatMessage && ticketInput) {
        const showInputs = ["#pelicula", "#fecha", "#horario", "#sala"]
            .map((selector) => document.querySelector(selector));
        let selectedSeats = [];
        let restoredSeats = [];
        let requestNumber = 0;

        try {
            restoredSeats = JSON.parse(seatSelector.dataset.selectedSeats || "[]");
            if (!Array.isArray(restoredSeats)) restoredSeats = [];
        } catch (error) {
            console.error("No se pudieron restaurar los asientos seleccionados.", error);
            restoredSeats = [];
        }

        const getShowParameters = () => Object.fromEntries(
            showInputs.map((input) => [input.name, input.value]),
        );

        const updateSeatCount = () => {
            const requiredSeats = Number(ticketInput.value) || 0;
            seatCount.textContent = `${selectedSeats.length} de ${requiredSeats} asientos elegidos`;
            const hiddenInputs = bookingForm.querySelectorAll(".seat-hidden-input");
            hiddenInputs.forEach((input) => input.remove());
            selectedSeats.forEach((seat) => {
                const input = document.createElement("input");
                input.type = "hidden";
                input.name = "asientos";
                input.value = seat;
                input.className = "seat-hidden-input";
                bookingForm.append(input);
            });
        };

        const renderSeats = (payload) => {
            const occupied = new Set(payload.ocupados);
            const availableSeats = [];
            seatGrid.replaceChildren();
            payload.filas.forEach((row) => {
                const rowLabel = document.createElement("span");
                rowLabel.className = "seat-row-label";
                rowLabel.textContent = row;
                seatGrid.append(rowLabel);
                for (let number = 1; number <= payload.asientos_por_fila; number += 1) {
                    const seat = `${row}${number}`;
                    const button = document.createElement("button");
                    button.type = "button";
                    button.className = "seat-button";
                    button.textContent = String(number);
                    button.setAttribute("aria-label", `Asiento ${seat}`);
                    if (occupied.has(seat)) {
                        button.disabled = true;
                        button.classList.add("is-occupied");
                        button.setAttribute("aria-label", `Asiento ${seat}, ocupado`);
                    } else {
                        availableSeats.push(seat);
                        button.setAttribute("aria-pressed", String(selectedSeats.includes(seat)));
                        button.classList.toggle("is-selected", selectedSeats.includes(seat));
                        button.addEventListener("click", () => {
                            if (selectedSeats.includes(seat)) {
                                selectedSeats = selectedSeats.filter((selected) => selected !== seat);
                            } else if (selectedSeats.length < (Number(ticketInput.value) || 0)) {
                                selectedSeats = [...selectedSeats, seat];
                            } else {
                                seatMessage.textContent = `Ya elegiste ${selectedSeats.length} asientos. Cambia la cantidad de boletos para elegir más.`;
                                return;
                            }
                            button.setAttribute("aria-pressed", String(selectedSeats.includes(seat)));
                            button.classList.toggle("is-selected", selectedSeats.includes(seat));
                            updateSeatCount();
                            seatMessage.textContent = selectedSeats.length === Number(ticketInput.value)
                                ? "Tus asientos están listos."
                                : `Elige ${Number(ticketInput.value) - selectedSeats.length} asiento(s) más.`;
                        });
                    }
                    seatGrid.append(button);
                }
            });
            if (restoredSeats.length) {
                selectedSeats = restoredSeats.filter((seat) => availableSeats.includes(seat))
                    .slice(0, Number(ticketInput.value) || 0);
                restoredSeats = [];
                renderSeats(payload);
                return;
            }
            selectedSeats = selectedSeats.filter((seat) => availableSeats.includes(seat))
                .slice(0, Number(ticketInput.value) || 0);
            updateSeatCount();
            seatMessage.textContent = `${payload.disponibles} asientos disponibles. Selecciona uno por cada boleto.`;
        };

        async function updateSeatMap() {
            const parameters = getShowParameters();
            const hasShow = Object.values(parameters).every(Boolean);
            const currentRequest = ++requestNumber;
            if (!hasShow) {
                seatSelector.hidden = true;
                seatGrid.replaceChildren();
                selectedSeats = [];
                updateSeatCount();
                seatMessage.textContent = "Selecciona película, fecha, horario y sala para ver la disponibilidad.";
                return;
            }
            seatSelector.hidden = false;
            seatMessage.textContent = "Consultando disponibilidad...";
            seatGrid.replaceChildren();
            const query = new URLSearchParams(parameters);
            try {
                const response = await fetch(`${seatSelector.dataset.apiUrl}?${query}`);
                const payload = await response.json();
                if (!response.ok) throw new Error(payload.error || "No se pudo consultar la disponibilidad.");
                if (currentRequest !== requestNumber) return;
                renderSeats(payload);
            } catch (error) {
                if (currentRequest !== requestNumber) return;
                seatGrid.replaceChildren();
                seatMessage.textContent = `No se pudo cargar el mapa de asientos: ${error.message}`;
            }
        }

        showInputs.forEach((input) => input.addEventListener("change", () => {
            selectedSeats = [];
            updateSeatCount();
            updateSeatMap();
        }));
        ticketInput.addEventListener("change", () => {
            selectedSeats = selectedSeats.slice(0, Number(ticketInput.value) || 0);
            updateSeatCount();
            updateSeatMap();
        });
        bookingForm.addEventListener("submit", (event) => {
            if (selectedSeats.length !== Number(ticketInput.value)) {
                event.preventDefault();
                seatMessage.textContent = `Elige exactamente ${ticketInput.value} asiento(s) antes de confirmar.`;
                seatSelector.scrollIntoView({ behavior: "smooth", block: "center" });
            }
        });
        updateSeatCount();
        updateSeatMap();
    }
});
