import pandas as pd  # 🔹 Esto faltaba

def clean_string(s):
    """
    Asegura que cualquier string pueda ser codificado a UTF-8.
    Reemplaza caracteres no válidos.
    """
    if isinstance(s, str):
        # Maneja bytes mal decodificados y secuencias UTF-8 truncadas
        return s.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    elif isinstance(s, bytes):
        return s.decode("utf-8", errors="replace")
    return s


def clean_dataframe_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Aplica clean_string a todas las celdas de tipo texto en el DataFrame.
    """
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(clean_string)
    return df