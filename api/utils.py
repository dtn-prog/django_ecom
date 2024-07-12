def get_username_from_email(email):
    parts = email.split('@')

    if len(parts) < 2:
        return email
    
    username = parts[0]
    domain = parts[1].split('.')[0]
    return f"{username}_{domain}"