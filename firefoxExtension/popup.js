document.addEventListener('DOMContentLoaded', () => {
  document.getElementById('checkButton').addEventListener('click', handleCheck);

  document.getElementById('inputText').addEventListener('keypress', function(event) {
    if (event.key === 'Enter') {
      event.preventDefault();  // Prevents the default Enter key behavior
      handleCheck();
    }
  });

  // Function to handle the text check
  async function handleCheck() {
    const inputText = document.getElementById('inputText').value;
    const outputDiv = document.getElementById('output');

    if (inputText.trim() === "") {
      outputDiv.innerText = "Please enter some text.";
      return;
    }

    try {
      const response = await fetch('http://127.0.0.1:5000/process', {
        method: 'POST',
        headers: {
          'Content-Type': 'application/json'
        },
        body: JSON.stringify({ text: inputText })
      });

      if (!response.ok) {
        throw new Error(`Error: ${response.statusText}`);
      }

      const data = await response.json();
      console.log('API response:', data);
      outputDiv.innerText = `Prediction: ${data.prediction}%, Worst Case ${data.worstCase}%\nDanger: ${data.danger}`;
    } catch (error) {
      console.error('Fetch error:', error);
      outputDiv.innerText = `Error: ${error.message}`;
    }
  }

  // Get all links on the current page and check them via the API
  document.getElementById('getLinksButton').addEventListener('click', () => {
    chrome.tabs.query({ active: true, currentWindow: true }, (tabs) => {
      chrome.tabs.sendMessage(tabs[0].id, { action: "getLinks" }, async (response) => {
        if (chrome.runtime.lastError) {
          console.error(chrome.runtime.lastError.message);
          return;
        }

        const links = response.links;
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

            if (data.danger === "Likely Scam" || data.danger === "Highly likely Scam") {
              alert(`Scam link detected: ${link}`);
            }

          } catch (error) {
            console.error(`Error checking ${link}:`, error);
          }
        }
      });
    });
  });
});
