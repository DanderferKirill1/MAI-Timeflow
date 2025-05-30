def shorten_teacher_name(full_name: str) -> str:
    """
    Преобразует полное ФИО в сокращенный формат.
    Например: 'Иванова Елена Павловна' -> 'Иванова Е. П.'
    """
    if not full_name:
        return ""
        
    parts = full_name.split()
    if len(parts) == 1:
        return parts[0]
    elif len(parts) == 2:
        return f"{parts[0]} {parts[1][0]}."
    elif len(parts) >= 3:
        return f"{parts[0]} {parts[1][0]}. {parts[2][0]}."
    return full_name 