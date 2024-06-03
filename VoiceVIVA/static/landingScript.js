document.addEventListener("DOMContentLoaded", function() {
    // Select the elements with the classes '.homepage', '.homep2', '.homep3', and '.homep4'
    var homepage = document.querySelector('.homepage');
    var homep2 = document.querySelector('.homep2');
    var homep3 = document.querySelector('.homep3');
    var homep4 = document.querySelector('.homep4');

    // Define a function to handle the smooth transition between the pages
    function smoothTransition() {
        // Set a timeout to remove the 'active' class from '.homepage' and add it to '.homep2' after a short delay
        setTimeout(function() {
            homepage.classList.remove('active');
            homep2.classList.add('active');

            // Set a timeout to remove the 'active' class from '.homep2' and add it to '.homep3' after a short delay
            setTimeout(function() {
                homep2.classList.remove('active');
                homep3.classList.add('active');

                // Set a timeout to remove the 'active' class from '.homep3' and add it to '.homep4' after a short delay
                setTimeout(function() {
                    homep3.classList.remove('active');
                    homep4.classList.add('active');

                    // Set a timeout to remove the 'active' class from '.homep4' and add it back to '.homepage' after a short delay
                    setTimeout(function() {
                        homep4.classList.remove('active');
                        homepage.classList.add('active');

                        // Call the function recursively to repeat the transition
                        smoothTransition();
                    }, 5000); // Change to 5000 milliseconds (5 seconds)
                }, 5000); // Change to 5000 milliseconds (5 seconds)
            }, 5000); // Change to 5000 milliseconds (5 seconds)
        }, 5000); // Change to 5000 milliseconds (5 seconds)
    }

    // Start the smooth transition initially
    smoothTransition();
});