document.addEventListener("DOMContentLoaded", function() {
    const elements = {
        buyerinformation: document.getElementById("profileInformationbuyer"),
        profileForm: document.getElementById("profileForm"),
        
        productOverview: document.getElementById("productOverview"),
        dashboard: document.getElementById("dashboard"),
        cartlink: document.getElementById("cart-link"),
        orderlink: document.getElementById("order-link"),
        vieworderbtn: document.getElementById("view-order-btn"),
      
    };

    if (elements.buyerinformation) {
        elements.buyerinformation.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/buyer_dashboard/buyer_profile";
        });
    }

    if (elements.profileForm) {
        elements.profileForm.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/buyer_profile_form/update-profile";
        });
    }

    

    if (elements.productOverview) {
        elements.productOverview.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/buyer_dashboard/productOverview";
        });
    }

    if (elements.dashboard) {
        elements.dashboard.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/buyer_dashboard";
        });
    }

    if (elements.cartlink) {
        elements.cartlink.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/buyer_dashboard/cart";
        });
    }
    if (elements.orderlink) {
        elements.orderlink.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/user-orders";
        });
    }
    if (elements.vieworderbtn) {
        elements.vieworderbtn.addEventListener("click", function(event) {
            event.preventDefault(); 
            window.location.href = "/user-orders";
        });
    }

    
});
