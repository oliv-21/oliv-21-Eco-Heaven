// Function to delete an item from the cart
function deleteItem(button) {
    const cartItem = button.closest('.info-procuct'); // Find the closest cart item container
    const itemId = cartItem.querySelector('.product-name').getAttribute('productid');  // Get item ID from the product name span

    // Calculate the total price of the item being removed
    const totalPrice = parseFloat(cartItem.querySelector('.total-price').textContent.replace('₱', '').replace(',', ''));

    // Update the total payment displayed
    updateTotalAfterDeletion(totalPrice);

    // Remove the specific cart item from the DOM
    cartItem.remove();

    // Send AJAX request to delete the item from the database
    sendDeleteRequest(itemId)
        .then(data => {
            if (data.status === 'error') {
                alert('Error deleting item: ' + data.message);
            } else {
                console.log(data.message);
            }
        })
        .catch(error => console.error('Error:', error));

    // Check if there are any remaining items in the shop
    removeShopContainerIfEmpty(cartItem);
}

// Function to update the total payment after item deletion
function updateTotalAfterDeletion(totalPrice) {
    const totalPriceElement = document.getElementById('totalPayment'); // Total payment element
    const currentTotal = parseFloat(totalPriceElement.textContent.replace('₱', '').replace(',', ''));
    const newTotal = currentTotal - totalPrice; // Deduct item price from total
    totalPriceElement.textContent = `₱${newTotal.toFixed(2)}`; // Set the new total payment
}

// Function to send the delete request
function sendDeleteRequest(itemId) {
    return fetch('/delete_cart_item', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ 'item_id': itemId }) 
    }).then(response => response.json());
}

// Function to check for remaining items in the shop and remove the container if empty
function removeShopContainerIfEmpty(cartItem) {
    const shopCartContainer = cartItem.closest('.shop-cart-container');
    const remainingItems = shopCartContainer.querySelectorAll('.info-procuct');
    if (remainingItems.length === 0) {
        shopCartContainer.remove();
    }
}

// Function to handle selecting/deselecting all items under a shop
function toggleShop(shopCheckbox) {
    const shopName = shopCheckbox.getAttribute('data-shop'); // Get the shop name from the data attribute
    const itemCheckboxes = document.querySelectorAll(`input.select-item[data-shop="${shopName}"]`); // Select all product checkboxes in this shop

    // Toggle the state of all product checkboxes based on the shop checkbox
    itemCheckboxes.forEach(itemCheckbox => {
        itemCheckbox.checked = shopCheckbox.checked;
    });

    updateTotal(); // Recompute the total payment based on checked items
}

// Function to update the total payment
function updateTotal() {
    let totalPayment = 0;

    // Find all checked product checkboxes
    const checkedItems = document.querySelectorAll('input.select-item:checked');

    checkedItems.forEach(itemCheckbox => {
        const cartItem = itemCheckbox.closest('.cart-item-container');
        const itemPrice = parseFloat(cartItem.querySelector('.total-price').textContent.replace('₱', '').replace(',', ''));
        totalPayment += itemPrice; // Add the price of the checked item to the total
    });

    // Update the total payment displayed on the page
    const totalPriceElement = document.getElementById('totalPayment');
    totalPriceElement.textContent = `₱${totalPayment.toFixed(2)}`;
}





// function deleteItem(button) {
//     // Find the closest cart item container
//     const cartItem = button.closest('.cart-item-container');
//     if (!cartItem) {
//         console.error("Cart item container not found.");
//         return;
//     }

//     // Extract the product ID
//     const itemId = cartItem.querySelector('.product-name').getAttribute('productid');

//     // Calculate the total price of the item being removed
//     const totalPrice = parseFloat(cartItem.querySelector('.total-price').textContent.replace('₱', '').replace(',', ''));

//     // Update the total payment
//     updateTotalAfterDeletion(totalPrice);

//     // Remove the specific cart item from the DOM
//     cartItem.remove();

//     // Check if the parent shop container is now empty
//     removeShopContainerIfEmpty(cartItem);

//     // Send AJAX request to delete the item
//     sendDeleteRequest(itemId)
//         .then(data => {
//             if (data.status === 'error') {
//                 alert('Error deleting item: ' + data.message);
//             } else {
//                 console.log(data.message);
//             }
//         })
//         .catch(error => console.error('Error:', error));
// }

// function removeShopContainerIfEmpty(cartItem) {
//     // Find the parent shop container
//     const shopCartContainer = cartItem.closest('.shop-cart-container');
//     if (!shopCartContainer) {
//         console.error("Shop cart container not found.");
//         return;
//     }

//     // Check if there are any remaining cart items in the shop
//     const remainingItems = shopCartContainer.querySelectorAll('.cart-item-container');
//     if (remainingItems.length === 0) {
//         shopCartContainer.remove();
//     }
// }

// function updateTotalAfterDeletion(price) {
//     const totalPaymentElement = document.querySelector('.total-payment');
//     if (!totalPaymentElement) {
//         console.error("Total payment element not found.");
//         return;
//     }

//     let currentTotal = parseFloat(totalPaymentElement.textContent.replace('₱', '').replace(',', ''));
//     currentTotal -= price;
//     totalPaymentElement.textContent = '₱' + currentTotal.toLocaleString('en-US', { minimumFractionDigits: 2 });
// }

// function sendDeleteRequest(itemId) {
//     return fetch('/delete-item/${itemId}', { method: 'DELETE' })
//         .then(response => response.json());
// }

// // Function to update the total payment after item deletion
// function updateTotalAfterDeletion(totalPrice) {
//     const totalPriceElement = document.getElementById('totalPayment'); // Total payment element
//     const currentTotal = parseFloat(totalPriceElement.textContent.replace('₱', '').replace(',', ''));
//     const newTotal = currentTotal - totalPrice; // Deduct item price from total
//     totalPriceElement.textContent = `₱${newTotal.toFixed(2)}`; // Set the new total payment
// }

// // Function to send the delete request
// function sendDeleteRequest(itemId) {
//     return fetch('/delete_cart_item', {
//         method: 'POST',
//         headers: {
//             'Content-Type': 'application/x-www-form-urlencoded',
//         },
//         body: new URLSearchParams({ 'item_id': itemId }) 
//     }).then(response => response.json());
// }