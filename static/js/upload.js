/**
 * Upload Page JavaScript
 * Handles image upload, drag-drop, and detection display
 */

// DOM Elements
const dropZone = document.getElementById('dropZone');
const fileInput = document.getElementById('fileInput');
const previewSection = document.getElementById('previewSection');
const previewImage = document.getElementById('previewImage');
const detectBtn = document.getElementById('detectBtn');
const resetBtn = document.getElementById('resetBtn');
const loadingSection = document.getElementById('loadingSection');
const resultsSection = document.getElementById('resultsSection');
const newDetectionBtn = document.getElementById('newDetectionBtn');

// State
let selectedFile = null;

/**
 * Initialize event listeners
 */
function initUploadPage() {
    // Drag and drop events
    dropZone.addEventListener('dragover', handleDragOver);
    dropZone.addEventListener('dragleave', handleDragLeave);
    dropZone.addEventListener('drop', handleDrop);
    
    // File input event
    fileInput.addEventListener('change', handleFileSelect);
    
    // Button events
    detectBtn.addEventListener('click', handleDetect);
    resetBtn.addEventListener('click', resetUpload);
    newDetectionBtn.addEventListener('click', resetUpload);
}

/**
 * Handle drag over event
 */
function handleDragOver(e) {
    e.preventDefault();
    dropZone.classList.add('drag-over');
}

/**
 * Handle drag leave event
 */
function handleDragLeave() {
    dropZone.classList.remove('drag-over');
}

/**
 * Handle drop event
 */
function handleDrop(e) {
    e.preventDefault();
    dropZone.classList.remove('drag-over');
    
    const files = e.dataTransfer.files;
    if (files.length > 0) {
        handleFile(files[0]);
    }
}

/**
 * Handle file selection from input
 */
function handleFileSelect(e) {
    if (e.target.files.length > 0) {
        handleFile(e.target.files[0]);
    }
}

/**
 * Validate and process selected file
 */
function handleFile(file) {
    // Validate file type
    const validTypes = ['image/jpeg', 'image/jpg', 'image/png', 'image/bmp', 'image/webp'];
    if (!validTypes.includes(file.type)) {
        alert('Please select a valid image file (JPG, PNG, BMP, WEBP)');
        return;
    }

    // Validate file size (16MB max)
    const maxSize = 16 * 1024 * 1024;
    if (file.size > maxSize) {
        alert('File size should not exceed 16MB');
        return;
    }

    selectedFile = file;
    
    // Show preview
    const reader = new FileReader();
    reader.onload = (e) => {
        previewImage.src = e.target.result;
        dropZone.style.display = 'none';
        previewSection.style.display = 'block';
    };
    reader.readAsDataURL(file);
}

/**
 * Reset to initial upload state
 */
function resetUpload() {
    selectedFile = null;
    fileInput.value = '';
    dropZone.style.display = 'flex';
    previewSection.style.display = 'none';
    resultsSection.style.display = 'none';
    loadingSection.style.display = 'none';
}

/**
 * Handle detect button click
 */
async function handleDetect() {
    if (!selectedFile) return;

    const formData = new FormData();
    formData.append('file', selectedFile);
    formData.append('confidence', 0.25);

    previewSection.style.display = 'none';
    loadingSection.style.display = 'block';
    resultsSection.style.display = 'none';

    try {
        const response = await fetch('/detect', {
            method: 'POST',
            body: formData
        });

        const data = await response.json();

        if (data.success) {
            displayResults(data);
        } else {
            alert('Error: ' + (data.error || 'Detection failed'));
            resetUpload();
        }
    } catch (error) {
        alert('Error: ' + error.message);
        resetUpload();
    } finally {
        loadingSection.style.display = 'none';
    }
}

/**
 * Display detection results
 */
function displayResults(data) {
    // Show images
    document.getElementById('originalImage').src = data.original_image;
    document.getElementById('detectedImage').src = data.detected_image;

    // Show statistics
    document.getElementById('totalItems').textContent = data.statistics.total_items;

    // Show category breakdown
    const categoryStats = document.getElementById('categoryStats');
    categoryStats.innerHTML = '';
    
    if (Object.keys(data.statistics.categories).length > 0) {
        for (const [category, count] of Object.entries(data.statistics.categories)) {
            const categoryCard = document.createElement('div');
            categoryCard.className = 'stat-card category-stat';
            categoryCard.innerHTML = `
                <div class="stat-number">${count}</div>
                <div class="stat-label">${capitalize(category)}</div>
            `;
            categoryStats.appendChild(categoryCard);
        }
    } else {
        categoryStats.innerHTML = '<p class="no-data">No waste items detected</p>';
    }

    // Show detection details table
    const tableBody = document.getElementById('detectionsTableBody');
    tableBody.innerHTML = '';
    
    if (data.detections.length > 0) {
        data.detections.forEach((detection, index) => {
            const row = document.createElement('tr');
            row.innerHTML = `
                <td>${index + 1}</td>
                <td><span class="category-badge ${detection.class}">${capitalize(detection.class)}</span></td>
                <td>${(detection.confidence * 100).toFixed(2)}%</td>
                <td>${detection.bbox.join(', ')}</td>
            `;
            tableBody.appendChild(row);
        });
    } else {
        tableBody.innerHTML = '<tr><td colspan="4" class="no-data">No detections found</td></tr>';
    }

    resultsSection.style.display = 'block';
}

/**
 * Capitalize first letter
 */
function capitalize(str) {
    return str.charAt(0).toUpperCase() + str.slice(1);
}

// Initialize on page load
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initUploadPage);
} else {
    initUploadPage();
}