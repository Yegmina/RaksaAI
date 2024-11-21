'use strict';

/* start of the template */
const debug_phase = "pre-alfa";

/*get functions*/
function getValueByName(local_name) {
  const element = getElement('name', local_name);
  return element ? element.value : null;
}

function getValueById(local_id) {
  const element = getElement('id', local_id);
  return element ? element.value : null;
}

function getValueByTagName(local_tag) {
  const element = getElement('tag', local_tag);
  return element ? element.value : null;
}

function getValueByClassName(local_class) {
  const element = getElement('class', local_class);
  return element ? element.value : null;
}


function getElement(selector, value) {
  let elements;

  switch (selector) {
    case 'name':
      elements = document.getElementsByName(value);
      break;
    case 'id':
      elements = document.querySelectorAll(`#${value}`);
      break;
    case 'tag':
      elements = document.getElementsByTagName(value);
      break;
    case 'class':
      elements = document.getElementsByClassName(value);
      break;
    default:
      console.log(`Unknown selector type: ${selector}`);
      return null;
  }

  if (!elements || elements.length === 0) {
    console.log(`No element found with ${selector}: ${value}`);
    return null;
  } else if (elements.length > 1 && selector !== 'id') {
    console.log(`Unexpected duplicates with the same ${selector}: ${value}`);
    return elements;
  }
  else if (elements.length > 1 && selector === 'id') {
    customAlert("Different tags with same id found! Check HTML code and fix this!")
    console.log(`Unexpected duplicates with the same ${selector}: ${value}`);
    return elements;
  }

  return elements[0];
}

/*get function end*/

/* customAlert and console log functions, debuging etc */

// Overriding the alert function conditionally based on debug_phase;
function customAlert(string) {
  if (debug_phase === "pre-alfa") {
    window.alert(string); // Use browser's built-in alert
  } else {
    console.error(string); // Logs errors to the console in other phases
  }
}



/* end */


/* end of the template*/




document.getElementById('filter-method').addEventListener('change', (e) => {
    const method = e.target.value;
    document.getElementById('dropdown-container').style.display = method === 'dropdown' ? 'block' : 'none';
    document.getElementById('upload-container').style.display = method === 'upload' ? 'block' : 'none';
});

document.getElementById('filter-button').addEventListener('click', async () => {
    let csvFile = document.getElementById('csv-file').files[0];
    
    // If no file is uploaded, use the default CSV file
    if (!csvFile) {
        customAlert('No file uploaded. Using default companies CSV file.');
        csvFile = await fetch('default_companies.csv') // Make sure 'default_companies.csv' exists in the same directory
            .then(response => {
                if (!response.ok) throw new Error("Failed to load the default CSV file.");
                return response.blob(); // Convert the response to a Blob
            })
            .catch(error => {
                console.error(error);
                customAlert("Default file could not be loaded.");
                return null;
            });
    }

    if (!csvFile) {
        customAlert('No valid CSV file available. Please upload or add the default file.');
        return;
    }

    const filterMethod = document.getElementById('filter-method').value;
    let filterList = [];

    if (filterMethod === 'dropdown') {
        const selectedOptions = document.getElementById('dropdown').selectedOptions;
        filterList = Array.from(selectedOptions).map(option => option.value);
    } else {
        const filterFile = document.getElementById('filter-file').files[0];
        if (!filterFile) {
            customAlert('Please upload the filter list file.');
            return;
        }
        filterList = await readFileAsText(filterFile).then(data => data.split('\n').map(line => line.trim()));
    }

    const csvData = await readFileAsText(csvFile);
    const filteredData = filterCSV(csvData, filterList);

    downloadCSV(filteredData, 'relevant_companies_last_search.csv');
});

function readFileAsText(file) {
    return new Promise((resolve, reject) => {
        const reader = new FileReader();
        reader.onload = () => resolve(reader.result);
        reader.onerror = () => reject(reader.error);
        reader.readAsText(file);
    });
}

function filterCSV(csvData, filterList) {
    const rows = csvData.split('\n').map(row => row.trim()); // Split rows and trim whitespace
    const [header, ...dataRows] = rows;

    // Ensure rows have at least two columns
    const filteredRows = dataRows.filter(row => {
        const columns = row.split(',');
        if (columns.length < 2) return false; // Skip rows without the required structure

        const mainBusinessLine = columns[1]?.trim(); // Safely access the second column
        return filterList.includes(mainBusinessLine);
    });

    return [header, ...filteredRows].join('\n'); // Combine filtered rows with header
}

function downloadCSV(data, filename) {
    const blob = new Blob([data], { type: 'text/csv' });
    const url = URL.createObjectURL(blob);
    const link = document.getElementById('download-link');
    link.href = url;
    link.download = filename;
    link.style.display = 'block';
    link.textContent = 'Download Filtered CSV';
}
