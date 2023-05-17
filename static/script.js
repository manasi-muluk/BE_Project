document.addEventListener('DOMContentLoaded', function() {
    var nextButton = document.getElementById('next-button');
  
    // Add click event listener to the "Next" button
    nextButton.addEventListener('click', function() {
      // Redirect to the new page
      window.location.href = '/next-page';
    });
  });
  

  