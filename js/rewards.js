/**
 * EcoLocate - Rewards Calculator (Phase 6)
 * Calculates illustrative EcoReward points using MySQL devices table.
 * Supports backend calculation, quantity validation, and personal rewards history logging.
 */

document.addEventListener('DOMContentLoaded', () => {
  initRewardsCalculator();
});

function initRewardsCalculator() {
  const deviceSelect = document.getElementById('device-select');
  const quantityInput = document.getElementById('quantity-input');
  const btnMinus = document.getElementById('qty-minus');
  const btnPlus = document.getElementById('qty-plus');
  const calculateBtn = document.getElementById('calculate-rewards-btn');
  const resetBtn = document.getElementById('reset-calculator-btn');
  const saveBtn = document.getElementById('save-reward-btn');
  const clearHistoryBtn = document.getElementById('clear-history-btn');

  const pointsDisplay = document.getElementById('calculated-points');
  const summaryText = document.getElementById('calculation-summary-text');
  const co2Display = document.getElementById('calculated-co2');
  const materialsDisplay = document.getElementById('calculated-materials');
  const quantityError = document.getElementById('quantity-error');
  const historyTbody = document.getElementById('history-tbody');
  const totalHistoryPoints = document.getElementById('total-history-points');

  if (!deviceSelect || !calculateBtn) return; // Not on rewards page

  // If options were not loaded from Jinja2 template, fetch dynamically from MySQL API
  if (deviceSelect.options.length === 0) {
    fetch('/api/devices')
      .then(res => res.json())
      .then(data => {
        if (data.success && data.devices) {
          deviceSelect.innerHTML = '';
          data.devices.forEach(d => {
            const opt = document.createElement('option');
            opt.value = d.id;
            opt.setAttribute('data-points', d.points_per_unit);
            opt.textContent = `${d.device_name} (${d.points_per_unit} points/unit)`;
            deviceSelect.appendChild(opt);
          });
          calculatePoints();
        }
      })
      .catch(err => console.error('Error fetching devices:', err));
  }

  // Stepper controls
  if (btnMinus) {
    btnMinus.addEventListener('click', () => {
      let val = parseInt(quantityInput.value, 10) || 1;
      if (val > 1) {
        quantityInput.value = val - 1;
        validateQuantity();
        calculatePoints();
      }
    });
  }

  if (btnPlus) {
    btnPlus.addEventListener('click', () => {
      let val = parseInt(quantityInput.value, 10) || 1;
      if (val < 1000) {
        quantityInput.value = val + 1;
        validateQuantity();
        calculatePoints();
      }
    });
  }

  if (quantityInput) {
    quantityInput.addEventListener('input', () => {
      validateQuantity();
      calculatePoints();
    });
    quantityInput.addEventListener('change', () => {
      validateQuantity();
      calculatePoints();
    });
  }

  if (deviceSelect) {
    deviceSelect.addEventListener('change', () => {
      calculatePoints();
    });
  }

  if (calculateBtn) {
    calculateBtn.addEventListener('click', (e) => {
      e.preventDefault();
      calculatePoints(true);
    });
  }

  if (resetBtn) {
    resetBtn.addEventListener('click', (e) => {
      e.preventDefault();
      resetCalculator();
    });
  }

  if (saveBtn) {
    saveBtn.addEventListener('click', (e) => {
      e.preventDefault();
      saveCalculation();
    });
  }

  if (clearHistoryBtn) {
    clearHistoryBtn.addEventListener('click', (e) => {
      e.preventDefault();
      clearHistory();
    });
  }

  // Initial calculation on load
  calculatePoints();

  // --------------------------------------------------------------------------
  // Core Calculation Function
  // --------------------------------------------------------------------------
  function calculatePoints(fetchBackend = false) {
    if (!validateQuantity()) return;

    const selectedOption = deviceSelect.options[deviceSelect.selectedIndex];
    if (!selectedOption) return;

    const deviceId = selectedOption.value;
    const pointsPerUnit = parseInt(selectedOption.getAttribute('data-points'), 10) || 10;
    const quantity = parseInt(quantityInput.value, 10) || 1;

    // Formula: Total Points = Quantity * Points Per Unit
    const totalPoints = quantity * pointsPerUnit;

    // Update displays immediately on frontend
    if (pointsDisplay) pointsDisplay.textContent = totalPoints.toLocaleString();
    if (summaryText) {
      summaryText.textContent = `${quantity} Unit(s) × ${pointsPerUnit} points/unit`;
    }
    if (co2Display) {
      co2Display.textContent = `${(totalPoints * 0.12).toFixed(1)} kg`;
    }
    if (materialsDisplay) {
      materialsDisplay.textContent = `${(totalPoints * 0.25).toFixed(1)} g`;
    }

    // Call backend API endpoint to verify backend validation and calculation
    if (fetchBackend) {
      fetch('/api/rewards/calculate', {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' },
        body: JSON.stringify({
          device_id: deviceId,
          quantity: quantity
        })
      })
      .then(res => res.json())
      .then(data => {
        if (data.success) {
          if (pointsDisplay) pointsDisplay.textContent = data.total_points.toLocaleString();
          if (summaryText) {
            summaryText.textContent = `${data.quantity} Unit(s) × ${data.points_per_unit} points/unit`;
          }
          if (window.showToast) {
            window.showToast(`Estimated: ${data.total_points} EcoPoints (${data.quantity} × ${data.device_name})`, 'success');
          }
        } else {
          showQuantityError(data.error || 'Calculation failed.');
        }
      })
      .catch(err => {
        console.error('Backend calculation error:', err);
      });
    }
  }

  function validateQuantity() {
    const rawVal = quantityInput.value.trim();
    const val = parseInt(rawVal, 10);

    if (!rawVal || isNaN(val) || val <= 0) {
      showQuantityError('Quantity must be a positive number greater than 0.');
      return false;
    }

    if (val > 1000) {
      showQuantityError('Maximum quantity is 1,000 units.');
      return false;
    }

    hideQuantityError();
    return true;
  }

  function showQuantityError(msg) {
    if (quantityError) {
      quantityError.textContent = msg;
      quantityError.style.display = 'block';
    }
    quantityInput.classList.add('is-invalid');
  }

  function hideQuantityError() {
    if (quantityError) {
      quantityError.textContent = '';
      quantityError.style.display = 'none';
    }
    quantityInput.classList.remove('is-invalid');
  }

  function resetCalculator() {
    if (deviceSelect) {
      deviceSelect.selectedIndex = 0;
    }
    if (quantityInput) {
      quantityInput.value = 1;
    }
    hideQuantityError();
    calculatePoints();
    if (window.showToast) {
      window.showToast('Calculator parameters reset to defaults.', 'info');
    }
  }

  // --------------------------------------------------------------------------
  // Save Calculation to History
  // --------------------------------------------------------------------------
  function saveCalculation() {
    if (!validateQuantity()) return;

    const selectedOption = deviceSelect.options[deviceSelect.selectedIndex];
    if (!selectedOption) return;

    const deviceId = selectedOption.value;
    const quantity = parseInt(quantityInput.value, 10) || 1;

    saveBtn.disabled = true;
    saveBtn.innerHTML = 'Saving to History...';

    fetch('/api/rewards/save', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        device_id: deviceId,
        quantity: quantity
      })
    })
    .then(res => res.json())
    .then(data => {
      saveBtn.disabled = false;
      saveBtn.innerHTML = `
        <svg width="16" height="16" fill="none" stroke="currentColor" viewBox="0 0 24 24">
          <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M8 7H5a2 2 0 00-2 2v9a2 2 0 002 2h14a2 2 0 002-2V9a2 2 0 00-2-2h-3m-1 4l-3 3m0 0l-3-3m3 3V4"></path>
        </svg>
        Save Calculation to My History
      `;

      if (data.success) {
        if (window.showToast) {
          window.showToast(data.message, 'success');
        }
        refreshHistoryTable();
      } else {
        if (window.showToast) {
          window.showToast(data.error || 'Failed to save calculation', 'error');
        }
      }
    })
    .catch(err => {
      saveBtn.disabled = false;
      saveBtn.innerHTML = 'Save Calculation to My History';
      console.error('Save error:', err);
      if (window.showToast) {
        window.showToast('Network error while saving calculation', 'error');
      }
    });
  }

  function refreshHistoryTable() {
    fetch('/api/rewards/history')
      .then(res => res.json())
      .then(data => {
        if (data.success && historyTbody) {
          historyTbody.innerHTML = '';
          if (data.history.length === 0) {
            historyTbody.innerHTML = `
              <tr id="empty-history-row">
                <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                  No calculations saved yet. Select your devices above and click "Save Calculation to My History".
                </td>
              </tr>
            `;
          } else {
            data.history.forEach(item => {
              const tr = document.createElement('tr');
              const dateStr = item.created_at ? new Date(item.created_at).toLocaleDateString(undefined, {
                day: '2-digit', month: 'short', year: 'numeric', hour: '2-digit', minute: '2-digit'
              }) : 'Just now';

              tr.innerHTML = `
                <td><strong>${escapeHtml(item.device_name)}</strong></td>
                <td>${item.quantity} unit(s)</td>
                <td>${item.points_per_unit} pts</td>
                <td><span class="badge-points">+${item.total_points} pts</span></td>
                <td style="color: var(--text-light); font-size: 0.8rem;">${dateStr}</td>
              `;
              historyTbody.appendChild(tr);
            });
          }

          if (totalHistoryPoints) {
            totalHistoryPoints.textContent = `${data.total_points} pts`;
          }
        }
      })
      .catch(err => console.error('Error refreshing history:', err));
  }

  function clearHistory() {
    if (!confirm('Are you sure you want to clear your rewards calculation history?')) return;

    fetch('/api/rewards/history/clear', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' }
    })
    .then(res => res.json())
    .then(data => {
      if (data.success) {
        if (historyTbody) {
          historyTbody.innerHTML = `
            <tr id="empty-history-row">
              <td colspan="5" style="text-align: center; color: var(--text-muted); padding: 2rem;">
                No calculations saved yet. Select your devices above and click "Save Calculation to My History".
              </td>
            </tr>
          `;
        }
        if (totalHistoryPoints) totalHistoryPoints.textContent = '0 pts';
        if (window.showToast) window.showToast('Calculation history cleared.', 'info');
      }
    })
    .catch(err => console.error('Error clearing history:', err));
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
}
