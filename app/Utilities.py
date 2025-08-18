import pandas as pd  # 🔹 Esto faltaba

def clean_string(s):
    """
    Makes sure that any string can be codified to UTF-8.
    Replaces invalid characters.
    """
    if isinstance(s, str):
        # Handles poorly decoded bytes and truncated UTF-8 sequences
        return s.encode("utf-8", errors="replace").decode("utf-8", errors="replace")
    elif isinstance(s, bytes):
        return s.decode("utf-8", errors="replace")
    return s


def clean_dataframe_strings(df: pd.DataFrame) -> pd.DataFrame:
    """
    Applies clean_string to all text-type cells in the DataFrame.
    """
    for col in df.select_dtypes(include=['object']).columns:
        df[col] = df[col].apply(clean_string)
    return df