document.getElementById('checkButton').addEventListener('click', handleCheck);
document.getElementById('inputText').addEventListener('keypress', function(event) {
  if (event.key === 'Enter') {
    event.preventDefault();
    handleCheck();
  }
});

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
    outputDiv.innerText = `Prediction: ${data.prediction}%, Danger: ${data.danger}`;
  } catch (error) {
    console.error('Fetch error:', error);
    outputDiv.innerText = `Error: ${error.message}`;
  }
}