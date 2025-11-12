Docker Compose конфигурация для запуска Keycloak, Dolt и Python приложения.

**Запустите все сервисы:**
   ```bash
   docker-compose -f docker-compose.loocal.yml up --build -d
   ```

## Доступ к сервисам

- **Keycloak HTTPS**: https://localhost:8443 (admin/admin)
- **Dolt**: localhost:3306
- **Python приложение**: http://localhost:8000

## Куда тыкать

Есть Swagger так что все попинать можно по урлу `http://localhost:8000`