async function checkLinks() {
  const links = Array.from(document.querySelectorAll('a')).map(link => link.href);

  for (const link of links) {
    try {
      const res = await fetch('http://127.0.0.1:5000/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: link })
      });

      if (!res.ok) {
        throw new Error(`Error: ${res.statusText}`);
      }

      const data = await res.json();
      console.log(`Checked ${link}: ${data.prediction}, ${data.danger}`);

      // If the link is dangerous, show an alert
      if (data.danger === true) { // Adjust this condition based on your API's response format
        alert(`Scam link detected: ${link}`);
      }

    } catch (error) {
      console.error(`Error checking ${link}:`, error);
    }
  }
}

// Automatically check links when the page loads
document.addEventListener('DOMContentLoaded', checkLinks);
