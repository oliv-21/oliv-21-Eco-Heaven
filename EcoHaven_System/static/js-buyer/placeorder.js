// Select the "Select All" checkbox, individual item checkboxes, and total price label
const selectAllCheckbox = document.getElementById('select-all');
const itemCheckboxes = document.querySelectorAll('.select-item');
const totalPriceLabel = document.getElementById('totalPayment'); // Assuming the ID for total price element
const checkoutForm = document.getElementById('checkout-form');

let totalPrice = 0;

// Function to recalculate the total price based on checked items
function recalculateTotal() {
    totalPrice = 0;
    itemCheckboxes.forEach(item => {
        if (item.checked) {
            totalPrice += parseFloat(item.getAttribute('data-price'));
        }
    });
    totalPriceLabel.textContent = "₱" + totalPrice.toFixed(2); // Display the updated total
}

// Event listener for "Select All" checkbox to toggle all items
selectAllCheckbox.addEventListener('change', function () {
    itemCheckboxes.forEach(item => {
        item.checked = selectAllCheckbox.checked;
    });
    recalculateTotal(); // Recalculate total when "Select All" is toggled
});

// Event listener for individual item checkboxes to update total price on change
itemCheckboxes.forEach(item => {
    item.addEventListener('change', recalculateTotal); // Recalculate when item checkbox changes
});

// Form submission validation
checkoutForm.onsubmit = function (e) {
    const selectedItems = document.querySelectorAll('input[name="selected_items[]"]:checked');
    if (selectedItems.length === 0) {
        e.preventDefault(); // Prevent form submission if no items are selected
        alert('Please select at least one item to proceed to checkout.'); // Show alert
    }
};
