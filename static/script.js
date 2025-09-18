document.addEventListener('DOMContentLoaded', function() {
    const form = document.getElementById('patientForm');
    const previewElement = document.getElementById('preview_id');
    
    // Barcode reader enhancement
    let lastInputTime = 0;
    let inputBuffer = '';
    const BARCODE_MIN_LENGTH = 3;
    const BARCODE_TIMEOUT = 100; // milliseconds
    
    if (form && previewElement) {
        // Update ID preview when form changes
        function updatePreview() {
            fetch('/preview_id', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json',
                },
            })
            .then(response => response.json())
            .then(data => {
                if (data.oncocentre_id) {
                    previewElement.textContent = data.oncocentre_id;
                } else if (data.error) {
                    console.error('Preview error:', data.error);
                }
            })
            .catch(error => {
                console.error('Error updating preview:', error);
            });
        }
        
        // Update preview on page load
        updatePreview();
        
        // Update preview when any form field changes
        const formInputs = form.querySelectorAll('input, select');
        formInputs.forEach(input => {
            input.addEventListener('input', updatePreview);
            input.addEventListener('change', updatePreview);
        });
        
        // Barcode reader support
        function setupBarcodeSupport() {
            const textInputs = form.querySelectorAll('input[type="text"]');
            
            textInputs.forEach((input, index) => {
                input.addEventListener('input', function(e) {
                    const currentTime = Date.now();
                    const timeDiff = currentTime - lastInputTime;
                    
                    // Detect rapid input (likely from barcode scanner)
                    if (timeDiff < BARCODE_TIMEOUT && this.value.length >= BARCODE_MIN_LENGTH) {
                        // Add visual feedback for barcode scan
                        this.classList.add('barcode-scanned');
                        setTimeout(() => this.classList.remove('barcode-scanned'), 1000);
                        
                        // Auto-focus next empty field
                        setTimeout(() => {
                            const nextEmptyField = findNextEmptyField();
                            if (nextEmptyField) {
                                nextEmptyField.focus();
                            }
                        }, 50);
                    }
                    
                    lastInputTime = currentTime;
                });
                
                // Add tabindex for better navigation
                input.setAttribute('tabindex', index + 1);
            });
        }
        
        function findNextEmptyField() {
            const allFields = form.querySelectorAll('input[type="text"], input[type="date"], select');
            for (let field of allFields) {
                if (!field.value || field.value === '') {
                    return field;
                }
            }
            return null;
        }
        
        setupBarcodeSupport();
    }
    
    // Auto-dismiss alerts after 5 seconds
    const alerts = document.querySelectorAll('.alert');
    alerts.forEach(alert => {
        setTimeout(() => {
            const bsAlert = new bootstrap.Alert(alert);
            bsAlert.close();
        }, 5000);
    });
    
    // Form validation enhancement
    if (form) {
        form.addEventListener('submit', function(e) {
            const requiredFields = form.querySelectorAll('[required]');
            let isValid = true;
            
            requiredFields.forEach(field => {
                if (!field.value.trim()) {
                    field.classList.add('is-invalid');
                    isValid = false;
                } else {
                    field.classList.remove('is-invalid');
                }
            });
            
            if (!isValid) {
                e.preventDefault();
                const firstInvalidField = form.querySelector('.is-invalid');
                if (firstInvalidField) {
                    firstInvalidField.focus();
                    firstInvalidField.scrollIntoView({ behavior: 'smooth', block: 'center' });
                }
            }
        });
        
        // Remove validation classes on input
        const allInputs = form.querySelectorAll('input, select');
        allInputs.forEach(input => {
            input.addEventListener('input', function() {
                this.classList.remove('is-invalid');
            });
        });
    }
});