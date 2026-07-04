// ===============================
// GLOBALS
// ===============================
let priceChart = null;
let isLoading = false;

// ===============================
// PREDICT FUNCTION (UPGRADED)
// ===============================
function predict() {

    // 🚫 Prevent double click
    if (isLoading) return;

    const lag1 = document.getElementById("lag1").value;
    const lag2 = document.getElementById("lag2").value;
    const lag3 = document.getElementById("lag3").value;
    const stock = document.getElementById("stock").value;
    const modelType = document.querySelector('input[name="model"]:checked').value;

    // ===============================
    // BASIC VALIDATION (OLD FEATURE)
    // ===============================
    if (!lag1 || !lag2 || !lag3) {
        document.getElementById("price").innerText = "Enter all values";
        document.getElementById("trend").innerText = "";
        if (document.getElementById("confidence"))
            document.getElementById("confidence").innerText = "";
        if (document.getElementById("explanation"))
            document.getElementById("explanation").innerText = "";
        return;
    }

    // ===============================
    // UI LOADING STATE (NEW)
    // ===============================
    const btn = document.getElementById("predictBtn");
    const status = document.getElementById("status");

    isLoading = true;
    if (btn) btn.disabled = true;

    if (status) {
        status.innerText =
            modelType === "dl"
                ? "🧠 Running Deep Learning model… please wait"
                : "⚙️ Running Machine Learning model…";
    }

    document.getElementById("price").innerText = "Predicting...";
    document.getElementById("trend").innerText = "";

    // ===============================
    // FETCH REQUEST
    // ===============================
    fetch("/predict", {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({
            stock: stock,
            model_type: modelType,
            lag_1: lag1,
            lag_2: lag2,
            lag_3: lag3
        })
    })
        .then(response => response.json())
        .then(data => {

            // ===============================
            // BACKEND ERROR HANDLING (OLD)
            // ===============================
            if (data.error) {
                document.getElementById("price").innerText = "Backend Error";
                document.getElementById("trend").innerText = data.error;
                return;
            }

            // ===============================
            // UPDATE TEXT OUTPUTS (OLD)
            // ===============================
            const priceEl = document.getElementById("price");
            animateNumber(priceEl, 0, data.predicted_price);


            document.getElementById("trend").innerText =
                "Trend: " + data.trend;

            if (document.getElementById("confidence")) {
                document.getElementById("confidence").innerText =
                    "Confidence Level: " + data.confidence + "%";
            }

            if (document.getElementById("explanation")) {
                document.getElementById("explanation").innerText =
                    data.explanation;
            }

            if (document.getElementById("summary") && data.market_summary) {
                document.getElementById("summary").innerText =
                    data.market_summary;
            }

            // ===============================
            // DRAW 60-DAY DATE-AWARE CHART
            // ===============================
            if (data.history_60 && data.dates_60) {
                drawChart(data.dates_60, data.history_60, data.predicted_price);
            } else if (data.history_60) {
                // fallback (old backend)
                drawChartSimple(data.history_60, data.predicted_price);
            }

        })
        .catch(error => {
            console.error("Fetch error:", error);
            document.getElementById("price").innerText = "Connection Failed";
        })
        .finally(() => {
            // ===============================
            // RESET UI STATE
            // ===============================
            isLoading = false;
            if (btn) btn.disabled = false;
            if (status) status.innerText = "Prediction completed ✔";
        });
}

// ===============================
// DATE-AWARE CHART (NEW)
// ===============================
function drawChart(dates, history, predictedPrice) {
    const ctx = document.getElementById("priceChart").getContext("2d");
    const values = [...history, predictedPrice];

    if (priceChart) priceChart.destroy();

    priceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: dates,
            datasets: [{
                label: "Stock Price",
                data: values,
                borderColor: "#00c6ff",
                backgroundColor: "rgba(0,198,255,0.15)",
                borderWidth: 2,
                tension: 0.4,
                pointRadius: values.map((_, i) =>
                    i === values.length - 1 ? 6 : 0
                ),
                pointBackgroundColor: values.map((_, i) =>
                    i === values.length - 1 ? "#ff4d4d" : "transparent"
                )
            }]
        },
        options: {
            responsive: true,
            plugins: { legend: { display: false } },
            scales: {
                x: { display: true },
                y: { beginAtZero: false }
            }
        }
    });
}

// ===============================
// FALLBACK CHART (OLD FEATURE)
// ===============================
function drawChartSimple(history, predictedPrice) {
    const ctx = document.getElementById("priceChart").getContext("2d");
    const labels = history.map((_, i) => `Day ${i + 1}`).concat("Prediction");
    const values = [...history, predictedPrice];

    if (priceChart) priceChart.destroy();

    priceChart = new Chart(ctx, {
        type: "line",
        data: {
            labels: labels,
            datasets: [{
                data: values,
                borderColor: "#00c6ff",
                borderWidth: 2,
                tension: 0.4
            }]
        }
    });
}
// ===============================
// MODEL CARD HIGHLIGHT
// ===============================
const mlCard = document.getElementById("mlCard");
const dlCard = document.getElementById("dlCard");

document.querySelectorAll('input[name="model"]').forEach(radio => {
    radio.addEventListener("change", () => {
        if (radio.value === "ml") {
            mlCard.classList.add("active");
            dlCard.classList.remove("active");
        } else {
            dlCard.classList.add("active");
            mlCard.classList.remove("active");
        }
    });
});

// Initial highlight
mlCard.classList.add("active");
// ===============================
// ANIMATED NUMBER COUNTER
// ===============================
function animateNumber(element, start, end, duration = 800) {
    let startTime = null;
    function step(timestamp) {
        if (!startTime) startTime = timestamp;
        const progress = Math.min((timestamp - startTime) / duration, 1);
        const value = Math.floor(progress * (end - start) + start);
        element.innerText = "₹ " + value.toLocaleString(); // Matches updated UI

        if (progress < 1) {
            window.requestAnimationFrame(step);
        } else {
            element.innerText = "₹ " + end.toLocaleString(undefined, {minimumFractionDigits: 2});
        }
    }
    window.requestAnimationFrame(step);
}
// ===============================
// GLASS TILT EFFECT
// ===============================
document.querySelectorAll(".glass").forEach(card => {
    card.addEventListener("mousemove", (e) => {
        const rect = card.getBoundingClientRect();
        const x = e.clientX - rect.left;
        const y = e.clientY - rect.top;

        const centerX = rect.width / 2;
        const centerY = rect.height / 2;

        const rotateX = -(y - centerY) / 20;
        const rotateY = (x - centerX) / 20;

        card.style.transform =
            `rotateX(${rotateX}deg) rotateY(${rotateY}deg) scale(1.02)`;
    });

    card.addEventListener("mouseleave", () => {
        card.style.transform = "rotateX(0) rotateY(0) scale(1)";
    });
});
// ===============================
// SMOOTH SCROLL REVEAL
// ===============================
const revealElements = document.querySelectorAll(".reveal");

const revealObserver = new IntersectionObserver(
    (entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add("active");
                revealObserver.unobserve(entry.target); // animate once
            }
        });
    },
    {
        threshold: 0.15
    }
);

revealElements.forEach(el => revealObserver.observe(el));
