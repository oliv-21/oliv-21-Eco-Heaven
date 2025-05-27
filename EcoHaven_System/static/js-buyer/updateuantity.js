// Function to update the quantity based on the unit price
function updateQuantity(button, change) {
    const cartItem = button.closest('.updateQuantity').parentElement;   
    const quantityInput = cartItem.querySelector('.quantity');
    const itemId = cartItem.querySelector('input[name="item_id"]').value; 

    // Update quantity
    let quantity = parseInt(quantityInput.value) + change;
    if (quantity < 1) quantity = 1; // Ensure minimum quantity is 1
    quantityInput.value = quantity;

    // Disable the decrement button if quantity is 1
    const decrementBtn = cartItem.querySelector('#decrementBtn');
    decrementBtn.disabled = (quantity === 1);

    // Send AJAX request to update the quantity in the database
    fetch('/update_cart_quantity', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/x-www-form-urlencoded',
        },
        body: new URLSearchParams({ 'item_id': itemId, 'quantity': quantity })
    })
    .then(response => response.json())
    .then(data => {
        if (data.status === 'error') {
            console.error(data.message);
            alert('Error updating quantity: ' + data.message);
        } else {
            console.log('Quantity updated successfully');
            // Update the displayed total price with the server's response
            const totalPriceElement = cartItem.querySelector('.total-price');
            totalPriceElement.textContent = `₱${data.new_total_price.toFixed(2)}`; // Update with the server's response
        }
    })
    .catch(error => {
        console.error('Error:', error);
        alert('An unexpected error occurred while updating the quantity.'); // User-friendly error message
    });
}
