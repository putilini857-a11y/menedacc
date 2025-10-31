/*
  # Создание таблицы resources для менеджера ресурсов

  1. Новые таблицы
    - `resources`
      - `id` (uuid, primary key) - уникальный идентификатор ресурса
      - `url` (text) - URL ресурса (например, https://example.com)
      - `login` (text) - логин для доступа к ресурсу
      - `password` (text) - пароль для доступа к ресурсу
      - `is_active` (boolean) - активен ли ресурс (true/false)
      - `created_at` (timestamptz) - дата и время создания ресурса

  2. Безопасность
    - Включить RLS для таблицы `resources`
    - Добавить политику для чтения всех ресурсов (public доступ)
    - Добавить политику для создания ресурсов (public доступ)
    - Добавить политику для обновления ресурсов (public доступ)
    - Добавить политику для удаления ресурсов (public доступ)

  Примечание: В данной реализации используется public доступ без аутентификации
*/

-- Создаем таблицу resources
CREATE TABLE IF NOT EXISTS resources (
  id uuid PRIMARY KEY DEFAULT gen_random_uuid(),
  url text NOT NULL,
  login text NOT NULL,
  password text NOT NULL,
  is_active boolean DEFAULT true,
  created_at timestamptz DEFAULT now()
);

-- Включаем RLS
ALTER TABLE resources ENABLE ROW LEVEL SECURITY;

-- Политики для публичного доступа (без аутентификации)
CREATE POLICY "Anyone can view resources"
  ON resources
  FOR SELECT
  USING (true);

CREATE POLICY "Anyone can create resources"
  ON resources
  FOR INSERT
  WITH CHECK (true);

CREATE POLICY "Anyone can update resources"
  ON resources
  FOR UPDATE
  USING (true)
  WITH CHECK (true);

CREATE POLICY "Anyone can delete resources"
  ON resources
  FOR DELETE
  USING (true);