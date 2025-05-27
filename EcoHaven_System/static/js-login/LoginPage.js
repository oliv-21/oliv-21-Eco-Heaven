document.addEventListener("DOMContentLoaded", function() {
    const links = {
        signupLink: document.getElementById("signup-link"),
        loginLink: document.getElementById("loginlink-link"),
        forgotPassword: document.getElementById("forgotPassword-link"),
        createAccountBuyer: document.getElementById("createAccountBuyer"),
        createAccountSeller: document.getElementById("createAccountSeller"),
        buyerFormLink: document.getElementById("buyerForm-Link"),
        sellerFormLink: document.getElementById("sellerForm-link"),
        passwordField: document.getElementById("password"),
        password2Field: document.getElementById("password2"),
        emailField: document.getElementById("email")
    };

    // Modal elements
    const modal = document.getElementById("messageModal");
    const modalMessage = document.getElementById("modalMessage");
    const closeModalButton = document.querySelector(".modal-footer button");

    // Function to open modal with a message
    function openModal(message) {
        modalMessage.textContent = message;
        modal.style.display = "block";
    }

    // Function to close modal
    function closeModal() {
        modal.style.display = "none";
    }

    // Close modal on button click
    closeModalButton.addEventListener("click", closeModal);

    // Navigation Links
    const navigateTo = (link, path) => {
        if (link) {
            link.addEventListener("click", function(event) {
                event.preventDefault();
                window.location.href = path;
            });
        }
    };

    // Set up navigation for all links
    navigateTo(links.signupLink, "/signup");
    navigateTo(links.forgotPassword, "/forgotPassword");
    navigateTo(links.loginLink, "/");

    // Form Submission with Modal for Error Display
    const validateAndSubmitForm = (formLink) => {
        if (formLink) {
            formLink.addEventListener("click", function(event) {
                event.preventDefault();
    
                const emailField = links.emailField;
                const password = links.passwordField.value;
                const password2 = links.password2Field.value;
    
                const email = emailField.value;
    
                // Check if email is valid
                const emailPattern = /^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$/;
                if (!emailPattern.test(email)) {
                    openModal("Please enter a valid email address.");
                    return;
                }
    
                // Check if passwords match
                if (password !== password2) {
                    openModal("Passwords do not match!");
                    return;
                }
    
                // Check if password length is at least 8 characters
                if (password.length < 8) {
                    openModal("Password must be at least 8 characters long.");
                    return;
                }
    
                // Check if all fields are filled
                if (!email || !password || !password2) {
                    openModal("Please fill in all fields.");
                    return;
                }
    
                // If all checks pass, submit the form
                document.querySelector('form').submit();
            });
        }
    };
    

    validateAndSubmitForm(links.buyerFormLink);
    validateAndSubmitForm(links.sellerFormLink);
});
