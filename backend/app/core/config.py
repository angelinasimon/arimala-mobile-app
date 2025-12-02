# app/core/config.py

MEMBERSHIP_GUEST_LIMITS = {
    "FAMILY": 3,      # 1 member + 3 guests = 4 total
    "INDIVIDUAL": 0,
    "STUDENT": 0,
    "COUPLES": 1,     # 1 member + 1 guest
    "PATRON": 0       # or adjust if they get more
}
