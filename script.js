// --- 1. CONFIGURATION ---
const API_BASE_URL = "http://localhost:8000"; // Your Backend
// Mock parking lots
const PARKING_LOTS = [
    { id: 'lot_st_thomas', name: 'St. Thomas College', lat: 10.5222, lng: 76.2177 },
    { id: 'lot_jubilee', name: 'Jubilee Park', lat: 10.5230, lng: 76.2185 },
    { id: 'lot_city_mall', name: 'City Mall Parking', lat: 10.5210, lng: 76.2155 },
    { id: 'lot_bus_stand', name: 'Bus Stand Lot', lat: 10.5205, lng: 76.2170 },
    { id: 'lot_railway', name: 'Railway Parking', lat: 10.5240, lng: 76.2160 }
];
const LOT_LOCATION = PARKING_LOTS[0];
const CAR_START = { lat: 10.5215, lng: 76.2165 };
let carMarker = null;
let isAutoDriving = false;
let carLatLng = { ...CAR_START };

// --- 2. INIT LEAFLET MAP ---
const map = L.map('map').setView([CAR_START.lat, CAR_START.lng], 18);
L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
    maxZoom: 20,
    attribution: '© OpenStreetMap contributors'
}).addTo(map);

// --- 3. ADD PARKING MARKER ---
// Custom Parking SVG Icon
const ParkingDivIcon = L.divIcon({
    className: '',
    iconSize: [40, 40],
    iconAnchor: [20, 40],
    html: `
        <div style="width:40px;height:40px;display:flex;align-items:center;justify-content:center;">
            <svg width="32" height="32" viewBox="0 0 32 32" fill="none" xmlns="http://www.w3.org/2000/svg">
                <circle cx="16" cy="16" r="15" fill="#fff" stroke="#4285f4" stroke-width="2"/>
                <text x="16" y="22" text-anchor="middle" font-size="18" font-family="Segoe UI, Arial, sans-serif" fill="#4285f4" font-weight="bold">P</text>
            </svg>
        </div>
    `
});
// Add all parking lot markers
PARKING_LOTS.forEach(lot => {
    L.marker([lot.lat, lot.lng], {
        icon: ParkingDivIcon,
        title: lot.name
    })
    .addTo(map)
    .bindPopup(`<b>${lot.name}</b><br>Parking Lot`)
    .on('click', () => openSidebar(lot.id));
});

// --- 4. ADD CAR MARKER ---
// Custom HTML marker for 3D car effect
let carAngle = 0;
const CarDivIcon = L.divIcon({
    className: '',
    iconSize: [44, 70],
    iconAnchor: [22, 35],
        html: `<div class="custom-car-marker" style="width:44px;height:70px;display:flex;align-items:center;justify-content:center;">
            <svg width="38" height="60" viewBox="0 0 38 60" xmlns="http://www.w3.org/2000/svg" style="display:block;">
                <polygon points="19,8 32,52 19,44 6,52" fill="#4285f4" stroke="#222" stroke-width="2" />
            </svg>
        </div>`
        // html: `<div class="custom-car-marker" style="width:44px;height:70px;display:flex;align-items:center;justify-content:center;">
        // </div>`
});
carMarker = L.marker([CAR_START.lat, CAR_START.lng], {
    icon: CarDivIcon,
    title: 'Your Car',
    draggable: false
}).addTo(map);

// --- 5. DISTANCE DISPLAY ---
function updateDistanceDisplay() {
    const dist = map.distance([carLatLng.lat, carLatLng.lng], [LOT_LOCATION.lat, LOT_LOCATION.lng]);
    document.getElementById('distance-display').innerText = Math.round(dist) + 'm away';
}
updateDistanceDisplay();

// --- 6. CAR MOVEMENT (ARROW KEYS) ---
let keys = {};
function moveCar() {
    let moved = false;
    let dLat = 0, dLng = 0;
    const step = 0.000012; // ~1.2m per keypress, slower
    if (keys['ArrowUp'])    { dLat += step; moved = true; carAngle = 0; }
    if (keys['ArrowDown'])  { dLat -= step; moved = true; carAngle = 180; }
    if (keys['ArrowLeft'])  { dLng -= step; moved = true; carAngle = 270; }
    if (keys['ArrowRight']) { dLng += step; moved = true; carAngle = 90; }
    // Diagonal movement angle
    if (keys['ArrowUp'] && keys['ArrowLeft']) carAngle = 315;
    if (keys['ArrowUp'] && keys['ArrowRight']) carAngle = 45;
    if (keys['ArrowDown'] && keys['ArrowLeft']) carAngle = 225;
    if (keys['ArrowDown'] && keys['ArrowRight']) carAngle = 135;
    if (moved) {
        carLatLng.lat += dLat;
        carLatLng.lng += dLng;
        carMarker.setLatLng([carLatLng.lat, carLatLng.lng]);
        // Rotate only the inner car div, not the marker container
        const carEl = carMarker.getElement();
        if (carEl) {
            const carBody = carEl.querySelector('.custom-car-marker');
            if (carBody) carBody.style.transform = `rotate(${carAngle}deg)`;
        }
        map.panTo([carLatLng.lat, carLatLng.lng]);
        updateDistanceDisplay();
    }
    requestAnimationFrame(moveCar);
}
window.addEventListener('keydown', e => { keys[e.code] = true; });
window.addEventListener('keyup', e => { keys[e.code] = false; });
requestAnimationFrame(moveCar);

// --- 7. AUTO DRIVE FEATURE ---
function startAutoDrive() {
    isAutoDriving = true;
    const target = [LOT_LOCATION.lat, LOT_LOCATION.lng];
    const interval = setInterval(() => {
        const dist = map.distance([carLatLng.lat, carLatLng.lng], target);
        if (dist < 10) {
            clearInterval(interval);
            isAutoDriving = false;
            openSidebar('lot_st_thomas');
            return;
        }
        // Move car towards target
        const dLat = (target[0] - carLatLng.lat) * 0.08;
        const dLng = (target[1] - carLatLng.lng) * 0.08;
        carLatLng.lat += dLat;
        carLatLng.lng += dLng;
        // Calculate angle
        carAngle = Math.atan2(dLng, dLat) * 180 / Math.PI;
        carMarker.setLatLng([carLatLng.lat, carLatLng.lng]);
        const carEl = carMarker.getElement();
        if (carEl) {
            const carBody = carEl.querySelector('.custom-car-marker');
            if (carBody) carBody.style.transform = `rotate(${carAngle}deg)`;
        }
        map.panTo([carLatLng.lat, carLatLng.lng]);
        updateDistanceDisplay();
    }, 16);
}

function findParking() {
    // Calculate distances to all lots
    const lotsWithDistance = PARKING_LOTS.map(lot => ({
        ...lot,
        distance: map.distance([carLatLng.lat, carLatLng.lng], [lot.lat, lot.lng])
    }));
    lotsWithDistance.sort((a, b) => a.distance - b.distance);
    // Show list in sidebar
    let html = `
    <div style='padding:0;'>
        <div style="display:flex;justify-content:space-between;align-items:center;padding:20px 20px 10px 20px;border-bottom:1px solid #eee;">
            <h3 style="margin:0;font-size:22px;color:#333;">Nearby Parking Lots</h3>
            <button onclick="window.closeSidebarPanel()" style="background:#f1f3f4;border:none;width:36px;height:36px;border-radius:50%;font-size:22px;cursor:pointer;">×</button>
        </div>
        <ul style='list-style:none;padding:20px;'>`;
    lotsWithDistance.forEach(lot => {
        html += `
            <li style='margin-bottom:18px;padding:16px 18px;background:#f8f9fa;border-radius:10px;box-shadow:0 2px 8px rgba(66,133,244,0.07);display:flex;justify-content:space-between;align-items:center;'>
                <div>
                    <b style="font-size:17px;color:#222;">${lot.name}</b><br>
                    <span style='color:#4285f4;font-size:15px;'>${Math.round(lot.distance)}m away</span>
                </div>
                <button onclick="window.selectLot('${lot.id}')" style='padding:7px 18px;border-radius:8px;border:none;background:#4285f4;color:#fff;cursor:pointer;font-size:15px;font-weight:500;box-shadow:0 2px 8px rgba(66,133,244,0.12);'>Select</button>
            </li>`;
    });
    html += `</ul></div>`;
    document.getElementById('sidebar').classList.add('active');
    document.getElementById('sidebar').innerHTML = html;
    // Helper for selecting lot
    window.selectLot = function(lotId) {
        const lot = PARKING_LOTS.find(l => l.id === lotId);
        if (!lot) return;
        map.panTo([lot.lat, lot.lng]);
        if (window.routeLine) map.removeLayer(window.routeLine);
        window.routeLine = L.polyline([
            [carLatLng.lat, carLatLng.lng],
            [lot.lat, lot.lng]
        ], { color: '#4285f4', weight: 4, dashArray: '8 8' }).addTo(map);
    };
    window.closeSidebarPanel = function() {
        document.getElementById('sidebar').classList.remove('active');
    };
}

// --- 8. SIDEBAR & LIVE FEED (unchanged) ---
let pollingInterval = null;
let cachedConfig = [];
async function openSidebar(lotId) {
    // Restore the original parking lot info panel
    let lot = PARKING_LOTS.find(l => l.id === lotId) || PARKING_LOTS[0];
    let html = `
        <div class="sidebar-header">
            <div class="sidebar-title">
                <h2 id="sidebar-name">${lot.name}</h2>
                <p id="sidebar-meta">Live Occupancy Feed • <span style="color:#0f9d58">Connecting...</span></p>
            </div>
            <button class="close-btn" onclick="window.closeSidebarPanel()">×</button>
        </div>
        <div class="sidebar-details" style="padding: 0 20px 20px 20px; color: #444; font-size: 15px;">
            <b>Details:</b>
            <p>Lorem ipsum dolor sit amet, consectetur adipiscing elit. Pellentesque euismod, urna eu tincidunt consectetur, nisi nisl aliquam nunc, eget aliquam massa nisl quis neque. Proin ac neque nec nisi blandit commodo.</p>
        </div>
        <div id="live-grid-container">
            <img id="live-map-img" src="st_thomas_top_down.png" alt="Live View">
            <div id="live-slots-layer"></div>
        </div>
    `;
    document.getElementById('sidebar').classList.add('active');
    document.getElementById('sidebar').innerHTML = html;
    window.closeSidebarPanel = function() {
        document.getElementById('sidebar').classList.remove('active');
    };
    // Optionally, fetch and show live data as before
    try {
        const res = await fetch(`${API_BASE_URL}/api/config`);
        const config = await res.json();
        cachedConfig = config.slots;
        startLivePolling();
    } catch (e) {
        console.error("Backend Error", e);
        document.getElementById('sidebar-meta').innerText = "Backend Offline - Check Server";
        document.getElementById('sidebar-meta').style.color = "red";
    }
}
function closeSidebar() {
    document.getElementById('sidebar').classList.remove('active');
    if (pollingInterval) clearInterval(pollingInterval);
}
function startLivePolling() {
    pollingInterval = setInterval(async () => {
        try {
            const res = await fetch(`${API_BASE_URL}/api/status`);
            const data = await res.json();
            renderLiveGrid(data.status_string);
            const occupied = (data.status_string.match(/1|C|S|B/g) || []).length;
            const free = data.status_string.length - occupied;
            document.getElementById('sidebar-meta').innerHTML = `Live Feed • <span style="color:#0f9d58"><b>${free}</b> Slots Available</span>`;
        } catch (e) { console.warn("Poll failed"); }
    }, 1000);
}
function renderLiveGrid(statusString) {
    const layer = document.getElementById('live-slots-layer');
    layer.innerHTML = '';
    const originalW = 800;
    const containerW = document.getElementById('live-grid-container').offsetWidth;
    const scale = containerW / originalW;
    cachedConfig.forEach((slot, index) => {
        const state = statusString[index] || '0';
        const div = document.createElement('div');
        div.className = 'live-slot';
        if (state !== '0') div.classList.add('occupied');
        const coords = slot.coordinates || slot;
        div.style.left = (coords.x * scale) + 'px';
        div.style.top = (coords.y * scale) + 'px';
        div.style.width = (coords.w * scale) + 'px';
        div.style.height = (coords.h * scale) + 'px';
        layer.appendChild(div);
    });
}