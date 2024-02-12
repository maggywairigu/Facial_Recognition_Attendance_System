document.getElementById('takeAttendanceBtn').addEventListener('click', async function() {
    try {
        const response = await fetch('/startAttendance', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json'
            },
            // Optionally, you can send data with the request if needed
            body: JSON.stringify({ /* data if needed */ })
        });
        if (response.ok) {
            // Redirect to the webcam interface page or display it in a modal
            window.location.href = '/webcam_interface.html';
        } else {
            console.error('Failed to start attendance');
        }
    } catch (error) {
        console.error('Error:', error);
    }
});
