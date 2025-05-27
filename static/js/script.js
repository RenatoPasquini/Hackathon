// static/js/script.js

document
  .getElementById("eventWizardForm")
  .addEventListener("submit", async function (event) {
    event.preventDefault(); // Impede o envio tradicional do formulário

    const themeSuggestionsOutput = document.getElementById(
      "themeSuggestionsOutput"
    );
    const loadingIndicator = document.getElementById("loadingIndicator");
    const errorMessageDisplay = document.getElementById("errorMessage");
    const submitButton = document.getElementById("submitButton");
    const loadingScreen = document.getElementById("loadingScreen");

    // Recolher dados do formulário
    const formData = {
      eventName: document.getElementById("eventName").value,
      eventType: document.getElementById("eventType").value,
      guestCount: document.getElementById("guestCount").value,
      budget: document.getElementById("budget").value,
      eventDate: document.getElementById("eventDate").value,
      eventObjective: document.getElementById("eventObjective").value,
    };

    loadingScreen.style.display = "block"; // Show loading screen

    try {
      const response = await fetch("/api/compile_responses", {
        method: "POST",
        headers: {
          "Content-Type": "application/json",
        },
        body: JSON.stringify(formData),
      });

      loadingScreen.style.display = "none"; // Hide loading screen
      const result = await response.json();

      if (response.ok) {
        console.log(result);
        const loadingScreen = document.getElementById("loadingScreen");
        console.log(result.compiled_response);
        console.log(themeSuggestionsOutput.innerHTML);
        console.log(themeSuggestionsOutput);
        themeSuggestionsOutput.innerHTML = marked.parse(result.compiled_response);
        loadingScreen.style.display = "none";
        resultsSection.style.display = "block";
      } else {
        errorMessageDisplay.textContent = `Erro ao obter sugestões: ${
          result.erro || response.statusText
        }`;
        errorMessageDisplay.style.display = "block";
        console.error("Erro do servidor:", result);
      }
    } catch (error) {
      loadingScreen.style.display = "none"; // Hide loading screen
      if (error.message.includes("Failed to fetch")) {
        errorMessageDisplay.textContent =
          "O servidor de API não está disponível. Por favor, tente novamente mais tarde.";
      } else {
        errorMessageDisplay.textContent = `Erro de comunicação com o servidor: ${error.message}. Verifique a consola para mais detalhes.`;
      }
      errorMessageDisplay.style.display = "block";
      console.error("Erro na chamada fetch:", error);
    } finally {
      submitButton.disabled = false; // Reabilitar botão
    }
  });
