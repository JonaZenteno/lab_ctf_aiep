import os

# Flags de los 5 retos, configurables vía variables de entorno para poder
# rotarlas entre eventos sin tocar código.
FLAG_1 = os.environ.get("LAB_FLAG", "AIEP{sqli_bypass_admin_sin_clave_2026}")
FLAG_2 = os.environ.get("LAB_FLAG_2", "AIEP{sqli_union_extrae_el_hash_2026}")
FLAG_3 = os.environ.get("LAB_FLAG_3", "AIEP{csrf_sin_proteccion_2026}")
FLAG_4 = os.environ.get("LAB_FLAG_4", "AIEP{sqli_union_columnas_a_ciegas_2026}")
FLAG_5 = os.environ.get("LAB_FLAG_5", "AIEP{sqli_blind_boolean_caracter_a_caracter_2026}")
