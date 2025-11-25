// URL de tu Backend (en local)
const API_URL = "https://ids-proyecto-fc98.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
    
    // 1. PING AL HONEYPOT (Registra visita en silencio)
    fetch(`${API_URL}/stats`)
        .then(res => res.json())
        .then(data => console.log("📡 Conexión segura establecida:", data))
        .catch(err => console.log("⚠️ Backend offline"));

    // 2. FORMULARIO DE CONTACTO
    const form = document.getElementById("contactForm");
    
    if(form) {
        form.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = form.querySelector("button");
            const originalText = btn.innerText;
            
            btn.innerText = "Encriptando...";
            btn.disabled = true;

            const data = {
                nombre: document.getElementById("nombre").value,
                email: document.getElementById("email").value,
                mensaje: document.getElementById("mensaje").value
            };

            try {
                const response = await fetch(`${API_URL}/contact`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });

                if (response.ok) {
                    alert("✅ Mensaje enviado correctamente.");
                    form.reset();
                } else {
                    alert("❌ Error al enviar.");
                }
            } catch (error) {
                console.error(error);
                alert("❌ No se pudo conectar con el servidor.");
            } finally {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        });
    }
});