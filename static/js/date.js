// Get yesterday's date
const yesterday = new Date();
yesterday.setDate(yesterday.getDate() - 1);

// Format the date as YYYY-MM-DD
const year = yesterday.getFullYear();
const month = String(yesterday.getMonth() + 1).padStart(2, '0');
const day = String(yesterday.getDate()).padStart(2, '0');
const formattedDate = `${year}-${month}-${day}`;

// Set the value of the date input field
document.getElementById('date').value = formattedDate;

