function populateSubjects() {
    const baseUrl = window.location.origin;
    const endpoint = `${baseUrl}/student/subjects/`;
    fetch(endpoint)
        .then(response => {
            if (!response.ok) {
                throw new Error('Failed to fetch subjects');
            }
            return response.json();
        })
        .then(data => {
            const subjectDropdown = document.getElementById('studentSubject');
            subjectDropdown.innerHTML = '<option value="">Select a subject</option>';
            data.forEach(subject => {
                const option = document.createElement('option');
                option.value = subject.id;
                option.textContent = subject.name;
                subjectDropdown.appendChild(option);
            });
        })
        .catch(error => console.error('Error:', error));
}

function reloadTableData() {
    const baseUrl = window.location.origin;
    const url = `${baseUrl}/student/home/`;
    window.location.href = url;
}

window.onclick = function(event) {
    if (event.target == document.getElementById('studentModal')) {
        document.getElementById('studentModal').style.display = 'none';
    }
};

function closeModal() {
    document.getElementById('studentModal').style.display = 'none';

    const fields = ['studentName', 'studentSubject', 'studentMarks'];
    fields.forEach(id => {
        const field = document.getElementById(id);
        field.value = '';
        field.classList.remove('invalid');
    });
}

function fetchStudentData(id) {
    const baseUrl = window.location.origin;
    const url = `${baseUrl}/student/get-student-detail/?id=${id}`;

    // Fetch student data from the server
    fetch(url)
        .then(response => response.json())
        .then(data => {
            if (data && data.other_message.status === 'success') {
                // Populate fields with the existing data
                document.getElementById('studentName').value = data.message.name || '';
                document.getElementById('studentMarks').value = data.message.marks || '';
            } else {
                console.error('Failed to fetch student data');
            }
        })
        .catch(error => {
            console.error('Error fetching student data:', error);
        });
}

function openModal(mode, id = '', name = '', subject = '', marks = '') {
    populateSubjects();
    // Display the modal
    document.getElementById('studentModal').style.display = 'block';

    // Populate fields if editing
    document.getElementById('studentName').value = name || '';
    document.getElementById('studentSubject').value = subject || '';
    document.getElementById('studentMarks').value = marks || '';

    // Set the modal title
    document.getElementById('modalTitle').innerText = mode === 'edit' ? 'Edit Student' : 'Add Student';
    
    // If editing, fetch student details if ID is available
    if (mode === 'edit' && id) {
        fetchStudentData(id)
    } else {
        // Populate fields if not editing (add mode)
        document.getElementById('studentName').value = name || '';
        document.getElementById('studentSubject').value = subject || '';
        document.getElementById('studentMarks').value = marks || '';
    };

    // Form submission logic with validation
    document.getElementById('studentForm').onsubmit = function(event) {
        event.preventDefault();

        // Reset previous validation styles
        [studentName, studentSubject, studentMarks].forEach(field => field.classList.remove('invalid'));

        // Validation checks
        let isValid = true;
        if (!studentName.value.trim()) {
            studentName.classList.add('invalid');
            isValid = false;
        }

        if (!studentSubject.value.trim()) {
            studentSubject.classList.add('invalid');
            document.getElementById('subjectError').style.display = 'block';
            isValid = false;
        }

        if (!studentMarks.value.trim()) {
            studentMarks.classList.add('invalid');
            isValid = false;
        }

        if (isValid) {
            submitForm(mode, id);
        }
    };
}

// Utility function to get a cookie value by name
function getCookie(name) {
    const cookies = document.cookie.split(';');
    for (let i = 0; i < cookies.length; i++) {
        const cookie = cookies[i].trim();
        if (cookie.startsWith(name + '=')) {
            return cookie.substring(name.length + 1);
        }
    }
    return null;
}

async function submitForm(mode, id) {
    const name = document.getElementById('studentName').value;
    const subject = document.getElementById('studentSubject').value;
    const marks = document.getElementById('studentMarks').value;

    let data = {
        name: name,
        subject: subject,
        marks: marks
    };

    const baseUrl = window.location.origin;
    let url = null;
    if (mode === 'add') {
        url = `${baseUrl}/student/add-student/`;
    } else if (mode === 'edit') {
        data.id = id;
        url = `${baseUrl}/student/edit-student/`;
    }

    try {
        const csrfToken = getCookie('csrftoken');
        const response = await fetch(url, {
            method: 'POST',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            },
            body: JSON.stringify(data)
        });
        if (response.ok) {
            const responseData = await response.json();
            console.log('Form submitted successfully:', responseData);
        } else {
            console.error('Failed to submit form:', response.status);
            throw new Error('Failed to submit form');
        }
    } catch (error) {
        console.error('Error submitting form:', error);
    }

    closeModal();
    reloadTableData();
}

async function deleteStudent(studentId) {
    const baseUrl = window.location.origin;
    const url = `${baseUrl}/student/delete-student/${studentId}/`;

    try {
        const csrfToken = getCookie('csrftoken');
        const response = await fetch(url, {
            method: 'DELETE',
            headers: {
                'X-CSRFToken': csrfToken,
                'Content-Type': 'application/json'
            }
        });

        if (response.ok) {
            const data = await response.json();
            console.log('Student deleted successfully:', data);
        } else {
            console.error('Failed to delete the student record:', response.status);
            throw new Error('Failed to submit request');
        }
    } catch (error) {
        console.error('Error submitting request:', error);
    }
    reloadTableData();
}

function logout() {
    const csrftoken = getCookie('csrftoken');
    const baseUrl = window.location.origin;
    const url = `${baseUrl}/student/logout/`;

    fetch(url, {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
            'X-CSRFToken': csrftoken, // Include the CSRF token
        },
    })
    .then(response => {
        if (response.ok) {
            return response.json();
        }
        throw new Error('Logout failed.');
    })
    .then(data => {
        console.log('Logged out:', data);
        window.location.href = `${baseUrl}/student/login/`; // Redirect to login
    })
    .catch(error => console.error('Error:', error));
}
