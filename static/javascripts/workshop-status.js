// Workshop Status Updates
// Fetches upcoming workshop data and updates the UI

(function() {
  'use strict';

  // Configuration - detect base URL
  const baseUrl = window.location.pathname.includes('/dlab-workshops/') ? '/dlab-workshops' : '';
  const UPCOMING_WORKSHOPS_URL = baseUrl + '/data/upcoming_workshops.json';
  const WORKSHOP_MAPPINGS_URL = baseUrl + '/data/workshop_mappings.yml';

  // Cache for performance
  let workshopData = null;
  let mappingsData = null;

  // Initialize when DOM is ready
  if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', init);
  } else {
    init();
  }

  function init() {
    // Add loading state to all badges
    document.querySelectorAll('.upcoming-session-badge').forEach(badge => {
      badge.classList.add('loading');
    });

    // Fetch workshop data
    fetchWorkshopData();
  }

  async function fetchWorkshopData() {
    try {
      // Fetch upcoming workshops JSON
      const response = await fetch(UPCOMING_WORKSHOPS_URL);
      if (response.ok) {
        workshopData = await response.json();
        updateAllWorkshopCards();
      } else {
        console.warn('No upcoming workshops data found');
        removeLoadingStates();
      }
    } catch (error) {
      console.error('Error fetching workshop data:', error);
      removeLoadingStates();
    }
  }

  function updateAllWorkshopCards() {
    if (!workshopData || !workshopData.workshops) return;

    // Get all workshop cards
    const workshopCards = document.querySelectorAll('[data-workshop-title]');
    
    workshopCards.forEach(card => {
      const cardTitle = card.dataset.workshopTitle;
      const matchingWorkshop = findMatchingWorkshop(cardTitle);
      
      if (matchingWorkshop) {
        updateWorkshopCard(card, matchingWorkshop);
      } else {
        showNoUpcomingSessions(card);
      }
    });
  }

  function findMatchingWorkshop(cardTitle) {
    if (!workshopData || !workshopData.workshops) return null;

    // First try exact title matching
    let match = workshopData.workshops.find(w => 
      w.title.toLowerCase().trim() === cardTitle.toLowerCase().trim()
    );

    // If no exact match, try matching base titles (without part specifications)
    // But only match Part 1 or workshops without parts (since registration is only for Part 1)
    if (!match) {
      // Extract base title (everything before ": Part")
      const cardBase = cardTitle.split(': Part')[0].toLowerCase().trim();
      
      // Find workshops that match the base title
      const matches = workshopData.workshops.filter(w => {
        const workshopBase = w.title.split(': Part')[0].toLowerCase().trim();
        return workshopBase === cardBase;
      });
      
      // From the matches, prefer Part 1 or workshops without parts
      match = matches.find(w => {
        return w.title.includes(': Part 1') || !w.title.includes(': Part');
      });
      
      // If no Part 1 found, return the first match (if any)
      if (!match && matches.length > 0) {
        match = matches[0];
      }
    }

    return match;
  }

  function normalizeTitle(title) {
    return title.toLowerCase()
      .replace(/[^a-z0-9\s]/g, '')
      .replace(/\s+/g, ' ')
      .replace(/parts\s+\d+[-–]\d+/g, 'parts')  // Normalize "Parts 1-3" to just "parts"
      .trim();
  }

  function titlesMatch(title1, title2) {
    const norm1 = normalizeTitle(title1);
    const norm2 = normalizeTitle(title2);

    // Check if one contains the other
    if (norm1.includes(norm2) || norm2.includes(norm1)) {
      return true;
    }

    // Check for common workshop patterns
    const patterns = [
      /python fundamentals/i,
      /r fundamentals/i,
      /data wrangling/i,
      /machine learning/i,
      /data visualization/i,
      /ai.?assisted coding/i,
      /copilot/i
    ];

    for (const pattern of patterns) {
      if (pattern.test(title1) && pattern.test(title2)) {
        return true;
      }
    }

    return false;
  }

  function updateWorkshopCard(card, workshop) {
    // Mark the card as active
    const workshopCard = card.closest('.workshop-card') || card;
    workshopCard.setAttribute('data-active', 'true');
    
    // Find badge container within the card
    const badgeContainer = workshopCard.querySelector('.upcoming-session-badge');
    if (badgeContainer) {
      badgeContainer.classList.remove('loading');
      const badge = createSessionBadge(workshop);
      badgeContainer.innerHTML = badge;
    }

    // Find register button container within the card
    const registerContainer = workshopCard.querySelector('.register-button-container');
    if (registerContainer && workshop.registration_url) {
      const button = createRegisterButton(workshop);
      registerContainer.innerHTML = button;
    }
  }

  function createSessionBadge(workshop) {
    const sessionDate = new Date(workshop.datetime_iso);
    const now = new Date();
    const daysUntil = Math.floor((sessionDate - now) / (1000 * 60 * 60 * 24));
    
    let badgeClass = 'badge-upcoming';
    let badgeText = `Next: ${formatDate(sessionDate)}`;
    
    if (daysUntil <= 7) {
      badgeClass = 'badge-upcoming';
      if (daysUntil === 0) {
        // Use the time field from the workshop data instead of converting
        badgeText = `Today at ${workshop.time}`;
      } else if (daysUntil === 1) {
        // Use the time field from the workshop data instead of converting
        badgeText = `Tomorrow at ${workshop.time}`;
      }
    } else if (daysUntil <= 30) {
      badgeClass = 'badge-upcoming-soon';
    }

    return `<span class="badge badge-pill ${badgeClass}">
      <i class="fas fa-calendar-alt"></i> ${badgeText}
    </span>`;
  }

  function createRegisterButton(workshop) {
    return `<a href="${workshop.registration_url}" 
            class="btn btn-sm btn-register" 
            target="_blank">
      <i class="fas fa-user-plus"></i> Register Now
    </a>`;
  }

  function showNoUpcomingSessions(card) {
    if (card.classList.contains('upcoming-session-badge')) {
      card.classList.remove('loading');
      card.innerHTML = `<span class="badge badge-pill badge-no-sessions">
        <i class="fas fa-clock"></i> No scheduled sessions
      </span>`;
    }
  }

  function removeLoadingStates() {
    document.querySelectorAll('.upcoming-session-badge.loading').forEach(badge => {
      badge.classList.remove('loading');
    });
  }

  function formatDate(date) {
    const options = { month: 'short', day: 'numeric' };
    return date.toLocaleDateString('en-US', options);
  }

  function formatTime(date) {
    const options = { hour: 'numeric', minute: '2-digit', hour12: true };
    return date.toLocaleTimeString('en-US', options);
  }

  // Expose functions for debugging
  window.workshopStatus = {
    refresh: fetchWorkshopData,
    getData: () => workshopData
  };

})();