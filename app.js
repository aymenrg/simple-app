// --- SECURITY: REGISTER FUNCTION ---
async function registerUser() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const msgBox = document.getElementById("loginStatus");

    // Basic frontend validation before bothering the server
    if (user.length < 3 || pass.length < 6) {
        msgBox.style.color = "red";
        msgBox.innerText = "Username must be 3+ chars, Password 6+ chars.";
        return;
    }

    try {
        const response = await fetch("/register", {
            method: "POST",
            headers: { "Content-Type": "application/json" },
            // Notice registration requires JSON, unlike Login which requires Form Data
            body: JSON.stringify({ username: user, password: pass })
        });

        if (response.status === 201) {
            msgBox.style.color = "green";
            msgBox.innerText = "Registration Successful! You may now Log In.";
        } else if (response.status === 400) {
            msgBox.style.color = "red";
            msgBox.innerText = "Registration Failed: Username already taken.";
        } else {
            msgBox.style.color = "red";
            msgBox.innerText = "Registration Failed. Check inputs.";
        }
    } catch (error) {
        msgBox.style.color = "red";
        msgBox.innerText = "Error reaching authentication server.";
    }
}

// --- SECURITY: LOGIN FUNCTION ---
async function loginUser() {
    const user = document.getElementById("username").value;
    const pass = document.getElementById("password").value;
    const msgBox = document.getElementById("loginStatus");

    const formData = new URLSearchParams();
    formData.append("username", user);
    formData.append("password", pass);

    try {
        const response = await fetch("/login", {
            method: "POST",
            headers: { "Content-Type": "application/x-www-form-urlencoded" },
            body: formData
        });

        if (response.ok) {
            // WE NO LONGER DO THIS: localStorage.setItem("my_jwt", data.access_token);
            msgBox.style.color = "green";
            msgBox.innerText = "Login Successful! System Unlocked.";
        } else {
            msgBox.style.color = "red";
            msgBox.innerText = "Login Failed. Check credentials.";
        }
    } catch (error) {
        msgBox.style.color = "red";
        msgBox.innerText = "Error reaching authentication server.";
    }
}

// --- APP: INJECT DATA ---
async function submitData() {
    const status = document.getElementById('statusInput').value;
    const metric = parseFloat(document.getElementById('metricInput').value);
    const msgBox = document.getElementById('message');
    const token = localStorage.getItem("my_jwt"); // Grab the VIP pass

    msgBox.style.color = "blue";
    msgBox.innerText = "Sending data to server...";

    try {
        const response = await fetch('/records', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            credentials: 'same-origin', // <-- THIS TELLS THE BROWSER TO SEND THE COOKIE
            body: JSON.stringify({ status: status, metric: metric })
        });

        if (response.ok) {
            msgBox.style.color = "green";
            msgBox.innerText = "Success: Record injected!";
            document.getElementById('statusInput').value = '';
            document.getElementById('metricInput').value = '';
        } else if (response.status === 401) {
            msgBox.style.color = "red";
            msgBox.innerText = "Error: Unauthorized. Please log in first.";
        } else {
            msgBox.style.color = "red";
            msgBox.innerText = "Error: Blocked by Pydantic Validation.";
        }
    } catch (error) {
        msgBox.style.color = "red";
        msgBox.innerText = "Critical Error: Cannot reach the backend.";
    }
}

// --- APP: LOAD SUMMARY ---
async function loadSummary() {
    const box = document.getElementById('summaryBox');
    box.innerHTML = "<p>Crunching numbers...</p>";

    try {
        const response = await fetch('/summary', {
            // Remove the Authorization header and add credentials
            credentials: 'same-origin' 
        });
        
        if (response.status === 401) {
            box.innerHTML = "<p style='color:red;'>Unauthorized. Please log in.</p>";
            return;
        }

        const data = await response.json();
        if (data.message) {
            box.innerHTML = `<p>${data.message}</p>`;
        } else {
            box.innerHTML = `
                <p><strong>Total Records:</strong> ${data.total_records}</p>
                <p><strong>Sum of Metrics:</strong> ${data.total_metric_sum}</p>
                <p><strong>Average Metric:</strong> ${data.average_metric.toFixed(2)}</p>
            `;
        }
    } catch (error) {
        box.innerHTML = "<p style='color:red;'>Failed to load summary.</p>";
    }
}

// --- APP: EXPORT CSV ---
// Note: This relies on standard browser navigation, which cannot send JWT headers.
function exportCSV() {
    window.location.href = '/export';
}