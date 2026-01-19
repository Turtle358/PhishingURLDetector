const params = new URLSearchParams(window.location.search);
const url = params.get('url') || "Unknown Website";
const prediction = params.get('prediction') || "-1";

document.getElementById('target-url').textContent = url;

document.getElementById('continue-link').href = url;

document.getElementById('safety-rating').textContent = prediction;

const ratingElement = document.getElementById('safety-rating');
ratingElement.style.color = "#dc3545";