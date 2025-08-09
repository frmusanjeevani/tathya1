// Handle intro animation redirect messages
window.addEventListener('message', function(event) {
    if (event.data.type === 'redirect' && event.data.page === 'login') {
        // Hide intro and show login
        if (window.parent.Streamlit) {
            window.parent.Streamlit.setComponentValue({
                type: 'redirect_to_login'
            });
        }
        // Fallback: reload page to show login
        setTimeout(() => {
            window.location.reload();
        }, 100);
    }
});