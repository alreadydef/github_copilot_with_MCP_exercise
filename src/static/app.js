document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  const sessionActivitySelect = document.getElementById("session-activity");
  const sessionForm = document.getElementById("session-form");
  const sessionIdInput = document.getElementById("session-id");
  const sessionDateInput = document.getElementById("session-date");
  const sessionStartTimeInput = document.getElementById("session-start-time");
  const sessionEndTimeInput = document.getElementById("session-end-time");
  const sessionLocationInput = document.getElementById("session-location");
  const sessionSubmitBtn = document.getElementById("session-submit-btn");
  const sessionCancelBtn = document.getElementById("session-cancel-btn");
  const sessionMessageDiv = document.getElementById("session-message");
  const advisorSessionsList = document.getElementById("advisor-sessions-list");

  let activitiesCache = {};

  function showMessage(target, text, type) {
    target.textContent = text;
    target.className = type;
    target.classList.remove("hidden");

    setTimeout(() => {
      target.classList.add("hidden");
    }, 5000);
  }

  function formatSessionLabel(session) {
    const locationPart = session.location ? ` | ${session.location}` : "";
    return `${session.date} | ${session.start_time} - ${session.end_time}${locationPart}`;
  }

  function buildUpcomingSessionsHTML(details) {
    const upcoming = details.upcoming_sessions || [];
    if (!upcoming.length) {
      return `<p><strong>Upcoming sessions:</strong> <em>No upcoming sessions scheduled</em></p>`;
    }

    return `
      <div class="sessions-section">
        <h5>Upcoming sessions</h5>
        <ul class="session-list">
          ${upcoming
            .map((session) => `<li>${formatSessionLabel(session)}</li>`)
            .join("")}
        </ul>
      </div>
    `;
  }

  function populateActivityDropdowns(activities) {
    activitySelect.innerHTML = '<option value="">-- Select an activity --</option>';
    sessionActivitySelect.innerHTML =
      '<option value="">-- Select an activity --</option>';

    Object.keys(activities).forEach((name) => {
      const studentOption = document.createElement("option");
      studentOption.value = name;
      studentOption.textContent = name;
      activitySelect.appendChild(studentOption);

      const advisorOption = document.createElement("option");
      advisorOption.value = name;
      advisorOption.textContent = name;
      sessionActivitySelect.appendChild(advisorOption);
    });
  }

  function resetSessionForm() {
    sessionIdInput.value = "";
    sessionForm.reset();
    sessionSubmitBtn.textContent = "Create Session";
    sessionCancelBtn.classList.add("hidden");
  }

  function populateAdvisorSessionList(activities) {
    advisorSessionsList.innerHTML = "";

    Object.entries(activities).forEach(([activityName, details]) => {
      const wrapper = document.createElement("div");
      wrapper.className = "advisor-activity-group";

      const sessions = details.sessions || [];
      const sessionsHtml = sessions.length
        ? sessions
            .map(
              (session) => `
                <li>
                  <span>${formatSessionLabel(session)}</span>
                  <div class="session-actions">
                    <button class="session-edit-btn" data-activity="${activityName}" data-session-id="${session.id}">Edit</button>
                    <button class="session-delete-btn" data-activity="${activityName}" data-session-id="${session.id}">Delete</button>
                  </div>
                </li>
              `
            )
            .join("")
        : "<li><em>No sessions yet</em></li>";

      wrapper.innerHTML = `
        <h5>${activityName}</h5>
        <ul class="session-list advisor-session-list">
          ${sessionsHtml}
        </ul>
      `;

      advisorSessionsList.appendChild(wrapper);
    });

    document.querySelectorAll(".session-edit-btn").forEach((button) => {
      button.addEventListener("click", handleEditSession);
    });

    document.querySelectorAll(".session-delete-btn").forEach((button) => {
      button.addEventListener("click", handleDeleteSession);
    });
  }

  // Function to fetch activities from API
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();
      activitiesCache = activities;

      // Clear loading message
      activitiesList.innerHTML = "";

      populateActivityDropdowns(activities);

      // Populate activities list
      Object.entries(activities).forEach(([name, details]) => {
        const activityCard = document.createElement("div");
        activityCard.className = "activity-card";

        const spotsLeft =
          details.max_participants - details.participants.length;

        // Create participants HTML with delete icons instead of bullet points
        const participantsHTML =
          details.participants.length > 0
            ? `<div class="participants-section">
              <h5>Participants:</h5>
              <ul class="participants-list">
                ${details.participants
                  .map(
                    (email) =>
                      `<li><span class="participant-email">${email}</span><button class="delete-btn" data-activity="${name}" data-email="${email}">❌</button></li>`
                  )
                  .join("")}
              </ul>
            </div>`
            : `<p><em>No participants yet</em></p>`;

        activityCard.innerHTML = `
          <h4>${name}</h4>
          <p>${details.description}</p>
          <p><strong>Schedule:</strong> ${details.schedule}</p>
          ${buildUpcomingSessionsHTML(details)}
          <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
          <div class="participants-container">
            ${participantsHTML}
          </div>
        `;

        activitiesList.appendChild(activityCard);
      });

      populateAdvisorSessionList(activities);

      // Add event listeners to delete buttons
      document.querySelectorAll(".delete-btn").forEach((button) => {
        button.addEventListener("click", handleUnregister);
      });
    } catch (error) {
      activitiesList.innerHTML =
        "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle unregister functionality
  async function handleUnregister(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const email = button.getAttribute("data-email");

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/unregister?email=${encodeURIComponent(email)}`,
        {
          method: "DELETE",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";

        // Refresh activities list to show updated participants
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      showMessage(
        messageDiv,
        response.ok ? result.message : result.detail || "An error occurred",
        response.ok ? "success" : "error"
      );
    } catch (error) {
      messageDiv.textContent = "Failed to unregister. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error unregistering:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(
          activity
        )}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();

        // Refresh activities list to show updated participants
        fetchActivities();
      }

      showMessage(
        messageDiv,
        response.ok ? result.message : result.detail || "An error occurred",
        response.ok ? "success" : "error"
      );
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  async function handleDeleteSession(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const sessionId = button.getAttribute("data-session-id");

    try {
      const response = await fetch(
        `/advisor/activities/${encodeURIComponent(activity)}/sessions/${sessionId}`,
        {
          method: "DELETE",
        }
      );
      const result = await response.json();

      showMessage(
        sessionMessageDiv,
        response.ok ? result.message : result.detail || "An error occurred",
        response.ok ? "success" : "error"
      );

      if (response.ok) {
        fetchActivities();
      }
    } catch (error) {
      showMessage(sessionMessageDiv, "Failed to delete session.", "error");
      console.error("Error deleting session:", error);
    }
  }

  function handleEditSession(event) {
    const button = event.target;
    const activity = button.getAttribute("data-activity");
    const sessionId = Number(button.getAttribute("data-session-id"));

    const activityDetails = activitiesCache[activity];
    if (!activityDetails) {
      return;
    }

    const session = (activityDetails.sessions || []).find((item) => item.id === sessionId);
    if (!session) {
      return;
    }

    sessionActivitySelect.value = activity;
    sessionIdInput.value = String(session.id);
    sessionDateInput.value = session.date;
    sessionStartTimeInput.value = session.start_time;
    sessionEndTimeInput.value = session.end_time;
    sessionLocationInput.value = session.location || "";

    sessionSubmitBtn.textContent = "Update Session";
    sessionCancelBtn.classList.remove("hidden");
  }

  sessionCancelBtn.addEventListener("click", () => {
    resetSessionForm();
  });

  sessionForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const activity = sessionActivitySelect.value;
    const sessionId = sessionIdInput.value;

    const payload = {
      date: sessionDateInput.value,
      start_time: sessionStartTimeInput.value,
      end_time: sessionEndTimeInput.value,
      location: sessionLocationInput.value || null,
    };

    const isEditing = Boolean(sessionId);
    const url = isEditing
      ? `/advisor/activities/${encodeURIComponent(activity)}/sessions/${sessionId}`
      : `/advisor/activities/${encodeURIComponent(activity)}/sessions`;

    const method = isEditing ? "PUT" : "POST";

    try {
      const response = await fetch(url, {
        method,
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(payload),
      });

      const result = await response.json();

      showMessage(
        sessionMessageDiv,
        response.ok ? result.message : result.detail || "An error occurred",
        response.ok ? "success" : "error"
      );

      if (response.ok) {
        resetSessionForm();
        fetchActivities();
      }
    } catch (error) {
      showMessage(sessionMessageDiv, "Failed to save session.", "error");
      console.error("Error saving session:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
