document.addEventListener("DOMContentLoaded", function () {
    var screen_id = document.getElementById('screen_id')?.value || '';
    var refreshInterval = parseInt(document.getElementById('acs_refresh_time')?.value) || 5000;
    const showImage = document.getElementById("show_patient_name_image")?.value.toLowerCase() === "true";
    const showCabin = document.getElementById("show_cabin")?.value.toLowerCase() === "true";
    let companyLocaleLang = null;
    let previousStates = {};

    function playNotificationSound() {
        const audio = document.getElementById('notificationSound');
        if (audio) audio.play();
    }
    function updateDateTime() {
        const now = new Date();
        const options = {
            weekday: 'short',
            year: 'numeric',
            month: 'short',
            day: 'numeric',
            hour: '2-digit',
            minute: '2-digit',
            second: '2-digit'
        };
        const $container = document.getElementById('currentDateTime');
        const locale = companyLocaleLang || navigator.languages?.[0] || 'en-IN';
        if ($container) {
            $container.innerHTML = now.toLocaleString(locale, options);
        }
    }
    function refreshQueueData() {
        fetch(`/almightycs/waitingscreen/data/${screen_id}`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({  })
            })
            .then(response => {
                if (!response.ok) {
                    throw new Error("Network response was not ok: " + response.statusText);
                }
                return response.json();
            })
            .then(data => {
                const htmlString = data.result.html || "";
                const $container = document.querySelector(".acs_row");
                const newStates = data.result.states || {};
                let stateChanged = false;
                if ($container) {
                    $container.innerHTML = htmlString;
                    const newcompanylang = document.getElementById('company_lang')?.value;
                    if (newcompanylang) {
                        companyLocaleLang = newcompanylang;
                    }
                } else {
                    console.error("Container not found");
                }
                for (let recId in newStates) {
                    const newState = newStates[recId];
                    const oldState = previousStates[recId];
                    if (oldState && oldState !== newState && ['waiting', 'in_consultation'].includes(newState)) {
                        stateChanged = true;
                    }
                    if (!oldState && ['waiting', 'in_consultation'].includes(newState)) {
                        stateChanged = true;
                    }
                }
                previousStates = newStates;
                if (stateChanged) {
                    playNotificationSound();
                }
            })
            .catch(error => {
                console.error("Fetch error:", error);
            });
    }
    refreshQueueData();
    updateDateTime();
    setInterval(refreshQueueData, refreshInterval);
    setInterval(updateDateTime, 1000);
});