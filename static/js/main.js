/**
 * EcoLocate - Main JavaScript Application (Phases 1-5)
 * Handles navigation, directory searching & filtering, Leaflet.js interactive mapping,
 * geolocation detection, Haversine nearest centre calculations, and form validations.
 */

document.addEventListener('DOMContentLoaded', () => {
  initNavigation();
  initCentresDirectory();
  initAuthValidation();
});

/* ==========================================================================
   Navigation & Mobile Menu
   ========================================================================== */
function initNavigation() {
  const mobileToggle = document.querySelector('.mobile-toggle');
  const siteHeader = document.querySelector('.site-header');

  if (mobileToggle && siteHeader) {
    mobileToggle.addEventListener('click', () => {
      const isExpanded = mobileToggle.getAttribute('aria-expanded') === 'true';
      mobileToggle.setAttribute('aria-expanded', !isExpanded);
      siteHeader.classList.toggle('mobile-nav-active');
    });

    // Close mobile menu when clicking outside
    document.addEventListener('click', (e) => {
      if (!siteHeader.contains(e.target) && siteHeader.classList.contains('mobile-nav-active')) {
        siteHeader.classList.remove('mobile-nav-active');
        mobileToggle.setAttribute('aria-expanded', 'false');
      }
    });
  }

  // Highlight current page nav link
  const currentPath = window.location.pathname.split('/').pop() || 'index.html';
  const navLinks = document.querySelectorAll('.nav-link');
  navLinks.forEach(link => {
    const href = link.getAttribute('href');
    if (href === currentPath || (currentPath === '' && href === 'index.html')) {
      link.classList.add('active');
    }
  });
}

/* ==========================================================================
   Phases 4 & 5: Interactive Map, Directory Filters, & Nearest Centres
   ========================================================================== */
function initCentresDirectory() {
  const container = document.getElementById('centres-grid-container');
  if (!container) return; // Not on the centres directory page

  const stateSelect = document.getElementById('filter-state');
  const citySelect = document.getElementById('filter-city');
  const deviceSelect = document.getElementById('filter-device');
  const searchInput = document.getElementById('filter-search');
  const searchBtn = document.getElementById('search-centres-btn');
  const locationBtn = document.getElementById('use-location-btn');
  const resetBtn = document.getElementById('reset-filters-btn');
  const resultsCountEl = document.getElementById('results-count');
  const activeFiltersEl = document.getElementById('active-filters-container');
  const paginationContainer = document.getElementById('pagination-container');
  const nearestBanner = document.getElementById('nearest-notice-banner');
  const nearestBannerText = document.getElementById('nearest-banner-text');
  const clearLocationBtn = document.getElementById('clear-location-btn');
  const resetMapViewBtn = document.getElementById('btn-reset-map-view');
  const mapStatsBadge = document.getElementById('map-stats-badge');

  let currentPage = 1;
  const itemsPerPage = 10;
  let currentCoords = null; // { lat, lng } in-memory only (never stored in DB)
  let isNearestMode = false;

  // Leaflet Map State
  let map = null;
  let facilityLayerGroup = null;
  let userMarker = null;
  let allMappedCentres = [];

  // Initialize Map, Dropdowns, and Directory
  initMap();
  initFilterDropdowns();
  fetchCentres(1);

  // --------------------------------------------------------------------------
  // 1. Interactive Leaflet.js Map Initialization
  // --------------------------------------------------------------------------
  function initMap() {
    const mapEl = document.getElementById('map');
    if (!mapEl) return;

    if (typeof L === 'undefined') {
      console.warn('Leaflet library is loading or unavailable. Retrying in 500ms...');
      setTimeout(initMap, 500);
      return;
    }

    try {
      // Centered on geographic India
      map = L.map('map', {
        scrollWheelZoom: false,
        zoomControl: true
      }).setView([21.7679, 78.8718], 5);

      // OpenStreetMap Tile Layer (Free, no API key required)
      L.tileLayer('https://{s}.tile.openstreetmap.org/{z}/{x}/{y}.png', {
        maxZoom: 19,
        attribution: '&copy; <a href="https://www.openstreetmap.org/copyright" target="_blank">OpenStreetMap</a> contributors'
      }).addTo(map);

      facilityLayerGroup = L.featureGroup().addTo(map);

      // Load all verified facility coordinates from backend API
      loadMapFacilities();

      // Reset Map View Button
      if (resetMapViewBtn) {
        resetMapViewBtn.addEventListener('click', () => {
          if (facilityLayerGroup && facilityLayerGroup.getLayers().length > 0) {
            map.fitBounds(facilityLayerGroup.getBounds().pad(0.12));
          } else {
            map.setView([21.7679, 78.8718], 5);
          }
        });
      }
    } catch (err) {
      console.error('Error initializing Leaflet map:', err);
    }
  }

  function loadMapFacilities() {
    fetch('/api/centres/map')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.centres) {
          allMappedCentres = data.centres;
          plotFacilityMarkers(allMappedCentres);
          if (mapStatsBadge) {
            mapStatsBadge.textContent = `${data.total} Verified Facilities Mapped`;
          }
        }
      })
      .catch(err => {
        console.error('Failed to load map facility coordinates:', err);
        if (mapStatsBadge) {
          mapStatsBadge.textContent = 'Map Ready (OpenStreetMap)';
        }
      });
  }

  function plotFacilityMarkers(centresList) {
    if (!facilityLayerGroup) return;
    facilityLayerGroup.clearLayers();

    centresList.forEach(c => {
      if (c.latitude && c.longitude) {
        const marker = createFacilityMarker(c);
        facilityLayerGroup.addLayer(marker);
      }
    });

    if (facilityLayerGroup.getLayers().length > 0 && !currentCoords) {
      map.fitBounds(facilityLayerGroup.getBounds().pad(0.12));
    }
  }

  function createFacilityMarker(c) {
    // Custom SVG Pin Icon
    const facilityIcon = L.divIcon({
      className: 'custom-facility-pin-wrapper',
      html: '<div class="custom-facility-pin" title="' + escapeHtml(c.centre_name) + '"></div>',
      iconSize: [28, 28],
      iconAnchor: [14, 28],
      popupAnchor: [0, -28]
    });

    const marker = L.marker([parseFloat(c.latitude), parseFloat(c.longitude)], {
      icon: facilityIcon,
      title: c.centre_name
    });

    // Determine direction URL based on whether user location is active
    let directionsUrl;
    if (currentCoords) {
      directionsUrl = `https://www.google.com/maps/dir/?api=1&origin=${currentCoords.lat},${currentCoords.lng}&destination=${c.latitude},${c.longitude}`;
    } else {
      directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${c.latitude},${c.longitude}`;
    }

    const distanceHtml = (typeof c.distance_km === 'number')
      ? `<div class="map-popup-distance">📍 ${c.distance_km} km from your location</div>`
      : '';

    const websiteBtnHtml = (c.website_url && c.website_url.trim())
      ? `<a href="${c.website_url.trim()}" target="_blank" rel="noopener noreferrer" class="btn btn-outline btn-sm">Visit Website</a>`
      : '';

    const popupContent = `
      <div class="map-popup-card">
        <div class="map-popup-badge">${escapeHtml(c.centre_type || 'Authorised Recycler')}</div>
        <h4 class="map-popup-title">${escapeHtml(c.centre_name)}</h4>
        <p class="map-popup-address">📍 ${escapeHtml(c.address)}</p>
        <div class="map-popup-meta">
          <span>State: <strong>${escapeHtml(c.state)}</strong> • City: <strong>${escapeHtml(c.city)}</strong></span>
          ${c.capacity_mta ? `<span>Capacity: <strong>${escapeHtml(c.capacity_mta)} MTA</strong></span>` : ''}
        </div>
        ${distanceHtml}
        <div class="map-popup-actions">
          <a href="${directionsUrl}" target="_blank" rel="noopener noreferrer" class="btn btn-primary btn-sm">
            Get Directions
          </a>
          ${websiteBtnHtml}
        </div>
      </div>
    `;

    marker.bindPopup(popupContent, { maxWidth: 320 });
    return marker;
  }

  // --------------------------------------------------------------------------
  // 2. Dropdown Filter Initialization
  // --------------------------------------------------------------------------
  function initFilterDropdowns() {
    if (stateSelect && stateSelect.options.length <= 1) {
      fetch('/api/states')
        .then(res => res.json())
        .then(data => {
          if (data.success && data.states) {
            data.states.forEach(st => {
              const opt = document.createElement('option');
              opt.value = st;
              opt.textContent = st;
              stateSelect.appendChild(opt);
            });
          }
        })
        .catch(err => console.log('State fetch info:', err));
    }

    if (stateSelect && citySelect) {
      stateSelect.addEventListener('change', () => {
        const selectedState = stateSelect.value.trim();
        citySelect.innerHTML = '<option value="">All Cities</option>';

        const cityUrl = selectedState 
          ? `/api/cities?state=${encodeURIComponent(selectedState)}`
          : '/api/cities';

        fetch(cityUrl)
          .then(res => res.json())
          .then(data => {
            if (data.success && data.cities) {
              data.cities.forEach(city => {
                const opt = document.createElement('option');
                opt.value = city;
                opt.textContent = city;
                citySelect.appendChild(opt);
              });
            }
          })
          .catch(err => console.log('City fetch error:', err));

        // When standard filter changes, exit nearest mode
        exitNearestMode(false);
        fetchCentres(1);
      });
    }

    if (citySelect) {
      citySelect.addEventListener('change', () => {
        exitNearestMode(false);
        fetchCentres(1);
      });
    }

    if (deviceSelect) {
      deviceSelect.addEventListener('change', () => {
        exitNearestMode(false);
        fetchCentres(1);
      });
    }

    if (searchInput) {
      let debounceTimer;
      searchInput.addEventListener('input', () => {
        clearTimeout(debounceTimer);
        debounceTimer = setTimeout(() => {
          exitNearestMode(false);
          fetchCentres(1);
        }, 400);
      });
    }
  }

  // --------------------------------------------------------------------------
  // 3. Fetch Standard Directory Records (/api/centres)
  // --------------------------------------------------------------------------
  function fetchCentres(page = 1) {
    currentPage = page;
    isNearestMode = false;

    container.innerHTML = `
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p style="color: var(--text-muted); font-size: 0.95rem;">Retrieving facilities from database...</p>
      </div>
    `;

    const state = stateSelect ? stateSelect.value.trim() : '';
    const city = citySelect ? citySelect.value.trim() : '';
    const deviceId = deviceSelect ? deviceSelect.value.trim() : '';
    const keyword = searchInput ? searchInput.value.trim() : '';

    const params = new URLSearchParams({
      page: currentPage,
      limit: itemsPerPage
    });

    if (state) params.append('state', state);
    if (city) params.append('city', city);
    if (deviceId) params.append('device_id', deviceId);
    if (keyword) params.append('q', keyword);

    // If user coordinates exist in session, include them so API computes distance
    if (currentCoords) {
      params.append('user_lat', currentCoords.lat);
      params.append('user_lng', currentCoords.lng);
    }

    fetch(`/api/centres?${params.toString()}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (data.success) {
          renderCentres(data.centres, data.total, false);
          renderPagination(data.page, data.total_pages);
          updateActiveFilterPills(state, city, deviceId, keyword);
        } else {
          showErrorState(data.error || 'Could not load facilities');
        }
      })
      .catch(err => {
        console.error('Fetch error:', err);
        showErrorState('Failed to connect to the backend server. Please verify Flask and MySQL are running.');
      });
  }

  // --------------------------------------------------------------------------
  // 4. Geolocation Detection & Nearest Centre Calculation (/api/centres/nearby)
  // --------------------------------------------------------------------------
  function handleUseLocation() {
    if (!navigator.geolocation) {
      showToast('Geolocation is not supported by your browser.', 'error');
      showFallbackLocationPrompt();
      return;
    }

    // Indicate loading state on button
    const originalText = locationBtn.innerHTML;
    locationBtn.disabled = true;
    locationBtn.innerHTML = `
      <div class="loading-spinner" style="width: 14px; height: 14px; border-width: 2px;"></div>
      Detecting Location...
    `;

    navigator.geolocation.getCurrentPosition(
      (position) => {
        locationBtn.disabled = false;
        locationBtn.innerHTML = originalText;

        const lat = position.coords.latitude;
        const lng = position.coords.longitude;

        applyUserLocation(lat, lng, 'Browser GPS');
      },
      (error) => {
        locationBtn.disabled = false;
        locationBtn.innerHTML = originalText;

        let errorMsg = 'Could not retrieve your location.';
        switch (error.code) {
          case error.PERMISSION_DENIED:
            errorMsg = 'Location permission was denied in your browser.';
            break;
          case error.POSITION_UNAVAILABLE:
            errorMsg = 'Location information is currently unavailable.';
            break;
          case error.TIMEOUT:
            errorMsg = 'Location detection request timed out.';
            break;
        }

        showToast(errorMsg + ' You can select a test location below.', 'info');
        showFallbackLocationPrompt();
      },
      {
        enableHighAccuracy: true,
        timeout: 10000,
        maximumAge: 60000
      }
    );
  }

  function applyUserLocation(lat, lng, sourceLabel = 'Current Location') {
    // 1. Store in memory for active view (NEVER in database)
    currentCoords = { lat: parseFloat(lat), lng: parseFloat(lng) };
    isNearestMode = true;

    // 2. Show loading feedback
    container.innerHTML = `
      <div class="loading-container">
        <div class="loading-spinner"></div>
        <p style="color: var(--text-muted); font-size: 0.95rem;">
          Calculating Haversine distances to verified recycling facilities...
        </p>
      </div>
    `;

    // 3. Update User Marker on Leaflet Map
    if (map) {
      const userIcon = L.divIcon({
        className: 'custom-user-pin-wrapper',
        html: '<div class="custom-user-pin" title="Your Location"></div>',
        iconSize: [22, 22],
        iconAnchor: [11, 11],
        popupAnchor: [0, -12]
      });

      if (userMarker) {
        userMarker.setLatLng([currentCoords.lat, currentCoords.lng]);
      } else {
        userMarker = L.marker([currentCoords.lat, currentCoords.lng], {
          icon: userIcon,
          zIndexOffset: 1000,
          title: 'Your Location'
        }).addTo(map);

        userMarker.bindPopup(`
          <div style="padding: 0.6rem 0.8rem; font-size: 0.875rem;">
            <strong style="color: #2563eb;">📍 Your Detected Location</strong>
            <div style="color: var(--text-muted); font-size: 0.8rem; margin-top: 0.25rem;">
              ${currentCoords.lat.toFixed(4)}° N, ${currentCoords.lng.toFixed(4)}° E
            </div>
          </div>
        `);
      }
    }

    // 4. Send Coordinates to Flask Backend (/api/centres/nearby)
    fetch(`/api/centres/nearby?lat=${currentCoords.lat}&lng=${currentCoords.lng}`)
      .then(res => {
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        return res.json();
      })
      .then(data => {
        if (data.success) {
          renderNearestResults(data);
          showToast(`Located ${data.count} facilities sorted by proximity (${sourceLabel})`, 'success');
        } else {
          showErrorState(data.error || 'Failed to calculate nearest centres');
        }
      })
      .catch(err => {
        console.error('Nearby fetch error:', err);
        showErrorState('Failed to retrieve nearest facilities from server.');
      });
  }

  function renderNearestResults(data) {
    const list = data.centres || [];

    // Show and update Nearest Notice Banner
    if (nearestBanner) {
      nearestBanner.style.display = 'flex';
      if (nearestBannerText) {
        nearestBannerText.innerHTML = `
          Detected <strong>${currentCoords.lat.toFixed(4)}° N, ${currentCoords.lng.toFixed(4)}° E</strong>. 
          Found <strong>${data.count}</strong> facilities with verified coordinates sorted from nearest to farthest. 
          <em>(${data.total_without_coordinates} facilities lack GPS coordinates and remain searchable below).</em>
        `;
      }
    }

    if (resultsCountEl) {
      resultsCountEl.innerHTML = `Showing <span>${list.length}</span> nearest verified recycling facilities (sorted by distance)`;
    }

    // Hide pagination controls in nearest proximity view
    if (paginationContainer) {
      paginationContainer.style.display = 'none';
    }

    // Render cards with distance badges
    renderCentres(list, list.length, true);

    // Zoom and pan Leaflet map to encompass user location and nearest facilities
    if (map && userMarker) {
      const markersToFit = [userMarker];
      if (facilityLayerGroup) {
        facilityLayerGroup.eachLayer(layer => markersToFit.push(layer));
      }
      try {
        const group = L.featureGroup(markersToFit);
        map.fitBounds(group.getBounds().pad(0.15));
      } catch (e) {
        map.setView([currentCoords.lat, currentCoords.lng], 9);
      }
    }
  }

  function exitNearestMode(fetchDirectory = true) {
    isNearestMode = false;
    currentCoords = null;

    if (nearestBanner) {
      nearestBanner.style.display = 'none';
    }

    if (userMarker && map) {
      map.removeLayer(userMarker);
      userMarker = null;
    }

    if (fetchDirectory) {
      fetchCentres(1);
    }
  }

  // --------------------------------------------------------------------------
  // 5. Render Recycling Centre Cards
  // --------------------------------------------------------------------------
  function renderCentres(list, totalCount, isNearest = false) {
    container.innerHTML = '';

    if (!isNearest && resultsCountEl) {
      if (totalCount === 0) {
        resultsCountEl.innerHTML = `No verified facilities found matching your criteria`;
      } else {
        const start = ((currentPage - 1) * itemsPerPage) + 1;
        const end = Math.min(currentPage * itemsPerPage, totalCount);
        resultsCountEl.innerHTML = `Showing <span>${start}-${end}</span> of <span>${totalCount}</span> verified recycling facilities`;
      }
    }

    if (!list || list.length === 0) {
      container.innerHTML = `
        <div class="empty-state">
          <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
            <path stroke-linecap="round" stroke-linejoin="round" stroke-width="1.5" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
          </svg>
          <h3>No Facilities Found</h3>
          <p>No authorized centres match your current search or location criteria. You can clear your filters or view all national facilities.</p>
          <button type="button" class="btn btn-outline btn-sm" id="empty-reset-btn">Reset All Filters</button>
        </div>
      `;
      const emptyReset = document.getElementById('empty-reset-btn');
      if (emptyReset) {
        emptyReset.addEventListener('click', resetFilters);
      }
      return;
    }

    list.forEach(c => {
      const card = document.createElement('div');
      card.className = 'centre-card';

      // Directions Link: Use coordinates if available, otherwise address fallback
      let directionsUrl;
      if (c.latitude && c.longitude) {
        if (currentCoords) {
          directionsUrl = `https://www.google.com/maps/dir/?api=1&origin=${currentCoords.lat},${currentCoords.lng}&destination=${c.latitude},${c.longitude}`;
        } else {
          directionsUrl = `https://www.google.com/maps/dir/?api=1&destination=${c.latitude},${c.longitude}`;
        }
      } else {
        directionsUrl = `https://www.google.com/maps/search/?api=1&query=${encodeURIComponent(c.centre_name + ' ' + c.address)}`;
      }

      // Distance Badge: Displayed when Haversine calculation has been performed
      let distanceBadgeHtml = '';
      if (typeof c.distance_km === 'number') {
        distanceBadgeHtml = `
          <span class="centre-badge badge-distance" title="${c.distance_km} km direct distance from your coordinates">
            📍 ${c.distance_km} km away
          </span>
        `;
      } else if (c.latitude && c.longitude) {
        distanceBadgeHtml = `
          <span class="centre-badge" style="background: #ecfdf5; color: #065f46; border: 1px solid #a7f3d0;" title="Geographic GPS coordinates verified">
            GPS Mapped
          </span>
        `;
      } else {
        distanceBadgeHtml = `
          <span class="centre-badge badge-no-coords" title="GPS coordinates pending official verification; address navigation available">
            Coords Pending
          </span>
        `;
      }

      // Website Button: Render ONLY when a real website URL exists
      let websiteBtnHtml = '';
      if (c.website_url && c.website_url.trim()) {
        const verificationNote = c.website_verification || 'Official domain verified';
        websiteBtnHtml = `
          <a href="${c.website_url.trim()}" 
             target="_blank" 
             rel="noopener noreferrer" 
             class="btn btn-outline btn-sm" 
             title="${verificationNote}">
            <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M10 6H6a2 2 0 00-2 2v10a2 2 0 002 2h10a2 2 0 002-2v-4M14 4h6m0 0v6m0-6L10 14"></path>
            </svg>
            Visit Official Website
          </a>
        `;
      }

      // Call Button: Render ONLY when verified phone number exists
      let callBtnHtml = '';
      if (c.phone_number && c.phone_number.trim()) {
        callBtnHtml = `
          <a href="tel:${c.phone_number.trim()}" class="btn btn-outline btn-sm">
            <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 5a2 2 0 012-2h3.28a1 1 0 01.948.684l1.498 4.493a1 1 0 01-.502 1.21l-2.257 1.13a11.042 11.042 0 005.516 5.516l1.13-2.257a1 1 0 011.21-.502l4.493 1.498a1 1 0 01.684.949V19a2 2 0 01-2 2h-1C9.716 21 3 14.284 3 6V5z"></path>
            </svg>
            Call Centre
          </a>
        `;
      }

      // Email Button: Render ONLY when verified email exists
      let emailBtnHtml = '';
      if (c.email && c.email.trim()) {
        emailBtnHtml = `
          <a href="mailto:${c.email.trim()}" class="btn btn-outline btn-sm">
            <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M3 8l7.89 5.26a2 2 0 002.22 0L21 8M5 19h14a2 2 0 002-2V7a2 2 0 00-2-2H5a2 2 0 00-2 2v10a2 2 0 002 2z"></path>
            </svg>
            Send Email
          </a>
        `;
      }

      // Fallback Search Contact: Render when direct website, phone, and email are all missing
      let fallbackSearchBtnHtml = '';
      if (!websiteBtnHtml && !callBtnHtml && !emailBtnHtml) {
        const searchQuery = encodeURIComponent(`${c.centre_name} ${c.city} e-waste contact`);
        fallbackSearchBtnHtml = `
          <a href="https://www.google.com/search?q=${searchQuery}" 
             target="_blank" 
             rel="noopener noreferrer" 
             class="btn btn-outline btn-sm"
             style="color: var(--text-muted);"
             title="Search publicly available telephone numbers and directories on Google">
            <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M21 21l-6-6m2-5a7 7 0 11-14 0 7 7 0 0114 0z"></path>
            </svg>
            Find Contact Details
          </a>
        `;
      }

      // Verification Badge
      const isWebsiteVerified = Boolean(c.website_url && c.website_url.trim());
      const websiteBadgeHtml = isWebsiteVerified
        ? `<span class="centre-badge badge-verified" title="${c.website_verification || 'Verified official domain'}">Official Website • Verified</span>`
        : `<span class="centre-badge badge-unverified" title="${c.website_verification || 'Not independently listed'}">Unverified Web Listing</span>`;

      // Device Acceptance Note or Badges
      let deviceAcceptanceHtml = '';
      if (c.accepted_devices) {
        const badges = c.accepted_devices.split(',').map(d => `<span class="category-tag">${escapeHtml(d.trim())}</span>`).join('');
        deviceAcceptanceHtml = `
          <div class="centre-categories">
            <div class="categories-label">Accepted Categories</div>
            <div class="category-tags">${badges}</div>
          </div>
        `;
      } else {
        deviceAcceptanceHtml = `
          <div style="font-size: 0.8125rem; color: var(--text-light); margin-bottom: 1.25rem;">
            Authorized dismantler/recycler compliant with CPCB e-waste streams.
          </div>
        `;
      }

      card.innerHTML = `
        <div>
          <div class="centre-card-header">
            <div>
              <h3 class="centre-name">${escapeHtml(c.centre_name)}</h3>
              <div style="font-size: 0.875rem; font-weight: 600; color: var(--primary); margin-top: 0.25rem;">
                ${escapeHtml(c.city)}, ${escapeHtml(c.state)}
              </div>
            </div>
            <div style="display: flex; flex-direction: column; align-items: flex-end; gap: 0.35rem;">
              <span class="centre-badge badge-cpcb">${escapeHtml(c.centre_type || 'Authorised Recycler')}</span>
              ${distanceBadgeHtml}
              ${websiteBadgeHtml}
            </div>
          </div>

          <p class="centre-address">
            <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M17.657 16.657L13.414 20.9a1.998 1.998 0 01-2.827 0l-4.244-4.243a8 8 0 1111.314 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 11a3 3 0 11-6 0 3 3 0 016 0z"></path>
            </svg>
            <span>${escapeHtml(c.address)}</span>
          </p>

          <div class="centre-meta">
            <div class="meta-item">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M19 11H5m14 0a2 2 0 012 2v6a2 2 0 01-2 2H5a2 2 0 01-2-2v-6a2 2 0 012-2m14 0V9a2 2 0 00-2-2M5 11V9a2 2 0 012-2m0 0V5a2 2 0 012-2h6a2 2 0 012 2v2M7 7h10"></path>
              </svg>
              <span>Capacity: <strong>${c.capacity_mta ? escapeHtml(c.capacity_mta) + ' MTA' : 'Authorized'}</strong></span>
            </div>
            <div class="meta-item">
              <svg fill="none" stroke="currentColor" viewBox="0 0 24 24">
                <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M9 12l2 2 4-4m6 2a9 9 0 11-18 0 9 9 0 0118 0z"></path>
              </svg>
              <span>Source: <strong>${escapeHtml(c.source || 'CPCB Registry')}</strong></span>
            </div>
          </div>

          ${deviceAcceptanceHtml}
        </div>

        <div class="centre-actions">
          <a href="${directionsUrl}" 
             target="_blank" 
             rel="noopener noreferrer" 
             class="btn btn-primary btn-sm">
            <svg width="15" height="15" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M14 5l7 7m0 0l-7 7m7-7H3"></path>
            </svg>
            Get Directions
          </a>
          ${websiteBtnHtml}
          ${callBtnHtml}
          ${emailBtnHtml}
          ${fallbackSearchBtnHtml}
        </div>
      `;

      container.appendChild(card);
    });
  }

  // --------------------------------------------------------------------------
  // 6. Pagination Controls
  // --------------------------------------------------------------------------
  function renderPagination(page, totalPages) {
    if (!paginationContainer) return;

    if (totalPages <= 1 || isNearestMode) {
      paginationContainer.style.display = 'none';
      paginationContainer.innerHTML = '';
      return;
    }

    paginationContainer.style.display = 'flex';
    paginationContainer.innerHTML = '';

    const prevBtn = document.createElement('button');
    prevBtn.className = 'pagination-btn';
    prevBtn.innerHTML = '&laquo; Prev';
    prevBtn.disabled = (page <= 1);
    prevBtn.addEventListener('click', () => {
      if (page > 1) {
        fetchCentres(page - 1);
        window.scrollTo({ top: container.offsetTop - 100, behavior: 'smooth' });
      }
    });
    paginationContainer.appendChild(prevBtn);

    const maxButtons = 5;
    let startPage = Math.max(1, page - 2);
    let endPage = Math.min(totalPages, startPage + maxButtons - 1);

    if (endPage - startPage < maxButtons - 1) {
      startPage = Math.max(1, endPage - maxButtons + 1);
    }

    if (startPage > 1) {
      const firstBtn = createPageBtn(1, page);
      paginationContainer.appendChild(firstBtn);
      if (startPage > 2) {
        const dots = document.createElement('span');
        dots.textContent = '...';
        dots.style.padding = '0 0.25rem';
        dots.style.color = 'var(--text-light)';
        paginationContainer.appendChild(dots);
      }
    }

    for (let p = startPage; p <= endPage; p++) {
      const pageBtn = createPageBtn(p, page);
      paginationContainer.appendChild(pageBtn);
    }

    if (endPage < totalPages) {
      if (endPage < totalPages - 1) {
        const dots = document.createElement('span');
        dots.textContent = '...';
        dots.style.padding = '0 0.25rem';
        dots.style.color = 'var(--text-light)';
        paginationContainer.appendChild(dots);
      }
      const lastBtn = createPageBtn(totalPages, page);
      paginationContainer.appendChild(lastBtn);
    }

    const nextBtn = document.createElement('button');
    nextBtn.className = 'pagination-btn';
    nextBtn.innerHTML = 'Next &raquo;';
    nextBtn.disabled = (page >= totalPages);
    nextBtn.addEventListener('click', () => {
      if (page < totalPages) {
        fetchCentres(page + 1);
        window.scrollTo({ top: container.offsetTop - 100, behavior: 'smooth' });
      }
    });
    paginationContainer.appendChild(nextBtn);
  }

  function createPageBtn(p, activePage) {
    const btn = document.createElement('button');
    btn.className = `pagination-btn ${p === activePage ? 'active' : ''}`;
    btn.textContent = p;
    btn.addEventListener('click', () => {
      if (p !== activePage) {
        fetchCentres(p);
        window.scrollTo({ top: container.offsetTop - 100, behavior: 'smooth' });
      }
    });
    return btn;
  }

  // --------------------------------------------------------------------------
  // 7. Active Filter Pills & Reset
  // --------------------------------------------------------------------------
  function updateActiveFilterPills(state, city, deviceId, keyword) {
    if (!activeFiltersEl) return;
    activeFiltersEl.innerHTML = '';

    const pills = [];
    if (state) pills.push({ type: 'state', label: `State: ${state}` });
    if (city) pills.push({ type: 'city', label: `City: ${city}` });
    if (deviceId && deviceSelect) {
      const selectedText = deviceSelect.options[deviceSelect.selectedIndex]?.text || `Device ID: ${deviceId}`;
      pills.push({ type: 'device', label: selectedText });
    }
    if (keyword) pills.push({ type: 'search', label: `Keyword: "${keyword}"` });

    if (pills.length > 0) {
      pills.forEach(p => {
        const pill = document.createElement('span');
        pill.className = 'filter-pill';
        pill.innerHTML = `
          ${escapeHtml(p.label)}
          <button type="button" aria-label="Remove filter">&times;</button>
        `;
        pill.querySelector('button').addEventListener('click', () => {
          if (p.type === 'state') {
            stateSelect.value = '';
            citySelect.innerHTML = '<option value="">All Cities</option>';
          }
          if (p.type === 'city') citySelect.value = '';
          if (p.type === 'device') deviceSelect.value = '';
          if (p.type === 'search' && searchInput) searchInput.value = '';
          fetchCentres(1);
        });
        activeFiltersEl.appendChild(pill);
      });
    }
  }

  function resetFilters() {
    if (stateSelect) stateSelect.value = '';
    if (citySelect) citySelect.innerHTML = '<option value="">All Cities</option>';
    if (deviceSelect) deviceSelect.value = '';
    if (searchInput) searchInput.value = '';

    exitNearestMode(true);
    if (facilityLayerGroup && facilityLayerGroup.getLayers().length > 0 && map) {
      map.fitBounds(facilityLayerGroup.getBounds().pad(0.12));
    }
    showToast('Search filters and map view reset.', 'info');
  }

  function showErrorState(msg) {
    container.innerHTML = `
      <div class="empty-state">
        <svg fill="none" stroke="#ef4444" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-3L13.732 4c-.77-1.333-2.694-1.333-3.464 0L3.34 16c-.77 1.333.192 3 1.732 3z"></path>
        </svg>
        <h3>Connection Error</h3>
        <p>${escapeHtml(msg)}</p>
        <button type="button" class="btn btn-outline btn-sm" id="error-retry-btn">Retry Request</button>
      </div>
    `;
    const retryBtn = document.getElementById('error-retry-btn');
    if (retryBtn) retryBtn.addEventListener('click', () => fetchCentres(1));
  }

  // Fallback demo city selector when GPS is denied or unavailable
  function showFallbackLocationPrompt() {
    const testCities = [
      { name: 'Delhi NCR (Connaught Place)', lat: 28.6315, lng: 77.2167 },
      { name: 'Bengaluru (MG Road)', lat: 12.9716, lng: 77.5946 },
      { name: 'Mumbai (Bandra West)', lat: 19.0657, lng: 72.8340 }
    ];

    const promptHtml = `
      <div style="background: #eff6ff; border: 1px solid #bfdbfe; border-radius: var(--radius-md); padding: 0.75rem 1rem; margin-top: 1rem; font-size: 0.85rem; color: #1e40af;">
        <strong>Simulate Location:</strong> Browser GPS was not accessed. Click a sample city to test nearest proximity:
        <div style="display: flex; gap: 0.5rem; margin-top: 0.5rem; flex-wrap: wrap;">
          ${testCities.map(c => `
            <button type="button" class="btn btn-sm btn-outline test-loc-btn" data-lat="${c.lat}" data-lng="${c.lng}" style="background: #ffffff; padding: 0.2rem 0.6rem; font-size: 0.75rem;">
              📍 ${c.name}
            </button>
          `).join('')}
        </div>
      </div>
    `;

    // Append fallback chip container if not already present
    let fallbackBox = document.getElementById('fallback-location-box');
    if (!fallbackBox) {
      fallbackBox = document.createElement('div');
      fallbackBox.id = 'fallback-location-box';
      const searchCard = document.querySelector('.search-filter-card');
      if (searchCard) searchCard.appendChild(fallbackBox);
    }
    fallbackBox.innerHTML = promptHtml;

    document.querySelectorAll('.test-loc-btn').forEach(btn => {
      btn.addEventListener('click', () => {
        const lat = parseFloat(btn.getAttribute('data-lat'));
        const lng = parseFloat(btn.getAttribute('data-lng'));
        applyUserLocation(lat, lng, btn.textContent.trim());
      });
    });
  }

  function escapeHtml(str) {
    if (!str) return '';
    return String(str)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#039;');
  }

  // --------------------------------------------------------------------------
  // 8. Event Bindings
  // --------------------------------------------------------------------------
  if (searchBtn) {
    searchBtn.addEventListener('click', (e) => {
      e.preventDefault();
      exitNearestMode(false);
      fetchCentres(1);
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', (e) => {
      e.preventDefault();
      resetFilters();
    });
  }

  if (locationBtn) {
    locationBtn.addEventListener('click', (e) => {
      e.preventDefault();
      handleUseLocation();
    });
  }

  if (clearLocationBtn) {
    clearLocationBtn.addEventListener('click', (e) => {
      e.preventDefault();
      exitNearestMode(true);
      showToast('Returned to full national directory view.', 'info');
    });
  }
}

/* ==========================================================================
   Frontend Form Validation (login.html & register.html)
   ========================================================================== */
function initAuthValidation() {
  const toggleButtons = document.querySelectorAll('.password-toggle-btn');
  toggleButtons.forEach(btn => {
    btn.addEventListener('click', () => {
      const targetId = btn.getAttribute('data-target');
      const input = document.getElementById(targetId);
      if (input) {
        if (input.type === 'password') {
          input.type = 'text';
          btn.innerHTML = `
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13.875 18.825A10.05 10.05 0 0112 19c-4.478 0-8.268-2.943-9.543-7a9.97 9.97 0 011.563-3.029m5.858.908a3 3 0 114.243 4.243M9.878 9.878l4.242 4.242M9.88 9.88l-3.29-3.29m7.532 7.532l3.29 3.29M3 3l18 18"></path>
            </svg>
          `;
          btn.setAttribute('aria-label', 'Hide password');
        } else {
          input.type = 'password';
          btn.innerHTML = `
            <svg width="20" height="20" fill="none" stroke="currentColor" viewBox="0 0 24 24">
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M15 12a3 3 0 11-6 0 3 3 0 016 0z"></path>
              <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M2.458 12C3.732 7.943 7.523 5 12 5c4.478 0 8.268 2.943 9.542 7-1.274 4.057-5.064 7-9.542 7-4.477 0-8.268-2.943-9.542-7z"></path>
            </svg>
          `;
          btn.setAttribute('aria-label', 'Show password');
        }
      }
    });
  });

  const registerForm = document.getElementById('register-form');
  if (registerForm) {
    registerForm.addEventListener('submit', (e) => {
      const name = document.getElementById('reg-name');
      const email = document.getElementById('reg-email');
      const pass = document.getElementById('reg-password');
      const confirm = document.getElementById('reg-confirm');
      const terms = document.getElementById('reg-terms');

      let isValid = true;

      if (name && name.value.trim().length < 2) {
        showFieldValidation(name, false, 'Please enter your full name (at least 2 characters)');
        isValid = false;
      } else if (name) {
        showFieldValidation(name, true);
      }

      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (email && !emailRegex.test(email.value.trim())) {
        showFieldValidation(email, false, 'Please enter a valid email address');
        isValid = false;
      } else if (email) {
        showFieldValidation(email, true);
      }

      if (pass && pass.value.length < 8) {
        showFieldValidation(pass, false, 'Password must be at least 8 characters');
        isValid = false;
      } else if (pass) {
        showFieldValidation(pass, true);
      }

      if (confirm && confirm.value !== (pass ? pass.value : '')) {
        showFieldValidation(confirm, false, 'Passwords do not match');
        isValid = false;
      } else if (confirm) {
        showFieldValidation(confirm, true);
      }

      if (terms && !terms.checked) {
        showToast('Please accept the Terms of Service and Privacy Policy', 'error');
        isValid = false;
      }

      if (!isValid) {
        e.preventDefault();
      }
    });
  }

  const loginForm = document.getElementById('login-form');
  if (loginForm) {
    loginForm.addEventListener('submit', (e) => {
      const email = document.getElementById('login-email');
      const pass = document.getElementById('login-password');

      let isValid = true;
      const emailRegex = /^[^\s@]+@[^\s@]+\.[^\s@]+$/;
      if (email && !emailRegex.test(email.value.trim())) {
        showFieldValidation(email, false, 'Please enter a valid email address');
        isValid = false;
      } else if (email) {
        showFieldValidation(email, true);
      }

      if (pass && pass.value.length === 0) {
        showFieldValidation(pass, false, 'Password is required');
        isValid = false;
      } else if (pass) {
        showFieldValidation(pass, true);
      }

      if (!isValid) {
        e.preventDefault();
      }
    });
  }
}

function showFieldValidation(input, isValid, errorMsg = '') {
  const group = input.closest('.form-group');
  if (!group) return;

  let errorEl = group.querySelector('.form-error');

  if (!isValid) {
    input.classList.add('is-invalid');
    if (!errorEl) {
      errorEl = document.createElement('div');
      errorEl.className = 'form-error';
      group.appendChild(errorEl);
    }
    errorEl.textContent = errorMsg;
  } else {
    input.classList.remove('is-invalid');
    if (errorEl) {
      errorEl.remove();
    }
  }
}

/* ==========================================================================
   Micro-Interactions & Notifications
   ========================================================================== */
function showToast(message, type = 'info') {
  let toastContainer = document.querySelector('.toast-container');
  if (!toastContainer) {
    toastContainer = document.createElement('div');
    toastContainer.className = 'toast-container';
    document.body.appendChild(toastContainer);
  }

  const toast = document.createElement('div');
  toast.className = `toast toast-${type}`;

  const iconSvg = type === 'success'
    ? `<svg width="20" height="20" fill="none" stroke="#10b981" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M5 13l4 4L19 7"></path></svg>`
    : (type === 'error'
      ? `<svg width="20" height="20" fill="none" stroke="#ef4444" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M6 18L18 6M6 6l12 12"></path></svg>`
      : `<svg width="20" height="20" fill="none" stroke="#10b981" viewBox="0 0 24 24"><path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M13 16h-1v-4h-1m1-4h.01M21 12a9 9 0 11-18 0 9 9 0 0118 0z"></path></svg>`);

  toast.innerHTML = `
    ${iconSvg}
    <span>${message}</span>
  `;

  toastContainer.appendChild(toast);

  setTimeout(() => {
    toast.classList.add('toast-fade-out');
    setTimeout(() => toast.remove(), 300);
  }, 4000);
}
