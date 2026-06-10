INSERT INTO lkp_estado_academico (key, label) VALUES
    ('alumno_regular', 'Alumno Regular'),
    ('no_regular',     'No Regular')
ON CONFLICT DO NOTHING;

INSERT INTO lkp_estado_cursada (key, code, label) VALUES
    ('inscripto',            'I',  'Inscripto'),
    ('regular',              'R',  'Regular'),
    ('promocionado',         'P',  'Promocionado'),
    ('aprobado',             'A',  'Aprobado'),
    ('desaprobado',          'D',  'Desaprobado'),
    ('pendiente_aprobacion', 'PA', 'Pendiente de Aprobación')
ON CONFLICT DO NOTHING;

INSERT INTO lkp_tipo_cursada (key, label) VALUES
    ('regular', 'Cursada Regular'),
    ('libre',   'Libre')
ON CONFLICT DO NOTHING;

INSERT INTO lkp_user_roles (key, label) VALUES
    ('admin',    'Administrador'),
    ('director', 'Dirección de Carrera'),
    ('docente',  'Docente')
ON CONFLICT DO NOTHING;

INSERT INTO lkp_nivel_carrera (key, label) VALUES
    ('grado',    'Grado'),
    ('pregrado', 'Pregrado')
ON CONFLICT DO NOTHING;

INSERT INTO lkp_nucleo_carrera (key, label) VALUES
    ('basico',      'Núcleo Básico'),
    ('avanzado',    'Núcleo Avanzado'),
    ('orientacion', 'Núcleo de Orientación')
ON CONFLICT DO NOTHING;
