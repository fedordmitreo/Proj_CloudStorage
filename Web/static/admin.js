    // Очистить файлы пользователя
    document.querySelectorAll(".btn-clear").forEach(button => {
      button.addEventListener("click", function () {
        const userId = this.getAttribute("data-userid");
        const userName = this.closest("tr").querySelector("td:nth-child(2)").textContent.trim();

        if (!confirm(`Вы уверены, что хотите удалить ВСЕ файлы пользователя #${userId} (${userName})? Это действие нельзя отменить.`)) {
          return;
        }

        fetch(`/admin/clear_user_files/${userId}`, { method: "POST" })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              alert(data.message);
            } else {
              alert("Ошибка: " + data.message);
            }
          })
          .catch(err => {
            console.error("Ошибка сети:", err);
            alert("Не удалось подключиться к серверу.");
          });
      });
    });

    // Удалить пользователя и его файлы
    document.querySelectorAll(".btn-delete").forEach(button => {
      button.addEventListener("click", function () {
        const userId = this.getAttribute("data-userid");
        const userName = this.closest("tr").querySelector("td:nth-child(2)").textContent.trim();

        if (!confirm(`⚠️ ВНИМАНИЕ: Вы собираетесь УДАЛИТЬ пользователя #${userId} (${userName}) и ВСЕ его файлы.\nЭто действие нельзя отменить.\n\nПродолжить?`)) {
          return;
        }

        fetch(`/admin/delete_user/${userId}`, { method: "POST" })
          .then(response => response.json())
          .then(data => {
            if (data.success) {
              alert(data.message);
              location.reload(); // Обновляем страницу после удаления
            } else {
              alert("Ошибка: " + data.message);
            }
          })
          .catch(err => {
            console.error("Ошибка сети:", err);
            alert("Не удалось подключиться к серверу.");
          });
      });
    });