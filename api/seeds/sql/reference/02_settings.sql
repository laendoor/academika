INSERT INTO settings (id, key, value, description) VALUES
    (gen_random_uuid(), 'auth.allowed_domains', '["@unq.edu.ar"]', 'Dominios habilitados para login e invitación (lista vacía = cualquier dominio)')
ON CONFLICT (key) DO NOTHING;
