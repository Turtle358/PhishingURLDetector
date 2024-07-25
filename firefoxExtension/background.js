browser.runtime.onMessage.addListener((message, sender, sendResponse) => {
    if (message.url) {
        let url = message.url;
        checkURL(url).then(prediction => {
            console.log(`Prediction for ${url}: ${prediction}`);  // Add this log
            if (prediction > 70) {
                browser.tabs.create({
                    url: browser.runtime.getURL('warning.html') + '?url=' + encodeURIComponent(url) + '&prediction=' + encodeURIComponent(prediction)
                });
            } else {
                browser.tabs.update(sender.tab.id, { url: url });
            }
        }).catch(error => {
            console.error('Error in checkURL:', error);
        });
        return true;  // Return true to indicate you will send a response asynchronously
    }
});

async function checkURL(url) {
    try {
        const response = await fetch('http://127.0.0.1:5000/process', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            body: JSON.stringify({ text: url })  // Assuming your API expects URL in text field
        });
        if (!response.ok) {
            throw new Error(`Error: ${response.statusText}`);
        }
        const data = await response.json();
        console.log('API response:', data);
        return data.prediction;
    } catch (error) {
        console.error('Fetch error:', error);
        return 0;
    }
}
