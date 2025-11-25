// URL de tu Backend (en local)
const API_URL = "https://ids-proyecto-fc98.onrender.com";

document.addEventListener("DOMContentLoaded", () => {
    console.log("🛡️ Sentinel System: Inicializado");

    // 1. FUNCIONALIDAD IDS (Predicción de Ataques)
    const vectorBoxes = document.querySelectorAll('.vector-box');

    vectorBoxes.forEach(box => {
        // Quitamos el evento onclick antiguo del HTML para manejarlo aquí
        box.removeAttribute('onclick'); 
        
        box.addEventListener('click', async () => {
            // Efecto visual de "Procesando"
            box.style.borderColor = "#facc15"; // Amarillo
            document.body.style.cursor = "wait";

            // Obtener los datos del vector
            const vectorString = box.getAttribute('data-vector');
            const features = vectorString.split(',').map(num => parseFloat(num.trim()));

            console.log("📤 Enviando tráfico al IDS:", features);

            try {
                // Enviar al Backend Python
                const response = await fetch(`${API_URL}/predict`, {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({ features: features })
                });

                const result = await response.json();

                // Mostrar Resultado
                if (result.is_threat) {
                    alert(`🚨 ALERTA DE SEGURIDAD 🚨\n\nTipo: ${result.prediction}\nConfianza: ${result.confidence}\n\nEl sistema ha bloqueado este tráfico.`);
                    box.style.borderColor = "#ef4444"; // Rojo
                } else {
                    alert(`✅ TRÁFICO SEGURO\n\nClasificación: ${result.prediction}\nConfianza: ${result.confidence}`);
                    box.style.borderColor = "#22d3ee"; // Cyan (Normal)
                }

            } catch (error) {
                console.error("Error IDS:", error);
                alert("❌ Error de conexión con el Servidor IDS.\n(El servidor gratuito de Render puede estar dormido, intenta de nuevo en 30 seg).");
                box.style.borderColor = "#334155"; // Volver a gris
            } finally {
                document.body.style.cursor = "default";
            }
        });
    });

    // 2. FORMULARIO DE CONTACTO (Código existente)
    const contactForm = document.getElementById("contactForm");
    if (contactForm) {
        contactForm.addEventListener("submit", async (e) => {
            e.preventDefault();
            const btn = contactForm.querySelector("button");
            const originalText = btn.innerText;
            btn.innerText = "Encriptando...";
            btn.disabled = true;

            const data = {
                nombre: document.getElementById("nombre").value,
                email: document.getElementById("email").value,
                mensaje: document.getElementById("mensaje").value
            };

            try {
                await fetch(`${API_URL}/contact`, {
                    method: "POST",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify(data)
                });
                alert("✅ Mensaje enviado correctamente.");
                contactForm.reset();
            } catch (error) {
                alert("❌ Error al enviar mensaje.");
            } finally {
                btn.innerText = originalText;
                btn.disabled = false;
            }
        });
    }
});