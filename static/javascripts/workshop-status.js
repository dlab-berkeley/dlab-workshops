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

    // Normalize the card title for comparison
    const normalizedCardTitle = cardTitle.toLowerCase().trim();
    const now = new Date();

    // Look for exact match first (for standalone workshops)
    let match = workshopData.workshops.find(w => {
      // Skip non-registrable parts
      if (w.title.includes(': Part 2') || w.title.includes(': Part 3') ||
          w.title.includes(': Part 4') || w.title.includes(': Part 5') ||
          w.title.includes(': Part 6')) {
        return false;
      }

      // Skip past workshops
      const workshopDate = new Date(w.datetime_iso);
      if (workshopDate < now) {
        return false;
      }

      return w.title.toLowerCase().trim() === normalizedCardTitle;
    });

    // If no exact match, try matching base titles (for multi-part workshops)
    if (!match) {
      const cardBase = cardTitle.split(': Part')[0].toLowerCase().trim();

      match = workshopData.workshops.find(w => {
        // Skip non-registrable parts
        if (w.title.includes(': Part 2') || w.title.includes(': Part 3') ||
            w.title.includes(': Part 4') || w.title.includes(': Part 5') ||
            w.title.includes(': Part 6')) {
          return false;
        }

        // Skip past workshops
        const workshopDate = new Date(w.datetime_iso);
        if (workshopDate < now) {
          return false;
        }

        const upcomingBase = w.title.split(': Part')[0].toLowerCase().trim();
        return upcomingBase === cardBase;
      });
    }

    // If still no match, try fuzzy contains matching (like Jekyll does)
    if (!match) {
      match = workshopData.workshops.find(w => {
        // Skip non-registrable parts
        if (w.title.includes(': Part 2') || w.title.includes(': Part 3') ||
            w.title.includes(': Part 4') || w.title.includes(': Part 5') ||
            w.title.includes(': Part 6')) {
          return false;
        }

        // Skip past workshops
        const workshopDate = new Date(w.datetime_iso);
        if (workshopDate < now) {
          return false;
        }

        const upcomingTitle = w.title.toLowerCase().trim();
        // Check if one contains the other (handles suffixes like "(In Person Only)")
        return upcomingTitle.includes(normalizedCardTitle) || normalizedCardTitle.includes(upcomingTitle);
      });
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

    let dateBadgeClass = 'badge-upcoming';
    let badgeText = `Next: ${formatDate(sessionDate)}`;

    if (daysUntil <= 7) {
      // Orange/yellow for urgent - happening soon!
      dateBadgeClass = 'badge-upcoming-soon';
      if (daysUntil === 0) {
        badgeText = `Today at ${workshop.time}`;
      } else if (daysUntil === 1) {
        badgeText = `Tomorrow at ${workshop.time}`;
      }
    } else {
      // Green for upcoming but not urgent
      dateBadgeClass = 'badge-upcoming';
    }

    // Return both "Available" badge and the date badge
    return `<span class="badge badge-pill badge-info mb-1"><i class="fas fa-calendar-check"></i> Available</span><span class="badge badge-pill ${dateBadgeClass}"><i class="fas fa-calendar-alt"></i> ${badgeText}</span>`;
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