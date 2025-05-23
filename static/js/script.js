// static/js/script.js

document.getElementById('eventWizardForm').addEventListener('submit', async function(event) {
    event.preventDefault(); // Impede o envio tradicional do formulário

    const resultsSection = document.getElementById('resultsSection');
    const themeSuggestionsOutput = document.getElementById('themeSuggestionsOutput');
    const loadingIndicator = document.getElementById('loadingIndicator');
    const errorMessageDisplay = document.getElementById('errorMessage');
    const submitButton = document.getElementById('submitButton');

    // Mostrar indicador de carregamento e limpar resultados anteriores
    resultsSection.style.display = 'block';
    loadingIndicator.style.display = 'block';
    themeSuggestionsOutput.textContent = '';
    errorMessageDisplay.style.display = 'none';
    errorMessageDisplay.textContent = '';
    submitButton.disabled = true; // Desabilitar botão durante o pedido

    // Recolher dados do formulário
    const formData = {
        eventName: document.getElementById('eventName').value,
        eventType: document.getElementById('eventType').value,
        guestCount: document.getElementById('guestCount').value,
        budget: document.getElementById('budget').value,
        eventDate: document.getElementById('eventDate').value,
        eventObjective: document.getElementById('eventObjective').value,
        themeIdea: document.getElementById('themeIdea').value
    };

    try {
        const response = await fetch('/api/suggest_themes', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            },
            body: JSON.stringify(formData),
        });

        loadingIndicator.style.display = 'none'; // Esconder indicador
        const result = await response.json();

        if (response.ok) {
            if (result.sugestoes_temas) {
                themeSuggestionsOutput.textContent = result.sugestoes_temas;
            } else {
                themeSuggestionsOutput.textContent = "Resposta recebida, mas sem sugestões de tema explícitas.";
                console.warn("Resposta do servidor:", result);
            }
        } else {
            errorMessageDisplay.textContent = `Erro ao obter sugestões: ${result.erro || response.statusText}`;
            errorMessageDisplay.style.display = 'block';
            console.error("Erro do servidor:", result);
        }
    } catch (error) {
        loadingIndicator.style.display = 'none'; // Esconder indicador
        errorMessageDisplay.textContent = `Erro de comunicação com o servidor: ${error.message}. Verifique a consola para mais detalhes.`;
        errorMessageDisplay.style.display = 'block';
        console.error('Erro na chamada fetch:', error);
    } finally {
        submitButton.disabled = false; // Reabilitar botão
    }
}); 