-- Admin de desarrollo: email "admin@unq.edu.ar", password "admin". Solo local, el
-- perfil dev nunca corre en prod (make seed-dev no está en el deploy).
-- El email no puede ser "admin" a secas: el login exige un dominio permitido
-- (`auth.allowed_domains`), y el normalizador de settings solo acepta "@dominio" o "*".
INSERT INTO users (id, email, hashed_password, role, is_active)
VALUES (
    gen_random_uuid(),
    'admin@unq.edu.ar',
    '$2b$12$4VfWaMPq/abGnT/iaoqBEuixm7EVaLxA6fnk4rzoWUVd0MPRpkkeS',
    'admin',
    true
)
ON CONFLICT (email) DO NOTHING;
