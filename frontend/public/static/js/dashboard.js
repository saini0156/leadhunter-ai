// LeadHunter AI — Dashboard Client Script

let allLeads = [];
let isDryRun = true;

document.addEventListener("DOMContentLoaded", () => {
    // Restore previous inputs or set defaults
    const savedCity = localStorage.getItem("leadhunter_city") || "Surat";
    const savedCategory = localStorage.getItem("leadhunter_category") || "Dentist";
    const savedService = localStorage.getItem("leadhunter_service") || "Digital Marketing";
    const savedCountry = localStorage.getItem("leadhunter_country") || "Canada";
    const savedLimit = localStorage.getItem("leadhunter_limit") || "10";

    const cityInput = document.getElementById("targetCity");
    const catInput = document.getElementById("targetCategory");
    const countryInput = document.getElementById("targetCountry");
    const limitInput = document.getElementById("targetLimit");

    if (cityInput) {
        cityInput.value = savedCity;
        cityInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                runStage("all");
            }
        });
    }

    if (countryInput) {
        const legacyCountryMap = { "UAE": "United Arab Emirates", "USA": "United States", "UK": "United Kingdom" };
        countryInput.value = legacyCountryMap[savedCountry] || savedCountry;
    }

    const serviceInput = document.getElementById("targetService");
    if (serviceInput) serviceInput.value = savedService;

    if (catInput) {
        catInput.value = savedCategory;
        catInput.addEventListener("keydown", (e) => {
            if (e.key === "Enter") {
                e.preventDefault();
                runStage("all");
            }
        });
    }

    if (limitInput) {
        limitInput.value = savedLimit;
    }

    refreshAllData();
    setInterval(fetchLiveLogs, 5000);
});

function handleParamChange() {
    const city = getCity();
    const category = getCategory();
    const service = getService();
    const country = getCountry();
    const limit = getLimit();
    localStorage.setItem("leadhunter_city", city);
    localStorage.setItem("leadhunter_category", category);
    localStorage.setItem("leadhunter_service", service);
    localStorage.setItem("leadhunter_country", country);
    localStorage.setItem("leadhunter_limit", limit);
    refreshAllData();
}

function getCity() {
    const el = document.getElementById("targetCity");
    return el && el.value.trim() ? el.value.trim() : "Surat";
}

function getCategory() {
    const el = document.getElementById("targetCategory");
    return el && el.value.trim() ? el.value.trim() : "Dentist";
}

function getService() {
    const el = document.getElementById("targetService");
    return el && el.value.trim() ? el.value.trim() : "Digital Marketing";
}

function getCountry() {
    const el = document.getElementById("targetCountry");
    return el && el.value.trim() ? el.value.trim() : "Canada";
}

function getLimit() {
    const el = document.getElementById("targetLimit");
    return el && el.value ? parseInt(el.value, 10) : 10;
}

// Tab Switching
function switchTab(tabId) {
    // Hide all tab panes
    document.querySelectorAll(".tab-pane").forEach(el => {
        el.classList.remove("active");
        el.style.display = "none";
    });
    
    // Deactivate all nav items
    document.querySelectorAll(".nav-item").forEach(el => el.classList.remove("active"));

    // Activate selected tab pane
    const targetTab = document.getElementById(`tab-${tabId}`);
    if (targetTab) {
        targetTab.classList.add("active");
        targetTab.style.display = "block";
    }

    // Activate corresponding sidebar nav item
    document.querySelectorAll(".nav-item").forEach(btn => {
        if (btn.getAttribute("onclick")?.includes(tabId)) {
            btn.classList.add("active");
        }
    });

    // Scroll main content to top
    const mainContent = document.querySelector(".main-content");
    if (mainContent) mainContent.scrollTop = 0;

    // Load data for specific tab
    if (tabId === "approval") loadApprovalQueue();
    if (tabId === "leads") loadLeadsTable();
    if (tabId === "logs") fetchLiveLogs();
}

// Toast Notifications
function showToast(message, type = "info") {
    let container = document.getElementById("toastContainer");
    if (!container) {
        container = document.createElement("div");
        container.id = "toastContainer";
        container.style.position = "fixed";
        container.style.bottom = "24px";
        container.style.right = "24px";
        container.style.zIndex = "9999";
        container.style.display = "flex";
        container.style.flexDirection = "column";
        container.style.gap = "8px";
        document.body.appendChild(container);
    }
    const toast = document.createElement("div");
    toast.className = `toast toast-${type}`;
    toast.style.background = type === "success" ? "#065f46" : type === "error" ? "#991b1b" : "#1e293b";
    toast.style.color = "#ffffff";
    toast.style.padding = "12px 18px";
    toast.style.borderRadius = "10px";
    toast.style.fontSize = "0.88rem";
    toast.style.fontWeight = "600";
    toast.style.boxShadow = "0 10px 25px rgba(0,0,0,0.5)";
    toast.style.display = "flex";
    toast.style.alignItems = "center";
    toast.style.gap = "10px";
    toast.style.transition = "all 0.3s ease";

    const icon = type === "success" ? "✅" : type === "error" ? "❌" : "⚡";
    toast.innerHTML = `<span>${icon}</span> <span>${message}</span>`;
    container.appendChild(toast);

    setTimeout(() => {
        toast.style.opacity = "0";
        setTimeout(() => toast.remove(), 300);
    }, 4000);
}

// Refresh Global Data
async function refreshAllData() {
    const city = getCity();
    const displayCityEl = document.getElementById("displayCity");
    if (displayCityEl) displayCityEl.innerText = city;
    await Promise.all([fetchStats(), loadLeadsTable(), loadApprovalQueue(), fetchLiveLogs()]);
}

// Fetch Pipeline Stats
async function fetchStats() {
    try {
        const city = getCity();
        const res = await fetch(`/api/stats?city=${encodeURIComponent(city)}`);
        const data = await res.json();
        if (data.status === "ok") {
            const s = data.stats;
            const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.innerText = val; };
            setVal("statDiscovered", s.discovered || 0);
            setVal("statHot", s.hot || 0);
            setVal("statWarm", s.warm || 0);
            setVal("statDemoReady", s.demo_ready || 0);
            setVal("statPendingApproval", s.pending_approval || 0);
            setVal("statSent", (s.sent || 0) + (s.dry_run_sent || 0));

            // Update badge on sidebar
            setVal("pendingApprovalBadge", s.pending_approval || 0);
        }
    } catch (err) {
        console.error("Error fetching stats:", err);
    }
}

// Execute Pipeline Stage
async function runStage(stage) {
    const city = getCity();
    const category = getCategory();
    const service = getService();
    const limit = getLimit();
    showToast(`Executing Stage: ${stage.toUpperCase()} (${limit} leads) for ${category} in ${city}...`, "info");

    const btn = document.getElementById("btnRunFullPipeline");
    if (btn && stage === "all") {
        btn.innerHTML = `<span class="btn-icon">⏳</span> Executing (${limit} Leads)...`;
        btn.disabled = true;
    }

    try {
        const res = await fetch(`/api/pipeline/run-stage`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ stage, city, category, country: getCountry(), service, limit })
        });
        const result = await res.json();
        if (result.status === "ok") {
            showToast(result.message || `Stage [${stage.toUpperCase()}] completed successfully!`, "success");
            await refreshAllData();
            if (stage === "all" || stage === "approval") {
                setTimeout(() => switchTab("approval"), 500);
            }
        } else {
            showToast(`Stage [${stage.toUpperCase()}] error: ${result.error || result.message}`, "error");
        }
    } catch (err) {
        showToast(`Failed to execute stage ${stage}: ${err}`, "error");
    } finally {
        if (btn && stage === "all") {
            btn.innerHTML = `<span class="btn-icon">🚀</span> Run Full Pipeline`;
            btn.disabled = false;
        }
    }
}

// Toggle Dry Run Mode
async function toggleDryRun() {
    try {
        const res = await fetch(`/api/config/dry-run`, { method: "POST" });
        const data = await res.json();
        isDryRun = data.dry_run;

        const pill = document.getElementById("dryRunToggle");
        if (isDryRun) {
            pill.className = "mode-pill dry-run-active";
            pill.innerHTML = "🛡️ DRY RUN ACTIVE";
            showToast("Outreach Safety Mode: DRY_RUN enabled", "info");
        } else {
            pill.className = "mode-pill live-active";
            pill.innerHTML = "🚨 LIVE MODE ACTIVE";
            showToast("WARNING: Outreach Live Sending Enabled!", "error");
        }
    } catch (err) {
        console.error("Error toggling dry run:", err);
    }
}

// Load Approval Queue
async function loadApprovalQueue() {
    const container = document.getElementById("approvalQueueContainer");
    try {
        const city = getCity();
        const res = await fetch(`/api/approvals?city=${encodeURIComponent(city)}`);
        const data = await res.json();
        const leads = data.leads || [];

        if (leads.length === 0) {
            container.innerHTML = `<div class="empty-state">✅ All caught up! No leads currently pending human approval.</div>`;
            return;
        }

        container.innerHTML = leads.map(l => {
            const leadName = l.name || l.business_name || 'Prospect';
            const leadId = l.lead_id || l.id;
            const demoUrl = l.demo_url || '';
            return `
            <div class="approval-card">
                <div class="approval-header">
                    <div>
                        <div class="approval-name">${leadName}</div>
                        <div class="approval-meta">📍 ${l.city || 'Vadodara'} • 🏷️ ${l.category || 'Local Business'} • 📞 ${l.phone || 'No phone'}</div>
                    </div>
                    <span class="badge ${l.lead_tier === 'HOT' ? 'badge-hot' : 'badge-warm'}">${l.lead_tier || 'PROSPECT'} (${l.lead_score || l.score || 0} pts)</span>
                </div>

                <div class="msg-preview-box">
                    <div class="msg-preview-title">📧 Cold Email Pitch</div>
                    <div style="font-weight: 600; margin-bottom: 4px;">${l.email_subject || 'Website Proposal'}</div>
                    <div style="color: #94a3b8; font-size: 0.82rem; white-space: pre-line;">${(l.email_message || 'N/A').slice(0, 160)}...</div>
                </div>

                <div class="msg-preview-box">
                    <div class="msg-preview-title">📱 WhatsApp Copy</div>
                    <div style="color: #94a3b8; font-size: 0.82rem; white-space: pre-line;">${(l.whatsapp_message || 'N/A').slice(0, 140)}...</div>
                </div>

                <div class="flex items-center justify-between" style="font-size: 0.82rem;">
                    <span>Demo Preview:</span>
                    ${demoUrl ? `<button class="btn btn-outline btn-sm" onclick="openDemoModal('${demoUrl}', '${escapeQuotes(leadName)}')">🖥️ View Demo Page</button>` : `<span style="color: #64748b;">Not Generated</span>`}
                </div>

                <div class="approval-actions">
                    <button class="btn btn-success" onclick="reviewLead(${leadId}, 'APPROVE')">✅ Approve</button>
                    <button class="btn btn-danger" onclick="reviewLead(${leadId}, 'REJECT')">❌ Reject</button>
                    ${l.phone ? `<button class="btn btn-outline btn-sm" onclick="openWhatsAppDirect('${l.phone}', '${escapeQuotes(l.whatsapp_message || '')}', '${demoUrl}')" style="margin-left: auto; border-color: #22c55e; color: #22c55e;">💬 Open in WhatsApp</button>` : ''}
                </div>
            </div>
            `;
        }).join("");

    } catch (err) {
        container.innerHTML = `<div class="empty-state">Error loading approval queue: ${err}</div>`;
    }
}

// 1-Click Review Lead
async function reviewLead(leadId, decision) {
    try {
        const res = await fetch(`/api/approvals/${leadId}`, {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ decision })
        });
        const result = await res.json();
        if (result.status === "ok") {
            const emailStatus = result.email_result?.status;
            if (emailStatus === "SENT") {
                showToast(`✅ Lead #${leadId} Approved & Cold Email Dispatched via Gmail!`, "success");
            } else if (emailStatus === "DRY_RUN_SENT") {
                showToast(`🛡️ Lead #${leadId} Approved (Outreach Simulated in DRY RUN Mode)`, "info");
            } else {
                showToast(`Lead #${leadId} marked ${decision}D!`, "success");
            }
            await loadApprovalQueue();
            await fetchStats();
        }
    } catch (err) {
        showToast(`Failed to update approval: ${err}`, "error");
    }
}

// Approve All Pending
async function approveAllPending() {
    try {
        const city = getCity();
        const res = await fetch(`/api/approvals/approve-all?city=${encodeURIComponent(city)}`, { method: "POST" });
        const result = await res.json();
        showToast(`Approved ${result.count || 0} pending leads!`, "success");
        await loadApprovalQueue();
        await fetchStats();
    } catch (err) {
        showToast(`Error: ${err}`, "error");
    }
}

// Load Leads Explorer Table
async function loadLeadsTable() {
    try {
        const res = await fetch(`/api/leads?limit=1000`);
        const data = await res.json();
        allLeads = data.leads || [];
        populateFilterDropdowns(allLeads);
        filterLeadsTable();
        renderHotProspects(allLeads);
    } catch (err) {
        console.error("Error loading leads table:", err);
    }
}

function toTitleCase(str) {
    if (!str) return "";
    return str.trim().toLowerCase().replace(/\b\w/g, char => char.toUpperCase());
}

function populateFilterDropdowns(leads) {
    const citySelect = document.getElementById("filterCity");
    const catSelect = document.getElementById("filterCategory");
    if (!citySelect || !catSelect) return;

    const currentCity = (citySelect.value || "").toLowerCase().trim();
    const currentCat = (catSelect.value || "").toLowerCase().trim();

    // Case-insensitive unique maps to prevent duplicate 'MOHALI' vs 'Mohali'
    const citiesMap = new Map();
    const categoriesMap = new Map();

    leads.forEach(l => {
        if (l.city && l.city.trim()) {
            const raw = l.city.trim();
            const key = raw.toLowerCase();
            if (!citiesMap.has(key)) {
                citiesMap.set(key, toTitleCase(raw));
            }
        }
        if (l.category && l.category.trim()) {
            const raw = l.category.trim();
            const key = raw.toLowerCase();
            if (!categoriesMap.has(key)) {
                categoriesMap.set(key, toTitleCase(raw));
            }
        }
    });

    const uniqueCities = Array.from(citiesMap.values()).sort();
    const uniqueCategories = Array.from(categoriesMap.values()).sort();

    citySelect.innerHTML = `<option value="">All Cities (${uniqueCities.length})</option>` + 
        uniqueCities.map(c => `<option value="${c}" ${c.toLowerCase() === currentCity ? 'selected' : ''}>📍 ${c}</option>`).join("");

    catSelect.innerHTML = `<option value="">All Categories (${uniqueCategories.length})</option>` + 
        uniqueCategories.map(c => `<option value="${c}" ${c.toLowerCase() === currentCat ? 'selected' : ''}>🏷️ ${c}</option>`).join("");
}

function renderHotProspects(leads) {
    const list = document.getElementById("hotProspectsList");
    if (!list) return;
    const hotLeads = leads.filter(l => l.lead_tier === "HOT").slice(0, 4);

    if (hotLeads.length === 0) {
        list.innerHTML = `<div class="empty-state">No HOT leads detected yet. Run Scoring stage!</div>`;
        return;
    }

    list.innerHTML = hotLeads.map(l => {
        const demoLink = l.demo_url ? (l.demo_url.includes('/preview/') ? ('/preview/' + l.demo_url.split('/preview/')[1]) : l.demo_url) : ('/preview/' + l.id);
        return `
        <div class="compact-lead-card" style="cursor: pointer;" onclick="openDemoModal('${demoLink}', '${escapeQuotes(l.name)}')">
            <div>
                <div class="compact-lead-title">${l.name}</div>
                <div class="compact-lead-meta">📍 ${l.city} • Website: ${l.website_status || 'Unchecked'}</div>
            </div>
            <div class="flex items-center gap-2">
                <span class="badge badge-hot">${l.score || 0} pts</span>
                <a href="${demoLink}" target="_blank" onclick="event.stopPropagation();" class="btn btn-outline btn-sm" style="color: #f97316; border-color: #f97316;">⚡ Demo →</a>
            </div>
        </div>
    `}).join("");
}

let selectedLeadIds = new Set();
let currentFilteredLeads = [];

function renderLeadsTable(leads) {
    currentFilteredLeads = leads;
    const tbody = document.getElementById("leadsTableBody");
    if (!tbody) return;
    if (leads.length === 0) {
        tbody.innerHTML = `<tr><td colspan="10" class="text-center" style="padding: 24px; color: #94a3b8;">No leads found matching current filter criteria.</td></tr>`;
        updateBulkActionsBar();
        return;
    }

    tbody.innerHTML = leads.map((l, index) => {
        const demoLink = l.demo_url ? (l.demo_url.includes('/preview/') ? ('/preview/' + l.demo_url.split('/preview/')[1]) : l.demo_url) : ('/preview/' + l.id);
        const isChecked = selectedLeadIds.has(l.id);
        return `
        <tr class="${isChecked ? 'row-selected' : ''}">
            <td style="text-align: center;">
                <input type="checkbox" class="table-checkbox lead-row-checkbox" value="${l.id}" ${isChecked ? 'checked' : ''} onchange="toggleLeadSelection(${l.id}, event)">
            </td>
            <td>
                <strong style="color: #f8fafc; font-size: 0.92rem;">#${index + 1}</strong>
                <div style="font-size: 0.72rem; color: #64748b;">ID: ${l.id}</div>
            </td>
            <td><strong>${l.name}</strong></td>
            <td>${l.category || '-'}</td>
            <td>📍 ${toTitleCase(l.city || '')}</td>
            <td><span class="badge badge-info">${l.website_status || 'PENDING'}</span></td>
            <td>
                ${l.lead_tier ? `<span class="badge ${l.lead_tier === 'HOT' ? 'badge-hot' : l.lead_tier === 'WARM' ? 'badge-warm' : 'badge-low'}">${l.lead_tier} (${l.score || 0})</span>` : '-'}
            </td>
            <td><span class="badge ${l.status === 'SENT' || l.status === 'DRY_RUN_SENT' ? 'badge-success' : 'badge-low'}">${l.status}</span></td>
            <td>
                <a href="${demoLink}" target="_blank" class="btn btn-outline btn-sm" style="color:#f97316; border-color:#f97316;">🖥️ Open Demo →</a>
            </td>
            <td>
                <div class="lead-actions-cell">
                    <button class="btn-action-view" onclick="openLeadModal(${l.id})" title="View Complete Profile">👁️ Details</button>
                    <button class="btn-action-edit" onclick="openEditLeadModal(${l.id})" title="Edit Lead">✏️ Edit</button>
                    <button class="btn-action-delete" onclick="deleteLead(${l.id}, '${escapeQuotes(l.name)}')" title="Delete Lead Permanently">🗑️</button>
                </div>
            </td>
        </tr>
    `}).join("");

    updateBulkActionsBar();
}

// Checkbox and Bulk Actions Management
function toggleLeadSelection(leadId, e) {
    if (e.target.checked) {
        selectedLeadIds.add(leadId);
    } else {
        selectedLeadIds.delete(leadId);
    }
    updateBulkActionsBar();
}

function toggleSelectAllLeads(e) {
    const isChecked = e.target.checked;
    if (isChecked) {
        currentFilteredLeads.forEach(l => selectedLeadIds.add(l.id));
    } else {
        currentFilteredLeads.forEach(l => selectedLeadIds.delete(l.id));
    }

    const rowCheckboxes = document.querySelectorAll(".lead-row-checkbox");
    rowCheckboxes.forEach(cb => {
        cb.checked = isChecked;
    });

    updateBulkActionsBar();
}

function updateBulkActionsBar() {
    const bar = document.getElementById("bulkActionsBar");
    const countEl = document.getElementById("selectedLeadsCount");
    const btnCountEl = document.getElementById("deleteSelectedBtnCount");
    const selectAllCb = document.getElementById("selectAllCheckbox");

    const count = selectedLeadIds.size;
    if (countEl) countEl.innerText = `${count} lead${count === 1 ? '' : 's'}`;
    if (btnCountEl) btnCountEl.innerText = count;

    if (bar) {
        bar.style.display = count > 0 ? "flex" : "none";
    }

    if (selectAllCb) {
        selectAllCb.checked = currentFilteredLeads.length > 0 && currentFilteredLeads.every(l => selectedLeadIds.has(l.id));
    }
}

function deselectAllLeads() {
    selectedLeadIds.clear();
    const rowCheckboxes = document.querySelectorAll(".lead-row-checkbox");
    rowCheckboxes.forEach(cb => cb.checked = false);
    const selectAllCb = document.getElementById("selectAllCheckbox");
    if (selectAllCb) selectAllCb.checked = false;
    updateBulkActionsBar();
}

// Bulk Delete Selected Leads
async function deleteSelectedLeads() {
    const ids = Array.from(selectedLeadIds);
    if (ids.length === 0) return;

    const confirmed = confirm(`Are you sure you want to permanently delete ${ids.length} selected lead(s)?\n\nThis will remove them from the database.`);
    if (!confirmed) return;

    try {
        const res = await fetch("/api/leads/bulk-delete", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify({ lead_ids: ids })
        });
        const data = await res.json();
        if (res.ok && data.status === "ok") {
            showToast(`🗑️ ${data.deleted_count || ids.length} leads deleted successfully!`, "success");
            allLeads = allLeads.filter(l => !selectedLeadIds.has(l.id));
            selectedLeadIds.clear();
            filterLeadsTable();
            populateFilterDropdowns(allLeads);
            fetchStats();
        } else {
            showToast(`Bulk delete failed: ${data.detail || data.message || "Unknown error"}`, "error");
        }
    } catch (err) {
        showToast(`Error deleting leads: ${err}`, "error");
    }
}

// Delete ALL Leads Across Database
async function confirmDeleteAllLeads() {
    const total = allLeads.length;
    if (total === 0) {
        showToast("Database is already empty.", "info");
        return;
    }

    const firstConfirm = confirm(`⚠️ DANGER: Are you sure you want to delete ALL ${total} leads from your database?\n\nThis will clear all discovered, verified, and scored leads.`);
    if (!firstConfirm) return;

    const typed = prompt(`To confirm wiping all ${total} leads, type DELETE in uppercase:`);
    if (typed !== "DELETE") {
        showToast("Action cancelled: verification text did not match.", "info");
        return;
    }

    try {
        const res = await fetch("/api/leads/delete-all", {
            method: "POST"
        });
        const data = await res.json();
        if (res.ok && data.status === "ok") {
            showToast(`💥 All leads have been deleted from the database!`, "success");
            allLeads = [];
            selectedLeadIds.clear();
            filterLeadsTable();
            populateFilterDropdowns(allLeads);
            fetchStats();
        } else {
            showToast(`Delete all failed: ${data.detail || data.message || "Unknown error"}`, "error");
        }
    } catch (err) {
        showToast(`Error deleting all leads: ${err}`, "error");
    }
}

// Search and Filter Leads Table
function filterLeadsTable() {
    const searchEl = document.getElementById("leadSearchInput");
    const countryEl = document.getElementById("filterCountry");
    const cityEl = document.getElementById("filterCity");
    const catEl = document.getElementById("filterCategory");
    const tierEl = document.getElementById("filterTier");
    const statusEl = document.getElementById("filterStatus");
    const webStatusEl = document.getElementById("filterWebsiteStatus");
    const clearBtn = document.getElementById("clearSearchBtn");

    const query = searchEl ? searchEl.value.toLowerCase().trim() : "";
    if (clearBtn) {
        clearBtn.style.display = query.length > 0 ? "inline-block" : "none";
    }

    const selectedCountry = countryEl ? countryEl.value.toLowerCase().trim() : "";
    const selectedCity = cityEl ? cityEl.value.toLowerCase().trim() : "";
    const selectedCategory = catEl ? catEl.value.toLowerCase().trim() : "";
    const tier = tierEl ? tierEl.value.trim() : "";
    const status = statusEl ? statusEl.value.trim() : "";
    const webStatus = webStatusEl ? webStatusEl.value.trim() : "";

    const filtered = allLeads.filter(l => {
        const nameMatch = l.name && l.name.toLowerCase().includes(query);
        const phoneMatch = l.phone && l.phone.toLowerCase().includes(query);
        const cityMatch = l.city && l.city.toLowerCase().includes(query);
        const catMatch = l.category && l.category.toLowerCase().includes(query);
        const addrMatch = l.address && l.address.toLowerCase().includes(query);
        const idMatch = String(l.id) === query || `#${l.id}` === query;

        const matchesQuery = !query || nameMatch || phoneMatch || cityMatch || catMatch || addrMatch || idMatch;
        const matchesCountry = !selectedCountry || inferLeadCountry(l).toLowerCase() === selectedCountry;
        const matchesCity = !selectedCity || (l.city && l.city.toLowerCase().includes(selectedCity));
        const matchesCat = !selectedCategory || (l.category && l.category.toLowerCase().includes(selectedCategory));
        const matchesTier = !tier || l.lead_tier === tier;
        const matchesStatus = !status || l.status === status;
        const matchesWeb = !webStatus || l.website_status === webStatus;

        return matchesQuery && matchesCountry && matchesCity && matchesCat && matchesTier && matchesStatus && matchesWeb;
    });

    renderLeadsTable(filtered);

    const counterEl = document.getElementById("tableCounterText");
    if (counterEl) {
        counterEl.innerText = `Showing ${filtered.length} of ${allLeads.length} leads in database`;
    }
}

function clearSearchInput() {
    const searchEl = document.getElementById("leadSearchInput");
    if (searchEl) {
        searchEl.value = "";
        searchEl.focus();
        filterLeadsTable();
    }
}

function resetTableFilters() {
    const setVal = (id, val) => { const el = document.getElementById(id); if (el) el.value = val; };
    setVal("leadSearchInput", "");
    setVal("filterCountry", "");
    setVal("filterCity", "");
    setVal("filterCategory", "");
    setVal("filterTier", "");
    setVal("filterStatus", "");
    setVal("filterWebsiteStatus", "");
    filterLeadsTable();
}

// Open Edit Lead Modal
async function openEditLeadModal(leadId) {
    const modal = document.getElementById("editLeadModal");
    if (!modal) return;

    let lead = allLeads.find(l => l.id === leadId);
    if (!lead) {
        try {
            const res = await fetch(`/api/leads/${leadId}`);
            const data = await res.json();
            lead = data.lead;
        } catch(e) {}
    }
    if (!lead) {
        showToast("Lead not found", "error");
        return;
    }

    document.getElementById("editLeadHeaderTitle").innerText = `Edit: ${lead.name} (#${lead.id})`;
    document.getElementById("editLeadId").value = lead.id;
    document.getElementById("editLeadName").value = lead.name || "";
    document.getElementById("editLeadCategory").value = lead.category || "";
    document.getElementById("editLeadCity").value = lead.city || "";
    document.getElementById("editLeadPhone").value = lead.phone || "";
    document.getElementById("editLeadEmail").value = lead.email || "";
    document.getElementById("editLeadWebsite").value = lead.website || "";
    document.getElementById("editLeadWebsiteStatus").value = lead.website_status || "PENDING";
    document.getElementById("editLeadTier").value = lead.lead_tier || "";
    document.getElementById("editLeadScore").value = lead.score !== null && lead.score !== undefined ? lead.score : "";
    document.getElementById("editLeadStatus").value = lead.status || "DISCOVERED";
    document.getElementById("editLeadAddress").value = lead.address || "";
    document.getElementById("editLeadWhatsAppMessage").value = lead.whatsapp_message || "";

    modal.classList.add("show");
}

// Save Edited Lead
async function handleSaveEditLead(e) {
    e.preventDefault();
    const leadId = document.getElementById("editLeadId").value;
    const btn = document.getElementById("btnSaveEditLead");
    if (btn) btn.innerText = "Saving...";

    const payload = {
        name: document.getElementById("editLeadName").value.trim(),
        category: document.getElementById("editLeadCategory").value.trim(),
        city: document.getElementById("editLeadCity").value.trim(),
        phone: document.getElementById("editLeadPhone").value.trim(),
        email: document.getElementById("editLeadEmail").value.trim(),
        website: document.getElementById("editLeadWebsite").value.trim(),
        website_status: document.getElementById("editLeadWebsiteStatus").value,
        lead_tier: document.getElementById("editLeadTier").value || null,
        score: document.getElementById("editLeadScore").value ? parseFloat(document.getElementById("editLeadScore").value) : null,
        status: document.getElementById("editLeadStatus").value,
        address: document.getElementById("editLeadAddress").value.trim(),
        whatsapp_message: document.getElementById("editLeadWhatsAppMessage").value.trim(),
    };

    try {
        const res = await fetch(`/api/leads/${leadId}`, {
            method: "PUT",
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload)
        });
        const data = await res.json();
        if (res.ok && data.status === "ok") {
            showToast(`✅ Lead #${leadId} updated successfully!`, "success");
            closeModal("editLeadModal");

            // Update in local memory array
            const idx = allLeads.findIndex(l => l.id === parseInt(leadId));
            if (idx !== -1) {
                allLeads[idx] = { ...allLeads[idx], ...payload };
            }
            filterLeadsTable();
            populateFilterDropdowns(allLeads);
            fetchStats();
        } else {
            showToast(`Update failed: ${data.detail || data.message || "Unknown error"}`, "error");
        }
    } catch (err) {
        showToast(`Error updating lead: ${err}`, "error");
    } finally {
        if (btn) btn.innerText = "💾 Save Changes";
    }
}

// Delete Lead Permanently
async function deleteLead(leadId, leadName) {
    const confirmed = confirm(`Are you sure you want to permanently delete lead #${leadId} (${leadName})?\n\nThis will remove the lead from your database.`);
    if (!confirmed) return;

    try {
        const res = await fetch(`/api/leads/${leadId}`, {
            method: "DELETE"
        });
        const data = await res.json();
        if (res.ok && data.status === "ok") {
            showToast(`🗑️ Lead #${leadId} deleted successfully!`, "success");
            allLeads = allLeads.filter(l => l.id !== leadId);
            filterLeadsTable();
            populateFilterDropdowns(allLeads);
            fetchStats();
        } else {
            showToast(`Delete failed: ${data.detail || data.message || "Unknown error"}`, "error");
        }
    } catch (err) {
        showToast(`Error deleting lead: ${err}`, "error");
    }
}

function formatPhoneForWhatsApp(phone) {
    if (!phone) return "";
    let digits = phone.replace(/\D/g, "");
    if (digits.length === 10) return "91" + digits;
    if (digits.length === 11 && digits.startsWith("0")) return "91" + digits.slice(1);
    if (digits.length >= 10 && !digits.startsWith("91")) return "91" + digits;
    return digits;
}

function openWhatsAppDirect(phone, messageText, demoUrl) {
    const formattedPhone = formatPhoneForWhatsApp(phone);
    if (!formattedPhone) {
        showToast("Invalid or missing phone number for WhatsApp", "error");
        return;
    }
    let body = messageText || `Hi! Check out your website demo: ${demoUrl}`;
    if (demoUrl && !body.includes(demoUrl)) {
        body += `\n\nPreview Link: ${demoUrl}`;
    }
    const url = `https://wa.me/${formattedPhone}?text=${encodeURIComponent(body)}`;
    window.open(url, "_blank");
}

function escapeQuotes(str) {
    if (!str) return "";
    return str.replace(/'/g, "\\'").replace(/"/g, '&quot;');
}

function formatDemoUrl(rawUrl, title) {
    if (!rawUrl && !title) return "/preview/demo";
    if (rawUrl && rawUrl.includes("/preview/")) {
        const pathPart = rawUrl.split("/preview/")[1];
        return "/preview/" + pathPart.split("?")[0].split("#")[0];
    }
    if (rawUrl && (rawUrl.startsWith("http://") || rawUrl.startsWith("https://"))) {
        try {
            const u = new URL(rawUrl);
            if (u.pathname && u.pathname.startsWith("/preview/")) {
                return u.pathname;
            }
        } catch(e) {}
    }
    if (title && title !== "undefined") {
        const slug = title.toLowerCase().replace(/[^a-z0-9]+/g, '-').replace(/(^-|-$)/g, '');
        return "/preview/" + slug;
    }
    return rawUrl || "/preview/demo";
}

// Open Demo Preview Modal
function openDemoModal(demoUrl, title) {
    const cleanUrl = formatDemoUrl(demoUrl, title);
    const displayTitle = title && title !== "undefined" ? title : "Demo Website";
    
    const titleEl = document.getElementById("modalDemoTitle");
    const linkEl = document.getElementById("modalDemoExternalLink");
    const frameEl = document.getElementById("demoPreviewFrame");
    
    if (titleEl) titleEl.innerText = displayTitle;
    if (linkEl) linkEl.href = cleanUrl;
    if (frameEl) frameEl.src = cleanUrl;
    
    const modal = document.getElementById("demoModal");
    if (modal) modal.classList.add("show");
}

// Open Lead Detail Modal
async function openLeadModal(leadId) {
    const modal = document.getElementById("leadModal");
    const body = document.getElementById("modalLeadBody");
    modal.classList.add("show");
    body.innerHTML = "Loading lead profile...";

    try {
        const res = await fetch(`/api/leads/${leadId}`);
        const data = await res.json();
        const l = data.lead;

        const sp = l.site_profile || {};
        const seo = sp.seo_audit || {};
        const loadTime = seo.load_time_sec || sp.load_time_sec || 'N/A';
        const healthScore = seo.seo_health_score !== undefined && seo.seo_health_score !== null ? seo.seo_health_score : (sp.seo_health_score || 'N/A');
        const speedCategory = seo.speed_category || sp.speed_category || 'N/A';
        const criticals = seo.critical_problems || [];
        const seoIssuesList = (seo.seo_issues || []).filter(i => !criticals.includes(i) && !(seo.seo_opportunities || []).includes(i));
        const opportunities = seo.seo_opportunities || [];
        const passedList = seo.passed_checks || [];
        const recommendations = seo.seo_recommendations || [];
        const fin = seo.financial_impact || {};

        document.getElementById("modalLeadName").innerText = l.name;
        body.innerHTML = `
            <div style="display: flex; flex-direction: column; gap: 14px;">
                <div style="display: grid; grid-template-columns: 1fr 1fr; gap: 10px;">
                    <div><strong>📍 City:</strong> ${l.city}</div>
                    <div><strong>🏷️ Category:</strong> ${l.category || '-'}</div>
                    <div><strong>📞 Phone:</strong> ${l.phone || 'N/A'}</div>
                    <div><strong>✉️ Email:</strong> ${l.email || 'N/A'}</div>
                    <div><strong>🌐 Website:</strong> ${l.website ? `<a href="${l.website}" target="_blank" style="color:#f97316;">${l.website}</a>` : 'None'}</div>
                    <div><strong>⭐ Rating:</strong> ${l.rating || 'N/A'} (${l.reviews_count || 0} reviews)</div>
                </div>

                <!-- Senior SEO Audit Card -->
                <div class="msg-preview-box" style="background: rgba(30, 41, 59, 0.7); border: 1px solid rgba(59, 130, 246, 0.3);">
                    <div class="msg-preview-title" style="color: #60a5fa; display: flex; align-items: center; justify-content: space-between;">
                        <span>🔍 Senior SEO Recruiter & Audit Report</span>
                        ${fin.formatted_loss_range ? `<span class="badge badge-hot" style="font-size: 0.76rem;">💰 Est. Revenue Loss: ${fin.formatted_loss_range}</span>` : ''}
                    </div>
                    <div style="display: grid; grid-template-columns: 1fr 1fr 1fr; gap: 8px; margin-bottom: 10px; font-size: 0.84rem;">
                        <div>⚡ <strong>Load Speed:</strong> <span class="badge ${speedCategory === 'FAST' ? 'badge-success' : speedCategory === 'MODERATE' ? 'badge-info' : 'badge-hot'}">${loadTime}s (${speedCategory})</span></div>
                        <div>📈 <strong>SEO Health Score:</strong> <span class="badge ${healthScore >= 70 ? 'badge-success' : healthScore >= 50 ? 'badge-warm' : 'badge-hot'}">${healthScore}/100</span></div>
                        <div>🔒 <strong>SSL Security:</strong> ${seo.has_ssl !== false ? '✅ HTTPS Enabled' : '❌ No SSL'}</div>
                    </div>
                    
                    <div style="font-size: 0.8rem; color: #cbd5e1; margin-bottom: 6px;">
                        <strong>On-Page Signals:</strong> 
                        Title: ${seo.has_title ? '✅' : '❌'} | Meta Description: ${seo.has_meta_description ? '✅' : '❌'} | H1 Tag: ${seo.has_h1 ? '✅' : '❌'} | Mobile Viewport: ${seo.has_mobile_viewport ? '✅' : '❌'}
                        ${fin.conversion_drop_percent ? `<span style="color: #fca5a5; margin-left: 8px;">(Est. Conversion Drop: -${fin.conversion_drop_percent}%)</span>` : ''}
                    </div>

                    ${criticals.length > 0 ? `
                        <div style="color: #ef4444; font-weight: 700; font-size: 0.82rem; margin-top: 8px;">🔴 Critical Problems:</div>
                        <ul style="padding-left: 18px; color: #fca5a5; font-size: 0.78rem; margin: 4px 0;">
                            ${criticals.map(c => `<li>${c}</li>`).join('')}
                        </ul>
                    ` : ''}

                    ${seoIssuesList.length > 0 ? `
                        <div style="color: #f97316; font-weight: 700; font-size: 0.82rem; margin-top: 8px;">🟠 SEO Issues:</div>
                        <ul style="padding-left: 18px; color: #fdba74; font-size: 0.78rem; margin: 4px 0;">
                            ${seoIssuesList.map(i => `<li>${i}</li>`).join('')}
                        </ul>
                    ` : ''}

                    ${opportunities.length > 0 ? `
                        <div style="color: #eab308; font-weight: 700; font-size: 0.82rem; margin-top: 8px;">🟡 SEO Opportunities:</div>
                        <ul style="padding-left: 18px; color: #fef08a; font-size: 0.78rem; margin: 4px 0;">
                            ${opportunities.map(o => `<li>${o}</li>`).join('')}
                        </ul>
                    ` : ''}

                    ${passedList.length > 0 ? `
                        <div style="color: #22c55e; font-weight: 700; font-size: 0.82rem; margin-top: 8px;">🟢 Passed Checks:</div>
                        <ul style="padding-left: 18px; color: #86efac; font-size: 0.78rem; margin: 4px 0;">
                            ${passedList.map(p => `<li>${p}</li>`).join('')}
                        </ul>
                    ` : ''}

                    ${recommendations.length > 0 ? `
                        <div style="color: #38bdf8; font-weight: 700; font-size: 0.82rem; margin-top: 8px;">💡 Action Recommendations:</div>
                        <ul style="padding-left: 18px; color: #7dd3fc; font-size: 0.78rem; margin: 4px 0;">
                            ${recommendations.map(r => `<li>${r}</li>`).join('')}
                        </ul>
                    ` : ''}
                </div>

                <div class="msg-preview-box">
                    <div class="msg-preview-title">📊 Qualification Score Reasons</div>
                    <ul style="padding-left: 18px; color: #94a3b8; font-size: 0.82rem;">
                        ${(l.score_reasons || []).map(r => `<li>${r}</li>`).join('') || '<li>No reasons recorded</li>'}
                    </ul>
                </div>

                <div class="msg-preview-box">
                    <div class="msg-preview-title">📧 AI Cold Email Pitch</div>
                    <div style="font-weight:600; margin-bottom:4px;">Subject: ${l.email_subject || 'N/A'}</div>
                    <div style="color: #94a3b8; font-size: 0.82rem; white-space: pre-line;">${l.email_message || 'No email generated yet.'}</div>
                </div>

                <div class="msg-preview-box">
                    <div class="msg-preview-title">📱 AI WhatsApp Message</div>
                    <div style="color: #94a3b8; font-size: 0.82rem; white-space: pre-line;">${l.whatsapp_message || 'No WhatsApp message generated yet.'}</div>
                </div>
            </div>
        `;
    } catch (err) {
        body.innerHTML = `Error loading details: ${err}`;
    }
}

function closeModal(modalId) {
    document.getElementById(modalId).classList.remove("show");
    if (modalId === "demoModal") {
        document.getElementById("demoPreviewFrame").src = "";
    }
}

function closeModalOnBackdrop(event, modalId) {
    if (event.target.id === modalId) {
        closeModal(modalId);
    }
}

// Fetch Live Console Logs
async function fetchLiveLogs() {
    try {
        const res = await fetch(`/api/logs?limit=40`);
        const data = await res.json();
        const logs = data.logs || [];

        // Update full console
        const consoleBox = document.getElementById("fullConsoleLogs");
        if (consoleBox) {
            consoleBox.innerHTML = `<pre class="console-text">${logs.join("\n")}</pre>`;
        }

        // Update overview preview stream
        const streamBox = document.getElementById("recentLogsStream");
        if (streamBox) {
            streamBox.innerHTML = logs.slice(-12).map(l => `<div class="log-line">${l}</div>`).join("");
        }
    } catch (err) {
        console.error("Error fetching logs:", err);
    }
}

function clearConsoleView() {
    document.getElementById("fullConsoleLogs").innerHTML = `<pre class="console-text">[Cleared console view]</pre>`;
}

function inferLeadCountry(lead) {
    const text = `${lead.city || ""} ${lead.address || ""}`.toUpperCase();
    const canadianMarkers = ["CANADA", " CN", ", ON", " ON ", ", BC", " BC ", ", AB", " AB ", ", MB", " MB ", ", SK", " SK ", ", NS", " NS ", ", NB", " NB ", ", NL", " NL ", ", PE", " PE ", ", QC", " QC ", ", NT", " NT ", ", YT", " YT ", ", NU", " NU "];
    if (canadianMarkers.some(m => text.includes(m)) || text.trim().endsWith(" CN")) return "Canada";
    if (text.includes("INDIA") || [" GUJARAT", " PUNJAB", " HARYANA", " DELHI", " MAHARASHTRA", " RAJASTHAN", " KARNATAKA"].some(m => text.includes(m))) return "India";
    return "Other";
}

function exportToCsv() {
    showToast("📥 Exporting CSV file...", "info");
    const params = new URLSearchParams();
    const values = {
        country: document.getElementById("filterCountry")?.value || "",
        city: document.getElementById("filterCity")?.value || "",
        category: document.getElementById("filterCategory")?.value || "",
        tier: document.getElementById("filterTier")?.value || "",
        status: document.getElementById("filterStatus")?.value || "",
        website_status: document.getElementById("filterWebsiteStatus")?.value || "",
        search: document.getElementById("leadSearchInput")?.value || ""
    };
    Object.entries(values).forEach(([key, value]) => { if (value) params.set(key, value); });

    const downloadUrl = `/api/export/csv?${params.toString()}`;
    const a = document.createElement("a");
    a.style.display = "none";
    a.href = downloadUrl;
    document.body.appendChild(a);
    a.click();
    setTimeout(() => a.remove(), 1000);
}

