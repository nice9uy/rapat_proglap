# templatetags/number_filters.py
from django import template

register = template.Library()

@register.filter
def format_rupiah(value):
    try:
        # Pastikan value adalah angka
        num = int(value)
        return f"{num:,}".replace(",", ".")  # 1.000.000
    except (ValueError, TypeError, OverflowError):
        return value