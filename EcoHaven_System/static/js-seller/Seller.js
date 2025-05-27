document.addEventListener("DOMContentLoaded", function() {
const addProduct = document.getElementById("product-link");
const updatestocks = document.getElementById("updatestocks-link");



addProduct.addEventListener("click", function(event) {
    event.preventDefault(); 
    window.location.href = "/seller-page/products"; 
});
updatestocks.addEventListener("click", function(event) {
    event.preventDefault(); 
    window.location.href = "/seller/update-stock"; 
});



});

document.addEventListener("DOMContentLoaded", function() {
    const addProductPage = document.getElementById("add-product"); 

    if (addProductPage) {
        addProductPage.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/seller/add-product"; 
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const sellerdashboard = document.getElementById("dashboard-link");
    const sellerinformation = document.getElementById("sellerinformation");
    const sellerFormUpdate = document.getElementById("seller-Form-update");


    // Check if the elements exist before adding event listeners
    if (sellerdashboard) {
        sellerdashboard.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/seller_dashboard"; 
        });
    }

    if (sellerinformation) {
        sellerinformation.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/seller/profile";
        });
    }
    if (sellerFormUpdate) {
        sellerFormUpdate.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/seller/update-profile";
        });
    }
});

document.addEventListener("DOMContentLoaded", function() {
    const logout = document.getElementById("logout-btn"); 

    if (logout) {
        logout.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/logout"; 
        });
    }
});
document.addEventListener("DOMContentLoaded", function() {
    const orders = document.getElementById("all-orders");

    if (orders) {
        orders.addEventListener("click", function(event) {
            event.preventDefault();
            window.location.href = "/seller/orders";
        });
    }
});




    




