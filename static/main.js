document.addEventListener('DOMContentLoaded', () => {
    // Şifre göster/gizle
    const toggleIcons = document.querySelectorAll('.toggle-password');
    toggleIcons.forEach(icon => {
        icon.addEventListener('click', () => {
            const input = icon.previousElementSibling;
            if (input.type === 'password') {
                input.type = 'text';
                icon.textContent = '🙈';
            } else {
                input.type = 'password';
                icon.textContent = '👁️';
            }
        });
    });

    // Profil modal aç/kapat
    const profileBtn = document.getElementById('profileBtn');
    const profileModal = document.getElementById('profileModal');
    const closeProfile = document.getElementById('closeProfile');
    if (profileBtn && profileModal && closeProfile) {
        profileBtn.onclick = () => {
            profileModal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        };
        closeProfile.onclick = () => {
            profileModal.style.display = 'none';
            document.body.style.overflow = '';
        };
        window.addEventListener('click', function(event) {
            if (event.target === profileModal) {
                profileModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
    }

    // Yeni Sohbet butonuna tıklayınca mesajları temizle
    const newChatBtn = document.querySelector('.new-chat-btn');
    if (newChatBtn) {
        newChatBtn.addEventListener('click', function(e) {
            e.preventDefault();
            const chatBox = document.getElementById('chat-box');
            if (chatBox) chatBox.innerHTML = '';
        });
    }

    // Loading state on form submit
    const forms = document.querySelectorAll('form');
    forms.forEach(form => {
        form.addEventListener('submit', () => {
            const submitBtn = form.querySelector('button[type="submit"]');
            if (submitBtn) {
                submitBtn.disabled = true;
                submitBtn.textContent = 'Yükleniyor...';
            }
        });
    });

    // Kayıt uyarı modalı aç/kapat
    window.showRegisterErrorModal = function() {
        const modal = document.getElementById('registerErrorModal');
        if (modal) {
            modal.style.display = 'block';
            document.body.style.overflow = 'hidden';
        }
    };
    const closeRegisterError = document.getElementById('closeRegisterError');
    const registerErrorModal = document.getElementById('registerErrorModal');
    if (closeRegisterError && registerErrorModal) {
        closeRegisterError.onclick = function() {
            registerErrorModal.style.display = 'none';
            document.body.style.overflow = '';
        };
        window.addEventListener('click', function(event) {
            if (event.target === registerErrorModal) {
                registerErrorModal.style.display = 'none';
                document.body.style.overflow = '';
            }
        });
    }
});
