// CLEAN VERSION - Replace lines 3780-3849 with this:

async function saveTask(updateId = null) {
    const title = document.getElementById('input-title').value;
    if (!title) return alert(t('title_required') || 'Titel erforderlich');

    const desc = document.getElementById('input-desc').value;
    const subject = selectedSubject;
    const year = selectedDate.getFullYear();
    const month = String(selectedDate.getMonth() + 1).padStart(2, '0');
    const d = String(selectedDate.getDate()).padStart(2, '0');
    const date = `${year}-${month}-${d}`;
    const url = updateId ? `/api/tasks/${updateId}` : '/api/tasks';

    try {
        const formData = new FormData();
        formData.append('title', title);
        formData.append('description', desc);
        formData.append('subject', subject || '');
        formData.append('subject_id', selectedSubjectId || '');
        formData.append('is_shared', isShared ? 'true' : 'false');
        formData.append('due_date', date);
        if (window.currentUser?.class_id) formData.append('class_id', window.currentUser.class_id);

        if (taskFiles.length > 0) {
            for (let i = 0; i < taskFiles.length; i++) {
                formData.append('images', taskFiles[i]);
            }
        }

        if (updateId && imagesToDelete.size > 0) {
            formData.append('deleted_images', Array.from(imagesToDelete).join(','));
        }

        const res = await fetch(url, {
            method: updateId ? 'PUT' : 'POST',
            body: formData
        });
        const data = await res.json();

        if (data.success) {
            imagesToDelete.clear();
            closeSheet();
            // Optionally reload the view after a short delay
            setTimeout(() => {
                if (currentView === 'tasks') renderTasks(currentTaskTab);
                else if (currentView === 'home') renderHome();
            }, 300);
        } else {
            alert(data.message || t('error'));
        }
    } catch (e) {
        console.error('saveTask error:', e);
        alert(t('connection_error') || 'Verbindungsfehler');
    }
}
