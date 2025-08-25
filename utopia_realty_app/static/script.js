// // static/script.js

// document.addEventListener('DOMContentLoaded', function () {
//     // Toggle dropdown visibility
//     window.toggleDropdown = function (dropdownId) {
//         // Hide all other dropdowns first
//         document.querySelectorAll('.dropdown-options').forEach(el => el.style.display = 'none');
//         document.getElementById(dropdownId).style.display = 'block';
//     };

//     // Updated selectOption
//     window.selectOption = function (inputId, value) {
//         const input = document.getElementById(inputId);
//         if (input) {
//             input.value = value;
//         }

//         // Also set hidden input for form submission
//         const hiddenInput = document.getElementById(inputId.replace('Input', 'Hidden'));
//         if (hiddenInput) {
//             hiddenInput.value = value;
//         }

//         // Close dropdown
//         const dropdown = document.getElementById(inputId + 'Dropdown') || input?.nextElementSibling;
//         if (dropdown) dropdown.style.display = 'none';
//     };

//     // Filter dropdown options
//     window.filterOptions = function (searchInput, dropdownId) {
//         const filter = searchInput.value.toLowerCase();
//         const options = document.querySelectorAll(`#${dropdownId} .option`);
//         options.forEach(opt => {
//             const txt = opt.textContent.toLowerCase();
//             opt.style.display = txt.includes(filter) ? '' : 'none';
//         });
//     };

//     // Reset filters on button click
//     window.resetFilters = function () {
//         document.querySelectorAll('.dropdown-search input').forEach(input => {
//             input.value = '';
//         });
//         document.querySelectorAll('select').forEach(select => {
//             select.selectedIndex = 0;
//         });
//     };

//     // Allow readonly inputs to be submitted
//     window.clearReadonlyInputs = function () {
//         document.getElementById('propertyNameInput')?.removeAttribute('readonly');
//         document.getElementById('developerInput')?.removeAttribute('readonly');
//     };

//     // Run reset on page load
//     window.addEventListener('load', () => {
//         resetFilters();
//     });

//     // Hide dropdowns on outside click
//     document.addEventListener('click', function (event) {
//         const dropdowns = document.querySelectorAll('.dropdown-options');
//         dropdowns.forEach(dropdown => {
//             const input = dropdown.previousElementSibling;
//             if (!dropdown.contains(event.target) && !input.contains(event.target)) {
//                 dropdown.style.display = 'none';
//             }
//         });
//     });
// });
