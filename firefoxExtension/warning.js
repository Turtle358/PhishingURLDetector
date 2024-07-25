const params = new URLSearchParams(window.location.search);
const url = params.get('url');
const prediction = params.get('prediction');
document.getElementById('continue-link').href = url;
document.getElementById('safety-rating').textContent = prediction ? prediction : "Not available";
console.log(`Safety Rating Displayed: ${document.getElementById('safety-rating').textContent}`);