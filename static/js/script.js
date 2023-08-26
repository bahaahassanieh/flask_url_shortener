document.getElementById('url-form').addEventListener('submit', async (event) => {
    event.preventDefault();

    const urlInput = document.getElementById('url-input');
    const resultParagraph = document.getElementById('result');

    const response = await fetch('/shorten', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json'
        },
        body: JSON.stringify({
            url: urlInput.value
        })
    });

    const data = await response.json();

    if (data.shortened_url) {
        resultParagraph.textContent = `Shortened URL: ${data.shortened_url}`;
    } else {
        resultParagraph.textContent = 'Error shortening the URL!';
    }
});
