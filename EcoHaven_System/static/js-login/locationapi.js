const provinceSelect = document.getElementById('provinceSelect');
const municipalitySelect = document.getElementById('municipalitySelect');
const barangaySelect = document.getElementById('barangaySelect');

// Load provinces for the Philippines
function loadProvinces() {
    provinceSelect.disabled = false;
    municipalitySelect.disabled = true;
    barangaySelect.disabled = true;

    provinceSelect.innerHTML = '<option value="">Select Province</option>';
    municipalitySelect.innerHTML = '<option value="">Select City/Municipality</option>';
    barangaySelect.innerHTML = '<option value="">Select Barangay</option>';

    fetch('https://psgc.gitlab.io/api/provinces')
        .then(response => response.json())
        .then(data => {
            data.forEach(province => {
                const option = document.createElement('option');
                option.value = province.code;
                option.textContent = province.name;
                provinceSelect.appendChild(option);
            });
        })
        .catch(error => console.error('Error loading provinces:', error));
}

// Load municipalities based on selected province
function loadMunicipalities() {
    const selectedProvinceCode = provinceSelect.value;

    municipalitySelect.disabled = false;
    barangaySelect.disabled = true;

    municipalitySelect.innerHTML = '<option value="">Select City/Municipality</option>';
    barangaySelect.innerHTML = '<option value="">Select Barangay</option>';

    if (selectedProvinceCode) {
        fetch(`https://psgc.gitlab.io/api/provinces/${selectedProvinceCode}/municipalities`)
            .then(response => response.json())
            .then(data => {
                data.forEach(municipality => {
                    const option = document.createElement('option');
                    option.value = municipality.code;
                    option.textContent = municipality.name;
                    municipalitySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading municipalities:', error));
    }
}

// Load barangays based on selected municipality
function loadBarangays() {
    const selectedMunicipalityCode = municipalitySelect.value;

    barangaySelect.disabled = false;

    barangaySelect.innerHTML = '<option value="">Select Barangay</option>';

    if (selectedMunicipalityCode) {
        fetch(`https://psgc.gitlab.io/api/municipalities/${selectedMunicipalityCode}/barangays`)
            .then(response => response.json())
            .then(data => {
                data.forEach(barangay => {
                    const option = document.createElement('option');
                    option.value = barangay.code;
                    option.textContent = barangay.name;
                    barangaySelect.appendChild(option);
                });
            })
            .catch(error => console.error('Error loading barangays:', error));
    }
}

// Event listeners
provinceSelect.addEventListener('change', loadMunicipalities);
municipalitySelect.addEventListener('change', loadBarangays);

// Load provinces on page load
window.onload = loadProvinces;
