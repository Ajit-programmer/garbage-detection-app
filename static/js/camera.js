/**
 * Camera Page JavaScript
 * Handles live camera feed and real-time waste detection
 */

// DOM Elements
const video = document.getElementById('video');
const canvas = document.getElementById('canvas');
const capturedImage = document.getElementById('capturedImage');
const startBtn = document.getElementById('startBtn');
const stopBtn = document.getElementById('stopBtn');
const captureBtn = document.getElementById('captureBtn');
const liveDetectionToggle = document.getElementById('liveDetectionToggle');
const cameraPlaceholder = document.getElementById('cameraPlaceholder');
const statusText = document.getElementById('statusText');
const fpsCounter = document.getElementById('fpsCounter');
const detectionResults = document.getElementById('detectionResults');

// State variables
let stream = null;
let liveDetectionInterval = null;
let fpsInterval = null;
let lastFrameTime = Date.now();
let frameCount = 0;
let isProcessing = false;
let detectionQueue = [];

// Configuration
const CONFIG = {
    VIDEO_WIDTH: 1280,
    VIDEO_HEIGHT: 720,
    DETECTION_INTERVAL: 500,  // milliseconds
    FPS_UPDATE_INTERVAL: 1000,  // milliseconds
    CONFIDENCE_THRESHOLD: 0.25,
    MAX_QUEUE_SIZE: 5
};

// Initialize on page load
document.addEventListener('DOMContentLoaded', function() {
    console.log('Camera page loaded');
    setupEventListeners();
    checkCameraSupport();
});

/**
 * Setup all event listeners
 */
function setupEventListeners() {
    startBtn.addEventListener('click', handleStartCamera);
    stopBtn.addEventListener('click', handleStopCamera);
    captureBtn.addEventListener('click', handleCapture);
    liveDetectionToggle.addEventListener('change', handleLiveDetectionToggle);
    
    // Cleanup on page unload
    window.addEventListener('beforeunload', cleanup);
}

/**
 * Check if camera is supported
 */
function checkCameraSupport() {
    if (!navigator.mediaDevices || !navigator.mediaDevices.getUserMedia) {
        updateStatus('Camera not supported in this browser', 'error');
        startBtn.disabled = true;
    }
}

/**
 * Handle start camera button
 */
async function handleStartCamera() {
    try {
        updateStatus('Requesting camera access...', 'info');
        
        // Request camera access
        stream = await navigator.mediaDevices.getUserMedia({
            video: {
                width: { ideal: CONFIG.VIDEO_WIDTH },
                height: { ideal: CONFIG.VIDEO_HEIGHT },
                facingMode: 'environment'  // Use back camera on mobile
            },
            audio: false
        });
        
        // Set video source
        video.srcObject = stream;
        
        // Wait for video to be ready
        video.onloadedmetadata = function() {
            video.play();
            showCameraFeed();
            startFPSCounter();
            updateStatus('Camera Active', 'success');
        };
        
    } catch (error) {
        console.error('Camera error:', error);
        handleCameraError(error);
    }
}

/**
 * Handle camera errors
 */
function handleCameraError(error) {
    let message = 'Error accessing camera';
    
    if (error.name === 'NotAllowedError') {
        message = 'Camera permission denied. Please allow camera access.';
    } else if (error.name === 'NotFoundError') {
        message = 'No camera found on this device.';
    } else if (error.name === 'NotReadableError') {
        message = 'Camera is already in use by another application.';
    }
    
    alert(message);
    updateStatus('Camera Error', 'error');
}

/**
 * Show camera feed
 */
function showCameraFeed() {
    video.style.display = 'block';
    cameraPlaceholder.style.display = 'none';
    capturedImage.style.display = 'none';
    
    startBtn.style.display = 'none';
    stopBtn.style.display = 'inline-block';
    captureBtn.style.display = 'inline-block';
}

/**
 * Handle stop camera button
 */
function handleStopCamera() {
    stopCamera();
}

/**
 * Stop camera and cleanup
 */
function stopCamera() {
    // Stop video stream
    if (stream) {
        stream.getTracks().forEach(track => track.stop());
        stream = null;
    }
    
    // Stop live detection
    stopLiveDetection();
    
    // Stop FPS counter
    if (fpsInterval) {
        clearInterval(fpsInterval);
        fpsInterval = null;
    }
    
    // Reset UI
    video.style.display = 'none';
    capturedImage.style.display = 'none';
    cameraPlaceholder.style.display = 'flex';
    
    startBtn.style.display = 'inline-block';
    stopBtn.style.display = 'none';
    captureBtn.style.display = 'none';
    
    detectionResults.style.display = 'none';
    liveDetectionToggle.checked = false;
    
    updateStatus('Camera Stopped', 'idle');
    fpsCounter.textContent = 'FPS: 0';
}

/**
 * Handle capture button
 */
function handleCapture() {
    captureAndDetect(false);
}

/**
 * Handle live detection toggle
 */
function handleLiveDetectionToggle(e) {
    if (e.target.checked) {
        startLiveDetection();
    } else {
        stopLiveDetection();
    }
}

/**
 * Start live detection mode
 */
function startLiveDetection() {
    if (!stream) {
        liveDetectionToggle.checked = false;
        return;
    }
    
    updateStatus('Live Detection Active', 'live');
    
    // Start detection interval
    liveDetectionInterval = setInterval(() => {
        if (!isProcessing && detectionQueue.length < CONFIG.MAX_QUEUE_SIZE) {
            captureAndDetect(true);
        }
    }, CONFIG.DETECTION_INTERVAL);
}

/**
 * Stop live detection mode
 */
function stopLiveDetection() {
    if (liveDetectionInterval) {
        clearInterval(liveDetectionInterval);
        liveDetectionInterval = null;
    }
    
    detectionQueue = [];
    
    if (stream) {
        updateStatus('Camera Active', 'success');
        video.style.display = 'block';
        capturedImage.style.display = 'none';
    }
}

/**
 * Capture frame and send for detection
 */
async function captureAndDetect(isLive = false) {
    if (!video.videoWidth || !video.videoHeight) {
        console.warn('Video not ready');
        return;
    }
    
    isProcessing = true;
    
    try {
        // Capture frame
        const imageData = captureFrame();
        
        // Send for detection
        const result = await detectFrame(imageData);
        
        if (result.success) {
            displayLiveResults(result, isLive);
            frameCount++;
        } else {
            console.error('Detection failed:', result.error);
            if (!isLive) {
                alert('Detection failed: ' + result.error);
            }
        }
    } catch (error) {
        console.error('Detection error:', error);
        if (!isLive) {
            alert('Detection error: ' + error.message);
        }
    } finally {
        isProcessing = false;
    }
}

/**
 * Capture current video frame to base64
 */
function captureFrame() {
    // Set canvas size to match video
    canvas.width = video.videoWidth;
    canvas.height = video.videoHeight;
    
    // Draw current frame
    const ctx = canvas.getContext('2d');
    ctx.drawImage(video, 0, 0, canvas.width, canvas.height);
    
    // Convert to base64
    return canvas.toDataURL('image/jpeg', 0.8);
}

/**
 * Send frame to backend for detection
 */
async function detectFrame(imageData) {
    const response = await fetch('/detect_frame', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            image: imageData,
            confidence: CONFIG.CONFIDENCE_THRESHOLD
        })
    });
    
    return await response.json();
}

/**
 * Display detection results
 */
function displayLiveResults(data, isLive = false) {
    detectionResults.style.display = 'block';
    
    // Update item count
    updateItemCount(data.statistics.total_items);
    
    // Update category breakdown
    updateCategories(data.statistics.categories);
    
    // Update detection list
    updateDetectionList(data.detections);
    
    // Show annotated image if not in live mode
    if (!isLive) {
        showAnnotatedImage(data.annotated_image);
    }
}

/**
 * Update total item count
 */
function updateItemCount(count) {
    const element = document.getElementById('liveItemCount');
    if (element) {
        element.textContent = count;
        
        // Animate update
        element.classList.add('updated');
        setTimeout(() => element.classList.remove('updated'), 300);
    }
}

/**
 * Update category statistics
 */
function updateCategories(categories) {
    const container = document.getElementById('liveCategories');
    container.innerHTML = '';
    
    if (Object.keys(categories).length > 0) {
        for (const [category, count] of Object.entries(categories)) {
            const item = createCategoryItem(category, count);
            container.appendChild(item);
        }
    } else {
        container.innerHTML = '<p class="no-data">No items detected</p>';
    }
}

/**
 * Create category item element
 */
function createCategoryItem(category, count) {
    const item = document.createElement('div');
    item.className = 'category-item-live';
    
    const name = document.createElement('span');
    name.className = 'category-name';
    name.textContent = capitalize(category);
    
    const badge = document.createElement('span');
    badge.className = 'category-count';
    badge.textContent = count;
    
    item.appendChild(name);
    item.appendChild(badge);
    
    return item;
}

/**
 * Update detection list
 */
function updateDetectionList(detections) {
    const container = document.getElementById('detectionsListLive');
    container.innerHTML = '';
    
    if (detections.length > 0) {
        detections.forEach((detection, index) => {
            const item = createDetectionItem(detection, index + 1);
            container.appendChild(item);
        });
    } else {
        container.innerHTML = '<p class="no-data">No detections in current frame</p>';
    }
}

/**
 * Create detection list item
 */
function createDetectionItem(detection, index) {
    const item = document.createElement('div');
    item.className = 'detection-item';
    
    const number = document.createElement('span');
    number.className = 'detection-number';
    number.textContent = '#' + index;
    
    const className = document.createElement('span');
    className.className = 'detection-class';
    className.textContent = capitalize(detection.class);
    
    const confidence = document.createElement('span');
    confidence.className = 'detection-confidence';
    confidence.textContent = (detection.confidence * 100).toFixed(1) + '%';
    
    item.appendChild(number);
    item.appendChild(className);
    item.appendChild(confidence);
    
    return item;
}

/**
 * Show annotated image
 */
function showAnnotatedImage(base64Image) {
    capturedImage.src = base64Image;
    capturedImage.style.display = 'block';
    video.style.display = 'none';
}

/**
 * Start FPS counter
 */
function startFPSCounter() {
    fpsInterval = setInterval(() => {
        const now = Date.now();
        const elapsed = (now - lastFrameTime) / 1000;
        
        if (elapsed > 0) {
            const fps = frameCount / elapsed;
            fpsCounter.textContent = `FPS: ${fps.toFixed(1)}`;
        }
        
        lastFrameTime = now;
        frameCount = 0;
    }, CONFIG.FPS_UPDATE_INTERVAL);
}

/**
 * Update status text and color
 */
function updateStatus(text, type = 'idle') {
    statusText.textContent = text;
    
    const colors = {
        idle: '#999',
        info: '#2196F3',
        success: '#4CAF50',
        live: '#2196F3',
        error: '#f44336'
    };
    
    statusText.style.color = colors[type] || colors.idle;
}

/**
 * Capitalize first letter
 */
function capitalize(str) {
    if (!str) return '';
    return str.charAt(0).toUpperCase() + str.slice(1).toLowerCase();
}

/**
 * Cleanup resources
 */
function cleanup() {
    stopCamera();
}

/**
 * Export functions for testing
 */
if (typeof module !== 'undefined' && module.exports) {
    module.exports = {
        captureFrame,
        detectFrame,
        updateStatus,
        capitalize
    };
}