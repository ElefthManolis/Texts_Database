function validateInputs() {
    let isValid = true;
    const numberInput = document.getElementById('number');
    const distanceMeasureSelect = document.getElementById('distance_measure');
    const numberValue = parseFloat(numberInput.value);
    const distanceMeasureValue = distanceMeasureSelect.value;
    const numberErrorMessage = document.getElementById('number-error');
    const distanceMeasureErrorMessage = document.getElementById('distance_measure-error');

    // Reset error states
    numberInput.classList.remove('error');
    distanceMeasureSelect.classList.remove('error');
    numberErrorMessage.textContent = '';
    distanceMeasureErrorMessage.textContent = '';

    // Validate number input
    if (isNaN(numberValue) || numberValue <= 0 || !Number.isInteger(numberValue)) {
        numberInput.classList.add('error');
        numberErrorMessage.textContent = 'Please enter a positive integer.';
        isValid = false;
    }

    // Validate distance measure selection
    if (!distanceMeasureValue || distanceMeasureValue === "Distance Measure") {
        distanceMeasureSelect.classList.add('error');
        distanceMeasureErrorMessage.textContent = 'Please select a distance measure.';
        isValid = false;
    }

    return isValid;
}

async function search() {
    if (!validateInputs()) {
        return; // Stop if inputs are invalid
    }
    const query = document.getElementById('query').value;
    const number = document.getElementById('number').value;
    const distance_measure = document.getElementById('distance_measure').value;
    const response = await fetch(`/search?query=${query}&number=${number}&distance_measure=${distance_measure}`);
    if (!response.ok) {
        console.error("Failed to fetch data from the server");
        return;
    }
    const results = await response.json();
    showResults(results, query);  
    // Scroll to the search button
    document.getElementById('searchButton').scrollIntoView({ behavior: 'smooth' });  
}

function highlightText(text, query) {
    const words = query.split(' ').filter(word => word.length > 0);
    let highlightedText = text;
    words.forEach(word => {
        const regex = new RegExp(`(${word})`, 'gi');
        highlightedText = highlightedText.replace(regex, '<span class="highlight">$1</span>');
    });
    return highlightedText;
}

function showResults(results, query) {
    let resultsDiv = document.getElementById('results');
    resultsDiv.innerHTML = '';
    // Display documents
    if ('documents' in results) {
        let documentsList = results['documents'];
        documentsList.forEach((currentDoc, index) => {
            let docP = document.createElement('p');
            let boltTitle = document.createElement('b');
            boltTitle.textContent = `Document ${index + 1}`;
            docP.innerHTML = `${highlightText(currentDoc, query)}`;
            resultsDiv.appendChild(boltTitle);
            resultsDiv.appendChild(docP);
        });
    } else {
        let noResultsP = document.createElement('p');
        noResultsP.textContent = 'No documents found.';
        resultsDiv.appendChild(noResultsP);
    }
}