window.onload = function() {
    const urlParams = new URLSearchParams(window.location.search);
    const error = urlParams.get('error');
    if (error) {
        document.getElementById('modalMessage').innerText = error;
        document.getElementById('messageModal').style.display = 'block';
    }
};

function closeModal() {
    document.getElementById('messageModal').style.display = 'none';
}

