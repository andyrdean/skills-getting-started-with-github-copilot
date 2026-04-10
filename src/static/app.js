document.addEventListener("DOMContentLoaded", () => {
  const activitiesList = document.getElementById("activities-list");
  const activitySelect = document.getElementById("activity");
  const signupForm = document.getElementById("signup-form");
  const messageDiv = document.getElementById("message");

  // Function to render activity cards from data
  function renderActivities(activities) {
    activitiesList.innerHTML = "";

    Object.entries(activities).forEach(([name, details]) => {
      const activityCard = document.createElement("div");
      activityCard.className = "activity-card";

      const spotsLeft = details.max_participants - details.participants.length;

      const participantsList = details.participants.length > 0
        ? `<ul class="participants-list">${details.participants.map(p =>
            `<li><span class="participant-email">${p}</span><button class="remove-btn" data-activity="${name}" data-email="${p}" title="Remove participant">&times;</button></li>`
          ).join('')}</ul>`
        : '<p class="no-participants">No participants yet — be the first!</p>';

      activityCard.innerHTML = `
        <h4>${name}</h4>
        <p>${details.description}</p>
        <p><strong>Schedule:</strong> ${details.schedule}</p>
        <p><strong>Availability:</strong> ${spotsLeft} spots left</p>
        <div class="participants-section">
          <strong>Participants:</strong>
          ${participantsList}
        </div>
      `;

      activitiesList.appendChild(activityCard);
    });

    // Attach click handlers for remove buttons
    activitiesList.querySelectorAll(".remove-btn").forEach((btn) => {
      btn.addEventListener("click", async () => {
        const activity = btn.dataset.activity;
        const email = btn.dataset.email;
        try {
          const response = await fetch(
            `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
            { method: "DELETE" }
          );
          if (response.ok) {
            fetchActivities();
          } else {
            const result = await response.json();
            alert(result.detail || "Failed to remove participant");
          }
        } catch (error) {
          console.error("Error removing participant:", error);
        }
      });
    });
  }

  // Function to fetch and display activities
  async function fetchActivities() {
    try {
      const response = await fetch("/activities");
      const activities = await response.json();

      renderActivities(activities);

      // Populate activity select dropdown (only on initial load)
      if (activitySelect.options.length <= 1) {
        Object.keys(activities).forEach((name) => {
          const option = document.createElement("option");
          option.value = name;
          option.textContent = name;
          activitySelect.appendChild(option);
        });
      }
    } catch (error) {
      activitiesList.innerHTML = "<p>Failed to load activities. Please try again later.</p>";
      console.error("Error fetching activities:", error);
    }
  }

  // Handle form submission
  signupForm.addEventListener("submit", async (event) => {
    event.preventDefault();

    const email = document.getElementById("email").value;
    const activity = document.getElementById("activity").value;

    try {
      const response = await fetch(
        `/activities/${encodeURIComponent(activity)}/signup?email=${encodeURIComponent(email)}`,
        {
          method: "POST",
        }
      );

      const result = await response.json();

      if (response.ok) {
        messageDiv.textContent = result.message;
        messageDiv.className = "success";
        signupForm.reset();
        fetchActivities();
      } else {
        messageDiv.textContent = result.detail || "An error occurred";
        messageDiv.className = "error";
      }

      messageDiv.classList.remove("hidden");

      // Hide message after 5 seconds
      setTimeout(() => {
        messageDiv.classList.add("hidden");
      }, 5000);
    } catch (error) {
      messageDiv.textContent = "Failed to sign up. Please try again.";
      messageDiv.className = "error";
      messageDiv.classList.remove("hidden");
      console.error("Error signing up:", error);
    }
  });

  // Initialize app
  fetchActivities();
});
