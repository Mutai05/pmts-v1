from django import template

register = template.Library()

@register.simple_tag
def get_rating_classes(rating_value):
    """Returns a dictionary of CSS classes based on the rating value."""
    rating_str = str(rating_value).lower()
    classes = {
        'focus_ring': 'focus:ring-primary', # Default
        'text': 'text-gray-700' # Default
    }
    if rating_str == '5':
        classes['focus_ring'] = 'focus:ring-green-500'
        classes['text'] = 'text-green-700'
    elif rating_str == '4':
        classes['focus_ring'] = 'focus:ring-blue-500'
        classes['text'] = 'text-blue-700'
    elif rating_str == '3':
        classes['focus_ring'] = 'focus:ring-yellow-500'
        classes['text'] = 'text-yellow-700'
    elif rating_str == '2':
        classes['focus_ring'] = 'focus:ring-orange-500'
        classes['text'] = 'text-orange-700'
    elif rating_str == '1':
        classes['focus_ring'] = 'focus:ring-red-500'
        classes['text'] = 'text-red-700'
    return classes
